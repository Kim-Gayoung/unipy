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
        needCommu = False
        
        for callee in calleeArr:
            if classArr.get(self.className) == 'Arduino' and (callee[1] == self.className or callee[2] == self.className):
                newBody.insert(0, ast.parse("_include = 'ArduinoJson.h'"))
                needCommu = True
                break
        
        newNode.body = newBody
        num = 0
        
        for stmt in newNode.body:
            if type(stmt).__name__ == 'FunctionDef' and classArr.get(self.className) == 'Arduino' and needCommu:
                annAst = ast.AnnAssign(target = ast.Name(id = 'jsonBuffer', ctx = ast.Load()), annotation = ast.Name(id = 'DynamicJsonBuffer', ctx = ast.Load()), value = None, simple = 1)
                newNode.body.insert(num, annAst)
#                newNode.body.insert(num, ast.parse('_DynamicJsonBuffer_jsonBuffer'))
#                newNode.body.insert(num + 1, ast.Expr(value = ast.Name(id = '_JsonObject&_jsonObject', ctx = ast.Load())))
                needCommu = False
                break
            else:
                num = num + 1
            
        num = 0
        
        if classArr.get(self.className) == 'Arduino':
            loopFunction = self.getLoop()
            
            for stmt in newNode.body:
                if type(stmt).__name__ == 'FunctionDef' and stmt.name == 'setup':                        
                    newNode.body.insert(num + 1, loopFunction)
                    break
                else:
                    num = num + 1
        
        num = 0
        
        for stmt in newNode.body:
            if type(stmt).__name__ == 'FunctionDef':
                if classArr.get(self.className) == 'Arduino':
                    num = num + 1
                    if stmt.name == 'loop':
                        newNode.body.insert(num, newFunction)
                        break
                else:
                    newNode.body.insert(num, newFunction)
                    break
            else:
                num = num + 1
        
        for impStmt in replaceAST.importList:
            newNode.body.insert(0, ast.Import(names = [ast.alias(name = impStmt, asname = None)]))

        replaceAST.importList = []
        newNode = ast.ClassDef(bases = node.bases, body = newNode, decorator_list = node.decorator_list, name = node.name)
               
        if self.dispatch_flag == True and classArr.get(self.className) != 'Arduino':
            newNode.body.body.append(ast.parse('_firstCall = dispatch()'))
#            dispatchValue = ast.Call(args = [], func = ast.Name(id='dispatch', ctx=ast.Load()), keywords = [])
#            dispatchCall = ast.Assign(targets = [ast.Name(id='_firstCall', ctx = ast.Store())], value = dispatchValue)
#            newNode.body.body.append(dispatchCall)
        
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
    
    def getLoop(self):
        loopFunction = ast.FunctionDef()
        loopFunction.body = []
        isExist = False
        
        if classArr.get(self.className) == 'Arduino':
            for tup in remoteProcList:
                if tup[0] == self.className and tup[1] != 'setup':
                    for callTup in calleeArr:
                        if callTup[1] == self.className and callTup[0] != tup[1]:
                            loopFunction.body.append(ast.Call(args = [], func = ast.Name(id=tup[1], ctx=ast.Load()), keywords = []))
                        elif callTup[1] == self.className and callTup[0] == tup[1]:
                            isExist = True
                    
            if isExist == True:
                loopFunction.body.append(ast.Expr(value = ast.Call(args=[], func = ast.Name(id='dispatch', ctx=ast.Load()), keywords=[])))
            
        if loopFunction.body == []:
            return []
        
        loopFunction.args = []
        loopFunction.decorator_list = []
        loopFunction.name = 'loop'
        loopFunction.returns = ast.NameConstant(value = None)
        
        return loopFunction
            
    
    def getDispatch(self):
        newFunction = ast.FunctionDef()
        newFunction.body = []
        caller = ""
        callee = ""
        
        
        newIf = ast.If()
        for elem in calleeArr:
            if elem[1] == self.className:
                callee = elem[1]
                caller = elem[2]
                funNum = -1
                for tup in remoteProcList:
                    if tup[0] == self.className and tup[1] == elem[0]:
                        funNum = tup[2]
                        break
                newIf.test = ast.Compare(left = ast.Name(id = "funid"), ops = [ast.Eq()], comparators = [ast.Num(n = funNum)])
                newIf.body = [ast.Expr(value = ast.Call(args = [], func = ast.Name(id=elem[0], ctx=ast.Load()), keywords = []))]
                newIf.orelse = []
                newFunction.body.append(newIf)
        
        if newFunction.body == []:
            return []
        
        commNode = self.getCommuNode(callee, caller, newIf)
        n = 0
        
        newFunction.body.clear()
        for comm in commNode:
            newFunction.body.insert(n, comm)
            n = n + 1
        
        if classArr.get(self.className) == 'Arduino':
            newFunction.name = 'dispatch'
            newFunction.returns = ast.NameConstant(value = None)
        else:
            newFunction.name = 'dispatch'
        
        newFunction.args =[]
        newFunction.decorator_list = []
        self.dispatch_flag = True
        
        return newFunction
    
    def getCommuNode(self, callee, caller, ifNode):
        calleeClass = classArr.get(callee)
        callerClass = classArr.get(caller)
        comm = commuTable.get(callerClass).get(calleeClass)
                
        newCommu = []

        if comm == 'Serial':
            if calleeClass == 'Arduino':
                newCommu.append(ast.parse('str: String = ""'))
                bodySource = "if Serial.available() > 0:\n" + "\tstr = Serial.readStringUntil(char('\\n'))\n"
                newCommu.append(ast.parse("funid: int = 0"))
                newCommu.append(ast.parse(bodySource))
                ifBodyAst = []
                valueAst = ast.Call(args = [ast.Name(id = "str", ctx = ast.Load())], func = ast.Attribute(attr = "parseObject", ctx = ast.Load(), value = ast.Name(id = "jsonBuffer", ctx = ast.Load())), keywords = [], kwargs = None, starargs = None)
