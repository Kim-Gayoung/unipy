import ast
import astunparse
import io
import sys
import os

commuTable = {
                'Arduino' : {'Arduino':None, 'Raspberry':'Serial', 'Cloud':'http', 'Mobile':'Bluetooth'},
                'Raspberry' : {'Arduino':'Serial', 'Raspberry':None, 'Cloud':'http', 'Mobile':'Socket'},
                'Cloud' : {'Arduino':'http', 'Raspberry':'http', 'Cloud':None, 'Mobile':'http'},
                'Mobile' : {'Arduino':'Bluetooth', 'Raspberry':'Socket', 'Cloud':'http', 'Mobile':None}
             }

debug = False

def codegen(node):
    astunparse.Unparser(node, sys.stdout)
    
class distFile(ast.NodeVisitor):
    def __init__(self, filePath):
        self.className = ""
        self.isDef = False
        self.filePath = filePath
        
    def generic_visit(self, node):
        if type(node).__name__ == 'ClassDef':
            self.isDef = True
            self.className = node.name
        else:
            self.isDef = False
        
        # 클래스 선언이 시작되면 클래스 별 저장
        if self.isDef == True:
            fileName = self.filePath
            if not os.path.exists(self.filePath):
                os.mkdir(self.filePath)
            fileName += "/" + self.className
            fileName += ".py"
            f = open(fileName, 'w+t')  
            sio = io.StringIO()
            astunparse.Unparser(node.body, sio)
            f.write(sio.getvalue())
            f.close()
            
        ast.NodeVisitor.generic_visit(self, node)

class replaceAST(ast.NodeTransformer):
    importList = []
    
    def __init__(self):
        self.className = ""

    def visit_FunctionDef(self, node):        
        for callee in calleeArr:
            name = ""
            n = ""
            if node.name.__contains__('_'):
                name = node.name.split('_')
                if name.__contains__(''):
                    name.remove('')
                for s in name[1:]:
                    n += s
            else:
                n = node.name
                
            if callee[0] == n and callee[1] == self.className:
                insertBody = CommLib.commRecvLib(self.className, callee[2], node)
                node.args.args.clear()
                break        
        else:
            insertBody = []
            
        newNode = self.generic_visit(node)
        
        num = 0
        
        newBody = self.visit_body(newNode.body)
        
        for body in insertBody:
            newBody.insert(num, body)
            num = num + 1
        
        newNode.body = newBody
        
        return newNode
                        
    def visit_ClassDef(self, node):
        self.className = node.name
        self.dispatch_flag = False
        newFunction = self.getDispatch()
        newNode = self.generic_visit(node)
        
        newBody = self.visit_body(node.body)
        
        newNode.body = newBody
        num = 0
        
        for stmt in newNode.body:
            if type(stmt).__name__ == 'FunctionDef':
                newNode.body.insert(num, newFunction)
                break
            else:
                num = num + 1
        
        for impStmt in replaceAST.importList:
            newNode.body.insert(0, ast.Import(names = [ast.alias(name = impStmt, asname = None)]))

        replaceAST.importList = []
        newNode = ast.ClassDef(bases = node.bases, body = newNode, decorator_list = node.decorator_list, name = node.name)
               
        if self.dispatch_flag == True:
            dispatchValue = ast.Call(args = [], func = ast.Name(id='dispatch', ctx=ast.Load()), keywords = [])
            dispatchCall = ast.Assign(targets = [ast.Name(id='_firstCall', ctx = ast.Store())], value = dispatchValue)
            newNode.body.body.append(dispatchCall)
        
        return newNode        
    
    def visit_While(self, node):
        newNode = self.generic_visit(node)
        
        newBody = self.visit_body(newNode.body)
        newNode.body = newBody
        
        return newNode
    
    def visit_If(self, node):
        newNode = self.generic_visit(node)
        
        newBody = self.visit_body(newNode.body)
        newNode.body.clear()

        for stmt in newBody:
            newNode.body.append(stmt)
        
        return newNode

    def visit_For(self, node):
        newNode = self.generic_visit(node)
        
        newBody = self.visit_body(newNode.body)
        newNode.body = newBody
        
        return newNode

    def visit_body(self, body):
        newBody = []
        for stmt in body:
            if debug:
                print (type(stmt))

            if type(stmt).__name__ == 'Assign' or type(stmt).__name__ == 'Expr':

                if type(stmt).__name__ == 'Assign':
                    targets = stmt.targets
                    
                    if type(targets[0]).__name__ == 'Name' and targets[0].id == '_import_list':
                        if type(stmt.value).__name__ == 'List' or type(stmt.value).__name__ == 'Tuple':
                            for elem in stmt.value.elts:
                                if type(elem).__name__ == 'Str' and elem.s not in replaceAST.importList:
                                    replaceAST.importList.append(elem.s)
                        elif type(stmt.value).__name__ == 'Str':
                            if stmt.value.s not in replaceAST.importList:
                                replaceAST.importList.append(stmt.value.s)
                        continue
                else:
                    targets = []
                        
                if type(stmt.value).__name__ == 'Call' and type(stmt.value.func).__name__ == 'Attribute' and type(stmt.value.func.value).__name__ == 'Name':
                    clz = stmt.value.func.value.id
                    meth = stmt.value.func.attr

                    newStmts = CommLib.commSendLib(self.className, clz, targets, meth, stmt)
                    
                    for newStmt in newStmts:
                        newBody.append(newStmt)
                        
                else:
                    newBody.append(stmt)

            else:
                newBody.append(stmt)

        return newBody
    
    def getDispatch(self):
        newFunction = ast.FunctionDef()
        newFunction.body = []
        caller = ""
        callee = ""
        
        for elem in calleeArr:
            newIf = ast.If()
            if elem[1] == self.className:
                callee = elem[1]
                caller = elem[2]
                funNum = -1
                for tup in remoteProcList:
                    if tup[0] == self.className and tup[1] == elem[0]:
                        funNum = tup[2]
                        break
                newIf.test = ast.Compare(left = ast.Name(id = "funid"), ops = [ast.Eq()], comparators = [ast.Num(n = funNum)])
                newIf.body = ast.Expr(value = ast.Call(args = [], func = ast.Name(id=elem[0], ctx=ast.Load()), keywords = []))
                newIf.orelse = []
                newFunction.body.append(newIf)
        
        if newFunction.body == []:
            return []
        
        commNode = self.getCommuNode(callee, caller)
        n = 0
        
        for comm in commNode:
            newFunction.body.insert(n, comm)
            n = n + 1
        
        if classArr.get(self.className) == 'Arduino':
            newFunction.name = '_void_dispatch'
        else:
            newFunction.name = 'dispatch'
            
        newFunction.args =[]
        newFunction.decorator_list = []
        self.dispatch_flag = True
        
        return newFunction
    
    def getCommuNode(self, callee, caller):
        calleeClass = classArr.get(callee)
        callerClass = classArr.get(caller)
        comm = commuTable.get(callerClass).get(calleeClass)
                
        newCommu = []

        if comm == 'Serial':
            if calleeClass == 'Arduino':
                newCommu.append(ast.parse('_char_funid = ""'))
                newCommu.append(ast.If(test = ast.parse('Serial.available() > 0').body[0].value, body = ast.parse('funid = Serial.read()'), orelse = []))
                
                return newCommu
            
            elif calleeClass == 'Raspberry':
                newCommu.append(ast.parse('ser = serial.Serial("/dev/ttyACM0")'))
                newCommu.append(ast.parse('funid = ser.read(1)'))
                
                return newCommu
                
        elif comm == 'Socket':
            if calleeClass == 'Raspberry':
                newCommu.append(ast.parse('s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)'))
                newCommu.append(ast.parse('s.bind((HOST, PORT))'))
                newCommu.append(ast.parse('s.listen(10)'))
                
                source = 'while 1:\n' + '\tconn, addr = s.accept()\n' + '\tfunid = conn.recv(1024).decode("utf-8")\n' + '\tif funid != None:\n' + '\t\tbreak'
                newCommu.append(ast.parse(source))
                
                return newCommu
            
            elif calleeClass == 'Mobile':
                newCommu.append(ast.parse('s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)'))
                newCommu.append(ast.parse('conn, addr = s.accept()'))
                newCommu.append(ast.parse('funid = conn.recv(1024)'))
                
                return newCommu
    
        elif comm == 'http':                
            if calleeClass == 'Cloud':
                newCommu.append(ast.parse('funid = int(sys.argv[1])'))
                
                return newCommu
                
            elif calleeClass == 'Mobile':
                return newCommu
            
        elif comm == 'Bluetooth':
            return newCommu
        else:
            print ("Not Supported Communication way")
        
        return newCommu
    