#                ifBodyAst.append(ast.Assign(targets = [ast.Name(id="JsonObject&_jsonObject", ctx = ast.Load())], value = valueAst))
                ifBodyAst.append(ast.AnnAssign(target = [ast.Name(id="jsonObject", ctx = ast.Load())], annotation = ast.Name(id = "JsonObject", ctx = ast.Load()), value = valueAst, simple = 1))
                ifBodyAst.append(ast.parse("funid = jsonObject['_funid']"))
                newCommu.append(ast.If(test = ast.Compare(comparators = [ast.Str(s = "")], left = ast.Name(id = "str", ctx = ast.Load()), ops = [ast.NotEq()]), body = ifBodyAst, orelse = []))
                newCommu.append(ifNode)
                newCommu.append(ast.parse('funid = -1'))
                
                return newCommu
            
            elif calleeClass == 'Raspberry':
                newCommu.append(ast.parse('global _ser, _jsonData'))
                newCommu.append(ast.parse('_ser = serial.Serial("/dev/ttyACM0", 9600)'))
                whileBody = []
                whileBody.append(ast.parse('jsonStr = _ser.readline().strip().decode("utf-8")'))
                whileBody.append(ast.parse('if jsonStr == "":\n\tcontinue'))
                whileBody.append(ast.parse('_jsonData = json.loads(jsonStr)'))
                whileBody.append(ast.parse('funid = _jsonData["_funid"]'))
                whileBody.append(ifNode)
                whileBody.append(ast.parse('funid = -1'))
                whileNode = ast.While(test = ast.Name(id = 'True', ctx = ast.Load()), body = whileBody, orelse = [])
                newCommu.append(whileNode)
                
                return newCommu
                
        elif comm == 'Socket':
            if calleeClass == 'Raspberry':
                newCommu.append(ast.parse('global _conn'))
                newCommu.append(ast.parse('s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)'))
                newCommu.append(ast.parse('s.bind((HOST, PORT))'))
                newCommu.append(ast.parse('s.listen(1)'))
                whileBody = []
                whileBody.append(ast.parse('_conn, addr = s.accept()'))
                whileBody.append(ast.parse('global _recieveJsonData'))
                whileBody.append(ast.parse('_recieveData = ""'))
                whileBody.append(ast.parse('_cnt = 0'))
                
                source = "while True:\n"
                source += "\ttmp = _conn.recv(1).decode('utf-8')\n" + "\t_recieveData += tmp\n"
                source += "\tif tmp == '{':\n" + "\t\t_cnt = _cnt + 1\n" + "\telif tmp == '}':\n" + "\t\t_cnt = _cnt - 1\n"
                source += "\tif _cnt == 0:\n" + "\t\tbreak\n"
                whileBody.append(ast.parse(source))
                
                whileBody.append(ast.parse('if _recieveData == "":\n\tcontinue\n'))
                whileBody.append(ast.parse('_recieveJsonData = json.loads(_recieveData)'))
                whileBody.append(ast.parse('funid = _recieveJsonData["_funid"]'))
                whileBody.append(ifNode)
                whileBody.append(ast.parse('funid = -1'))
                whileNode = ast.While(test = ast.Name(id='True', ctx = ast.Load()), body = whileBody, orelse = [])
                newCommu.append(whileNode)
                
                return newCommu
            
            elif calleeClass == 'Mobile':
                newCommu.append(ast.parse('global _conn'))
                newCommu.append(ast.parse(trySource))
                newCommu.append(ast.parse('s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)'))
                newCommu.append(ast.parse('s.bind((HOST, PORT))'))
                newCommu.append(ast.parse('s.listen(1)'))
                
                whileBody = []
                whileBody.append(ast.parse('_conn, addr = s.accept()'))
                
                source = "while True:\n"
                source += "\ttmp = _conn.recv(1).decode('utf-8')\n" + "\t_recieveData += tmp\n"
                source += "\tif tmp == '{':\n" + "\t\t_cnt = _cnt + 1\n" + "\telif tmp == '}':\n" + "\t\t_cnt = _cnt - 1\n"
                source += "\tif _cnt == 0:\n" + "\t\tbreak\n"
                whileBody.append(ast.parse(source))
                whileBody.append(ifNode)
                whileBody.append(ast.parse('funid = -1'))
                
                whileNode = ast.While(test = ast.Name(id = 'True', ctx = ast.Load()), body = whileBody, orelse = [])
                newCommu.append(whileNode)
                
                return newCommu
    
        elif comm == 'http':                
            if calleeClass == 'Cloud':
                newCommu.append(ast.parse('funid = int(sys.argv[1])'))
                newCommu.append(ifNode)
                
                return newCommu
                
            elif calleeClass == 'Mobile':
                newCommu.append(ifNode)
                return newCommu
            
        elif comm == 'Bluetooth':
            newCommu.append(ifNode)
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
        # jsonObject = jsonBuffer.createObject()
        # jsonObject["args1"] = args1
        # jsonObject["args2"] = args2
        # ...
        # jsonObject["argsn"] = argsn
        # jsonObject.printTo(Serial)
        
        smethval = CommLib.unparseExpr(methval)
        newAsts = []
        
        newAsts.append(ast.parse('sendFunid: JsonObject = jsonBuffer.createObject()'))
        newAsts.append(ast.parse('sendFunid["_funid"] = ' + smethval))
        newAsts.append(ast.parse('sendFunid.printTo(Serial)'))
        
        newAsts.append(ast.parse('jsonObject: JsonObject = jsonBuffer.createObject()'))
        num = 0
        
        for arg in node.value.args:
            sarg = CommLib.unparseExpr(arg)
            newAsts.append(ast.parse('jsonObject["args' + str(num) + '"] = ' + sarg))
            num  = num + 1
            
        newAsts.append(ast.parse('jsonObject.printTo(Serial)'))
        newAsts.append(ast.parse('jsonBuffer.clear()'))

        return newAsts

    # 아두이노에서 라즈베리 파이에서 받은 값을 읽는 시리얼 통신
    def recieveBySerialAtArduino(node):
        # servoControl(self, methval, data1, data2, ..., datan)
        
        # String recieveData = ""
        # while Serial.available() > 0:
        #   recieveData = Serial.readString()
        
        # JsonObject& jsonObject = jsonBuffer.createObject(recieveData)
        
        # data1 = jsonObject["args1"]
        # data2 = jsonObject["args2"]
        # ...
        # datan = jsonObject["argsn"]
        
        newAsts = []
        
        newAsts.append(ast.parse('recieveData: String = Serial.readStringUntil(char("\\n"))'))
                
        ifSource = "if recieveData != '':\n" + "\trecieveJson: JsonObject = jsonBuffer.parseObject(recieveData)\n"
        
        num = 0
        for arg in node.args.args:
            sarg = CommLib.unparseExpr(arg)
            argAst = ast.parse(sarg)
            newAsts.append(ast.parse(sarg))
            ifSource += "\ttmp" + str(num) + ": " + argAst.body[0].annotation.id + " = recieveJson['args" + str(num) + "']\n"
            ifSource += "\t" + argAst.body[0].target.id + " = tmp" + str(num) + "\n"
            num = num + 1

        newAsts.append(ast.parse(ifSource))
        newAsts.append(ast.parse('jsonBuffer.clear()'))

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
        
        if 'json' not in replaceAST.importList:
            replaceAST.importList.append('json')
        
        newAsts.append(ast.parse('_recieveData = _ser.readline().strip().decode("utf-8")'))
        newAsts.append(ast.parse('global _recieveJsonData'))
        
        ifSource = 'if _recieveData != "":\n' + '\t_recieveJsonData = json.loads(_recieveData)\n'
        ifSource += 'else:\n' + '\t_recieveJsonData = ""\n'
        newAsts.append(ast.parse(ifSource))
        
        num = 0
        ifSource = 'if _recieveJsonData != "":\n'
        for arg in node.args.args:
            sarg = CommLib.unparseExpr(arg)
            ifSource += '\t' + sarg + ' = _recieveJsonData["args' + str(num) + '"]\n'
            num = num + 1
            
        newAsts.append(ast.parse(ifSource))
        
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
        if 'json' not in replaceAST.importList:
            replaceAST.importList.append('json')
            
        newAsts.append(ast.parse('global ser'))
        newAsts.append(ast.parse('ser = serial.Serial("/dev/ttyACM0", 9600)'))

        smethval = CommLib.unparseExpr(methval)
        
        newAsts.append(ast.parse('_sendData = {}'))
        newAsts.append(ast.parse('_sendData["_funid"] = ' + smethval))
        newAsts.append(ast.parse('_sendFunid = json.dumps(_sendData)'))
        newAsts.append(ast.parse('ser.write(_sendFunid.encode("utf-8"))'))
        newAsts.append(ast.parse('ser.write("\\n".encode("utf-8"))'))
        newAsts.append(ast.parse('_sendData.clear()'))

        num = 0
        
        for arg in node.value.args:
            sarg = CommLib.unparseExpr(arg)
            newAsts.append(ast.parse('_sendData["args' + str(num) + '"] = ' + sarg))
            num = num + 1
        
        newAsts.append(ast.parse('_jsonData = json.dumps(_sendData)'))
        newAsts.append(ast.parse('ser.write(_jsonData.encode("utf-8"))'))
        newAsts.append(ast.parse('ser.write("\\n".encode("utf-8"))'))
        newAsts.append(ast.parse('ser.close()'))
        
        return newAsts
    
    def sendBySocketAtRaspberry(node, methval):        
        
        newAsts = []
        
        if 'socket' not in replaceAST.importList:
            replaceAST.importList.append('socket')
        if 'json' not in replaceAST.importList:
            replaceAST.importList.append('json')
        
        smethval = CommLib.unparseExpr(methval)
        
        newAsts.append(ast.parse('_sendData = {}'))
        newAsts.append(ast.parse('_sendData["_funid"] = ' + smethval))
        newAsts.append(ast.parse('_sendFunid = json.dumps(_sendData)'))
        newAsts.append(ast.parse('conn.sendall(_sendFunid.encode("utf-8"))'))
        newAsts.append(ast.parse('_sendData.clear()'))
        
        num = 0
        
        for arg in node.value.args:
            sarg = CommLib.unparseExpr(arg)
            newAsts.append(ast.parse('_sendData["args' + str(num) + '"] = ' + sarg))
            num = num + 1
        
        newAsts.append(ast.parse('_jsonData = json.dumps(_sendData)'))
        newAsts.append(ast.parse('conn.sendall(_sendData.encode("utf-8"))'))
        newAsts.append(ast.parse('conn.close()'))
            
        return newAsts
    
    def recieveBySocketAtRaspberry(node):
        # sendtest(data)
                
        # _jsonData = json.loads(_recieveData)
        
        # args1 = _recieveData["args1"]
        # args2 = _recieveData["args2"]
        # ...
        # argsn = _recieveData["argsn"]
        
        newAsts = []
        
        if 'socket' not in replaceAST.importList:
            replaceAST.importList.append('socket')
        if 'json' not in replaceAST.importList:
            replaceAST.importList.append('json')
        
        
        newAsts.append(ast.parse('_recieveData = ""'))
        newAsts.append(ast.parse('_cnt = 0'))
        
        source = "while True:\n"
        source += "\ttmp = _conn.recv(1).decode('utf-8')\n" + "\t_recieveData += tmp\n"
        source += "\tif tmp == '{':\n" + "\t\t_cnt = _cnt + 1\n" + "\telif tmp == '}':\n" + "\t\t_cnt = _cnt - 1\n"
        source += "\tif _cnt == 0:\n" + "\t\tbreak\n"
        newAsts.append(ast.parse(source))
        newAsts.append(ast.parse('global _jsonData'))
        
        ifSource = 'if _recieveData != "":\n' + '\t_jsonData = json.loads(_recieveData)\n'
        ifSource += 'else:\n' + '\t_jsonData = ""\n'
        newAsts.append(ast.parse(ifSource))
            
        num = 0
        
        ifSource = 'if _jsonData != "":\n'
        for arg in node.args.args:
            sarg = CommLib.unparseExpr(arg)
            ifSource += '\t' + sarg + ' = _jsonData["args' + str(num) + '"]\n'
            num = num + 1
        
        newAsts.append(ast.parse(ifSource))
        
        return newAsts
        
    def sendBySocketAtMobile(node, methval):
        
        newAsts = []
        
        if 'socket' not in replaceAST.importList:
            replaceAST.importList.append('socket')
        if 'json' not in replaceAST.importList:
            replaceAST.importList.append('json')
        
        newAsts.append(ast.parse('_writer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)'))

        smethval = CommLib.unparseExpr(methval)
        newAsts.append(ast.parse('_sendData = {}'))
        
        sparm = CommLib.unparseExpr(node.value.args[0])
        newAsts.append(ast.parse('_writer_tup = ' + sparm))
        newAsts.append(ast.parse('_writer.connect(_writer_tup)'))
        newAsts.append(ast.parse('_sendData["_funid"] = ' + smethval))
        newAsts.append(ast.parse('_sendFunid = json.dumps(_sendData)'))
        newAsts.append(ast.parse('_writer.sendall(_sendFunid.encode("utf-8"))'))
        newAsts.append(ast.parse('_sendData.clear()'))

        num = 0
        
        for arg in node.value.args[1:]:
            sarg = CommLib.unparseExpr(arg)
            newAsts.append(ast.parse('_sendData["args' + str(num) + '"] = ' + sarg))
            num = num + 1
        
        newAsts.append(ast.parse('_jsonData = json.dumps(_sendData)'))
        newAsts.append(ast.parse('_writer.sendall(_jsonData.encode("utf-8"))'))
        
        return newAsts
    
    def sendByHttpAtMobile(node, methval, targets):
        # getDoorlist()
        
        #door_arr = MyCloud.doorlist()
        #while((line = buffer.readLine()) != null)
        
        newAsts = []
        num = 0
        ipAddress = ""
        
        smethval = CommLib.unparseExpr(methval)
        newAsts.append(ast.parse("_field_dict = {}"))
        newAsts.append(ast.parse('_field_dict["_funid"] = ' + smethval))
        
        if 'urllib3' not in replaceAST.importList:
            replaceAST.importList.append('urllib3')
        if 'json' not in replaceAST.importList:
            replaceAST.importList.append('json')
        
        for arg in node.value.args:
            sarg = CommLib.unparseExpr(arg)
            if arg == node.value.args[0]:
                ipAddress = sarg
            else:
                newAsts.append(ast.parse('_field_dict["args' + str(num) + '"] = ' + sarg))
                num += 1
            
        newAsts.append(ast.parse("req = urllib3.PoolManager()"))
        
        for target in targets:
            starget = CommLib.unparseExpr(target)
            targetAst = ast.parse('_' + starget + ' = req.request("POST", ' + ipAddress + ', fields = _field_dict).data.decode("utf-8")')
            newAsts.append(targetAst)
            jsonAst = ast.parse(starget + ' = json.loads(_' + starget + ')')
            newAsts.append(jsonAst)
        
        return newAsts
    
    def sendByHttpAtRaspberry(node, methval, targets):
        
        newAsts = []
        num = 0
        ipAddress = ""
        
        smethval = CommLib.unparseExpr(methval)
        newAsts.append(ast.parse("_field_dict = {}"))
        newAsts.append(ast.parse("_field_dict['_funid'] = " + smethval))
        
        if 'urllib3' not in replaceAST.importList:
            replaceAST.importList.append('urllib3')
            
        for arg in node.value.args:
            sarg = CommLib.unparseExpr(arg)
            if arg == node.value.args[0]:
                ipAddress = sarg
            else:
                newAsts.append(ast.parse("_field_dict['args" + str(num) +"'] = " + sarg))
                num += 1
                
        newAsts.append(ast.parse("req = urllib3.PoolManager()"))
        
        if targets != []:    
            for target in targets:
                starget = CommLib.unparseExpr(target)
                newAsts.append(ast.parse(starget + ' = req.request("POST", ' + ipAddress + ', fields = _field_dict)'))
        else:
            newAsts.append(ast.parse("req.request('POST', " + ipAddress + ", fields = _field_dict)"))
        
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