class CommLib():    
    def commSendLib(fromClz, toClz, targets, meth, node):
        try:
            locToClz = classArr[toClz]
            locFromClz = classArr[fromClz]
        except:
            #print ("commSendLib : Exception")
            return [node]
        
        methval = ast.Num(n = -1)
        
        for remoteTup in remoteProcList:
            if remoteTup[0] == toClz and remoteTup[1] == meth:
                methval = ast.Num(n = remoteTup[2])
                break

        if locFromClz == 'Arduino' and locToClz == 'Raspberry':
            newNodes = CommLib.sendBySerialAtArduino(node, methval)
                                      
        elif locFromClz == 'Raspberry' and locToClz == 'Arduino':
            newNodes = CommLib.sendBySerialAtRaspberry(node, methval)
            
        elif locFromClz == 'Raspberry' and locToClz == 'Cloud':
            newNodes = CommLib.sendByHttpAtRaspberry(node, methval, targets)
        
        elif locFromClz == 'Raspberry' and locToClz == 'Mobile':
            newNodes = CommLib.sendBySocketAtRaspberry(node, methval, targets)
        
        elif locFromClz == 'Mobile' and locToClz == 'Cloud':
            newNodes = CommLib.sendByHttpAtMobile(node, methval, targets)
        
        elif locFromClz == 'Mobile' and locToClz == 'Raspberry':
            newNodes = CommLib.sendBySocketAtMobile(node, methval)
        
        else:
            print ("Invalid location")
            return [node]
        
        return newNodes
    
    def commRecvLib(toClz, fromClz, node):
        try:
            locToClz = classArr[toClz]
            locFromClz = classArr[fromClz]
            
        except:
#            print ("commRecvLib : Exception")
            return []
        
        if locFromClz == 'Arduino' and locToClz == 'Raspberry':
            newArgs = CommLib.recieveBySerialAtRaspberry(node)
        
        elif locFromClz == 'Raspberry' and locToClz == 'Arduino':
            newArgs = CommLib.recieveBySerialAtArduino(node)
        
        elif locFromClz == 'Raspberry' and locToClz == 'Cloud':
            newArgs = CommLib.recieveByHttpAtCloud(node)
        
        elif locFromClz == 'Raspberry' and locToClz == 'Mobile':
            newArgs = CommLib.recieveBySocketAtMobile(node)
        
        elif locFromClz == 'Mobile' and locToClz == 'Cloud':
            newArgs = CommLib.recieveByHttpAtCloud(node)
        
        elif locFromClz == 'Mobile' and locToClz == 'Raspberry':
            newArgs = CommLib.recieveBySocketAtRaspberry(node)
        
        else:
            print ("Invalid location")
            return [node]
            
        return newArgs
    
    #아두이노에서 라즈베리 파이로 보내는 시리얼 통신            
    def sendBySerialAtArduino(node, methval): 
        # Serial.println(node.value.args)
        smethval = CommLib.unparseExpr(methval)
        newAsts = []
        newAsts.append(ast.parse('Serial.println(' + smethval + ')'))
        
        for arg in node.value.args:
            sarg = CommLib.unparseExpr(arg)
            newAsts.append(ast.parse('Serial.println(' + sarg + ')'))

        return newAsts

    # 아두이노에서 라즈베리 파이에서 받은 값을 읽는 시리얼 통신
    def recieveBySerialAtArduino(node):
        # servoControl(self, methval, data1, data2, ..., datan)
        
        # data1 = Serial.read()
        # data2 = Serial.read()
        # ...
        # datan = Serial.read()
        
        newAsts = []
        
        for arg in node.args.args:
            sarg = CommLib.unparseExpr(arg)
            newAsts.append(ast.parse(sarg + ' = Serial.read()').body[0])

        return newAsts
    
    #라즈베리파이에서 아두이노의 값을 읽어오는 시리얼 통신
    def recieveBySerialAtRaspberry(node): 
        # requesttest(self, val1, val2, ..., valn)
        #
        #import serial
        #import requests
        #ser=serial.Serial('/dev/ttyACM0', 9600) -> option으로 device, baud rate
        #{"Serial":[dev:'/dev/ttyACM0', baudrate:9600]}
        
        #val1 = ser.read(1)
        #val2 = ser.read(1)
        #...
        #valn = ser.read(1)

        newAsts = []
        
        if 'serial' not in replaceAST.importList:
            replaceAST.importList.append('serial')
                    
        for arg in node.args.args:
            sarg = CommLib.unparseExpr(arg)
            newAsts.append(ast.parse(sarg + ' = ser.read(1)'))

        return newAsts
    
    def sendBySerialAtRaspberry(node, methval):
        #sendtest(self, methval, val1, val2, ..., valn):
        #ser=serial.Serial('/dev/ttyACM0', 9600); -> option으로 device, baud rate
        #{"Serial":[dev:'/dev/ttyACM0', baudrate:9600]}

        #ser.write(metval)
        #ser.write(val1)
        #ser.write(val2)
        # ...
        #ser.write(valn)
        newAsts = []
        
        if 'serial' not in replaceAST.importList:
            replaceAST.importList.append('serial')
            
        newAsts.append(ast.parse('ser = serial.Serial("/dev/ttyACM0")'))

        smethval = CommLib.unparseExpr(methval)
        newAsts.append(ast.parse('ser.write(' + smethval + ')'))

        for arg in node.value.args:
            sarg = CommLib.unparseExpr(arg)
            newAsts.append(ast.parse('ser.write(' + sarg + ')'))

        return newAsts
    
    def sendBySocketAtRaspberry(node, methval):        
        
        newAsts = []
        
        if 'socket' not in replaceAST.importList:
            replaceAST.importList.append('socket')
        
        for arg in node.value.args:
            sarg = CommLib.unparseExpr(arg)
            newAsts.append(ast.parse('conn.sendall(' + sarg + ')'))
            
        return newAsts
    
    def recieveBySocketAtRaspberry(node):
        #sendtest(data)
        
        #conn, addr = s.accept()
        #data = conn.recv(1024)
        
        newAsts = []
        
        if 'socket' not in replaceAST.importList:
            replaceAST.importList.append('socket')
        
        for arg in node.args.args:
            sarg = CommLib.unparseExpr(arg)
            newAsts.append(ast.parse(sarg + ' = conn.recv(1024)'))
        
        return newAsts
        
    def sendBySocketAtMobile(node, methval):
        
        newAsts = []
        
        if 'socket' not in replaceAST.importList:
            replaceAST.importList.append('socket')
        
        newAsts.append(ast.parse('_writer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)'))
        smethval = CommLib.unparseExpr(methval)
        
        for arg in node.value.args:
            sarg = CommLib.unparseExpr(arg)
            if arg == node.value.args[0]:
                newAsts.append(ast.parse('_writer_tup = ' + sarg))
                newAsts.append(ast.parse('_writer.connect(_writer_tup)'))
                newAsts.append(ast.parse('_writer.send(str(' + smethval + ').encode("utf-8"))'))
            else:
                newAsts.append(ast.parse('_writer.sendall(' + sarg + '.encode("utf-8"))'))
        
        return newAsts
    
    def sendByHttpAtMobile(node, methval, targets):
        # getDoorlist()
        
        #door_arr = MyCloud.doorlist()
        #while((line = buffer.readLine()) != null)
        
        newAsts = []
        num = 0
        ipAddress = ""
        datas = {}
        # fields에 
        
        smethval = CommLib.unparseExpr(methval)
        newAsts.append(ast.parse("_field_dict = {}"))
        newAsts.append(ast.parse('_field_dict["_funid"] = ' + smethval))
        
        if 'urllib3' not in replaceAST.importList:
            replaceAST.importList.append('urllib3')
        
        for arg in node.value.args:
            sarg = CommLib.unparseExpr(arg)
            if arg == node.value.args[0]:
                ipAddress = sarg
            else:
                newAsts.append(ast.parse('_field_dict["MOBILE_CLOUD_ARGS_' + str(num) + '"] = ' + sarg))
                num += 1
            
        newAsts.append(ast.parse("req = urllib3.PoolManager()"))
        
        for target in targets:
            starget = CommLib.unparseExpr(target)
            targetAst = ast.parse('_' + starget + ' = req.request("POST", ' + ipAddress + ', fields = _field_dict).data.decode("utf-8")')
            newAsts.append(targetAst)
            # replcae ' -> "
            jsonAst = ast.parse(starget + ' = json.loads(_' + starget + ')')
            newAsts.append(jsonAst)
        
        return newAsts
    
    def sendByHttpAtRaspberry(node, methval, targets):
        
        newAsts = []
        datas = {}
        num = 0
        ipAddress = ""
        
        smethval = CommLib.unparseExpr(methval)
        datas['_funid'] = smethval
        
        if 'urllib3' not in replaceAST.importList:
            replaceAST.importList.append('urllib3')
        
        for arg in node.value.args:
            sarg = CommLib.unparseExpr(arg)
            if arg == node.value.args[0]:
                ipAddress = sarg
            else:
                datas['GATEWAY_CLOUD_ARGS_' + str(num)] = sarg
                num += 1
                
        newAsts.append(ast.parse("req = urllib3.PoolManager()"))
        
        if targets != []:    
            for target in targets:
                starget = CommLib.unparseExpr(target)
                newAsts.append(ast.parse(starget + ' = req.request("POST", ' + ipAddress + ', data=' + str(datas) +')'))
        else:
            newAsts.append(ast.parse("req.request('POST', '" + ipAddress + "', data = " + str(datas) + ")"))
        
        return newAsts
    
    def recieveByHttpAtMobile(node):
        return []
    
    def sendByHttpAtCloud(node, methval):
        return []
    
    def recieveByHttpAtCloud(node):
        newAsts = []
        num = 2
        
        if 'sys' not in replaceAST.importList:
            replaceAST.importList.append('sys')
                
        if node.args.args != []:
            for arg in node.args.args:
                sarg = CommLib.unparseExpr(arg)
                newAsts.append(ast.parse(sarg + ' = sys.argv[' + str(num) + ']'))
                num = num + 1
                
        return newAsts

    def unparseStmt(tree):
        sio = io.StringIO()
        astunparse.Unparser(tree, sio)
        
        s = sio.getvalue().split("\n")[1]
                                      
        return s
    
    def unparseExpr(tree):
        if type(tree).__name__ == 'Str':
            return tree.s
        else:
            sio = io.StringIO()
            astunparse.Unparser(tree, sio)
            
            s = sio.getvalue().split("\n")[0]
                                          
            return s
    
class TableGenVisitor(ast.NodeVisitor):    
    def __init__(self):
        self.isDef = False
        self.className = ""
        self.num = 0
        global classArr
        global methodArr
        global remoteProcList
        classArr = {}
        methodArr = {}
        remoteProcList = []
        
        
    def generic_visit(self, node):
        if type(node).__name__ == 'ClassDef':
            self.isDef = True
            self.className = node.name

            # 상속 받는 방법에 따라 통신 방법을 달리 해줌
            if node.bases[0].id == 'Arduino' or node.bases[0].id == 'Raspberry' or node.bases[0].id == 'Cloud' or node.bases[0].id == 'Mobile':
                classArr[self.className] = node.bases[0].id

        # class 별 method list로 구성
        if type(node).__name__ == 'FunctionDef':
            name = node.name
            if name.__contains__('_'):
                name = node.name.split('_')
                if name.__contains__(''):
                    name.remove('')
                sname = ""
                for n in name[1:]:
                    sname += n                
                methodArr[sname] = self.className
                remoteProcList.append((self.className, sname, self.num))
                self.num = self.num + 1
            else:
                methodArr[node.name] = self.className
                remoteProcList.append((self.className, node.name, self.num))
                self.num = self.num + 1
            
        ast.NodeVisitor.generic_visit(self, node)
        
class FindCalleeCaller(ast.NodeVisitor):
    def __init__(self):
        self.className = ""
        global calleeArr
        calleeArr = []
        
    def visit_ClassDef(self, node):
        self.className = node.name
        
        self.generic_visit(node)
        
    def visit_Call(self, node):
        if type(node.func).__name__ == 'Attribute':
            callee = methodArr.get(node.func.attr)
            
            if callee is not None and not(calleeArr.__contains__((node.func.attr, callee, self.className))):
                calleeArr.append((node.func.attr, callee, self.className))
#            else:;
#                if type(node.func.value).__name__ == 'Name':
#                    cmd_last = "help('" + node.func.value.id + "')"
#                    stream = subprocess.check_output(["python", "-c", cmd_last], universal_newlines = True)
#                    isModule = stream.__contains__("Help on module ") or stream.__contains__("Help on package ")
#                    if isModule and not(importArr.__contains__(node.func.value.id)):
#                        importArr.append(node.func.value.id)
                

print ("1: case1(doorstate), 2: case2(control), 3: case3(dbcontent), 4: the other case")
selection = input("Enter the number : ")

firstCase = "case1_input/unipyprogram_doorstate.txt"
firstOutput = "case1_input/output"
secondCase = "case2_input/unipyprogram_control.txt"
secondOutput = "case2_input/output"
thirdCase = "case3_input/unipyprogram_dbcontent.txt"
thirdOutput = "case3_input/output"

fullPath = ""
fileName = ""
directory = ""
filename = ""

if selection == '1':
    fullPath = firstCase
    fileName = firstOutput
elif selection == '2':
    fullPath = secondCase
    fileName = secondOutput
elif selection == '3':
    fullPath = thirdCase
    fileName = thirdOutput
elif selection == '4':
    directory = input("Enter the working directory : ")
    filename = input("Enter the filename : ")
    fullPath = directory + "/" + filename
    fileName = directory + "/output"

# 파이썬의 파일을 읽어와서 문자열로 변환
f = open(fullPath, 'r+')
content = f.read()

# 문자열을 파싱 -> 방문 기록
x = TableGenVisitor()
t = ast.parse(content)

x.visit(t)

f = FindCalleeCaller()
f.visit(t)

replace_ast = replaceAST()
newT = replace_ast.visit(t)

#codegen(newT)

fileGen = distFile(fileName)
fileGen.visit(newT)
