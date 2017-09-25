import ast

class PrettyPrinter2Arduino(ast.NodeVisitor):
    def __init__(self):
       self.s_code = ""
       self.arr = ""
       self.indent = 0
       
    def visit_Module(self, node):
        self.generic_visit(node)
        
        print (self.s_code)
        
    def visit_FunctionDef(self, node):
        self.declFunction(node.name)
        self.s_code += "("
        self.generic_visit(node.args)
        self.s_code += ") {\n"
        self.indent += 1
        for stmt in node.body:
            self.s_code += "    " * self.indent
            self.generic_visit(ast.Expr(stmt))
            self.s_code += "\n"
        self.indent -= 1
        self.s_code += ("    " * self.indent) + "}\n"
        
    def visit_For(self, node):
        self.s_code += "for ("
        initNode = ""
        testNode = ""
        compNode = ""
        # python에서 작성하는 arduino 코드의 for문은 for __ in range(_) or range(_, _) or range(_, _, _)
        # ToDo : range(_, _, _)의 경우, 세번째 인자에 따라서 Add, Sub를 나눌 필요있음
        if type(node.iter).__name__ == 'Call':
            if len(node.iter.args) == 1:
                initNode = ast.Assign(targets = [node.target], value = ast.Num(n=0))
                testNode = ast.Compare(left = node.target, ops = [ast.Lt()], comparators = [ast.Num(n=node.iter.args[1])])
                compNode = ast.Assign(targets = [node.target], value = ast.BinOp(left = node.target, op = ast.Add(), right = ast.Num(n=1)))
            elif len(node.iter.args) == 2:
                initNode = ast.Assign(targets = [node.target], value = node.iter.args[0])
                testNode = ast.Compare(left = node.target, ops = [ast.Lt()], comparators = [node.iter.args[1]])
                compNode = ast.Assign(targets = [node.target], value = ast.BinOp(left = node.target, op = ast.Add(), right = ast.Num(n=1)))
            elif len(node.iter.args) == 3:
                initNode = ast.Assign(targets = [node.target], value = node.iter.args[0])
                testNode = ast.Compare(left = node.target, ops = [ast.Lt()], comparators = [node.iter.args[1]])
                compNode = ast.Assign(targets = [node.target], value = ast.BinOp(left = node.target, op = ast.Add(), right = node.iter.args[2]))
            self.generic_visit(ast.Expr(value = initNode))
            self.s_code += " "
            self.generic_visit(ast.Expr(value = testNode))
            self.s_code += "; "
            self.generic_visit(ast.Expr(value = compNode))
            self.s_code = self.s_code[:len(self.s_code) - 1]
        
        self.s_code += ") {\n"
        self.indent += 1
        
        for stmt in node.body:
            self.s_code += "    " * self.indent
            self.generic_visit(ast.Expr(value = stmt))
            self.s_code += "\n"
        
        self.indent -= 1
        self.s_code += "    " * self.indent + "}"
        
    def visit_If(self, node):
        self.s_code += "if ("
        self.generic_visit(ast.Expr(value = node.test))
        self.s_code += ") {\n"
        self.indent += 1
        
        for stmt in node.body:
            self.s_code += "    " * self.indent
            self.generic_visit(ast.Expr(value = stmt))
            self.s_code += "\n"
        
        self.indent -= 1
        self.s_code += "    " * self.indent        
        self.s_code += "}"
        
    def visit_Compare(self, node):
        self.generic_visit(ast.Expr(value = node.left))
        
        for op in node.ops:
            if type(op).__name__ == "Eq":
                self.s_code += " == "
            elif type(op).__name__ == "NotEq":
                self.s_code += " != "
            elif type(op).__name__ == "Lt":
                self.s_code += " < "
            elif type(op).__name__ == "LtE":
                self.s_code += " <= "
            elif type(op).__name__ == "Gt":
                self.s_code += " > "
            elif type(op).__name__ == "GtE":
                self.s_code += " >= "
            # is, is not, in, not in are not supported
#            elif type(op).__name__ == "Is":
#                pass
#            elif type(op).__name__ == "IsNot":
#                pass
#            elif type(op).__name__ == "In":
#                pass
#            elif type(op).__name__ == "NotIn":
#                pass
            else:
                print ("Invalid Compare Operator", op)
                break
            
            for comparator in node.comparators:
                self.generic_visit(ast.Expr(comparator))
        
    def visit_Name(self, node):
        if node.id.__contains__('_int') or node.id.__contains__('_void') or node.id.__contains__('_byte') or node.id.__contains__('_char'):
            sid = node.id.split('_')
            sid.remove('')
            
            for rid in sid[1:]:
                self.s_code += rid
        else:
            self.s_code += node.id
        self.generic_visit(node)
        
    def visit_NameConstant(self, node):
        if node.value == True:
            self.s_code += "true"
        elif node.value == False:
            self.s_code += "false"
            
        self.generic_visit(node)
        
    def visit_List(self, node):
        self.s_code += "{"
        for elem in node.elts:
            self.generic_visit(ast.Expr(value = elem))
            if elem != node.elts[len(node.elts) - 1]:
                self.s_code += ", "
        self.s_code += "}"
            
    def visit_Expr(self, node):
        self.generic_visit(node)
        self.s_code += ";"
    
    def visit_Call(self, node):
        self.generic_visit(ast.Expr(value = node.func))
        self.s_code += "("
        for arg in node.args:
            self.generic_visit(ast.Expr(value = arg))
            if arg != node.args[len(node.args) - 1]:
                self.s_code += ", "
        self.s_code += ")"
            
    def visit_Attribute(self, node):
        self.generic_visit(ast.Expr(value = node.value))
        self.s_code += "." + node.attr        
    
    def visit_Tuple(self, node):
        self.generic_visit(node)
        
    def visit_Dict(self, node):
        self.generic_visit(node)
        
    def visit_Num(self, node):
        self.s_code += str(node.n)
        
        self.generic_visit(node)
        
    def visit_Str(self, node):
        self.s_code += "\"" + node.s + "\""
        
        self.generic_visit(node)
        
    def visit_Assign(self, node):
        for target in node.targets:
            if type(target).__name__ == 'Name':
                tid = target.id
                if tid == '_include':
                    self.s_code += "#include <" + node.value.s + ">\n"
                elif tid == '_sensor_decl':
                    self.declSensor(node.value)
                    self.s_code += ";\n"
                # ToDo : Arduino double, float, short, unsigned, ...
                elif tid.__contains__('_int') or tid.__contains__('byte') or tid.__contains__('_char') or tid.__contains__('_boolean'):
                    self.declVariable(tid)
                    self.s_code += " = "
                    self.generic_visit(ast.Expr(value = node.value))
                    self.s_code += ";\n"
                else:
                    self.s_code += tid + " = "
                    self.generic_visit(ast.Expr(value = node.value))
                    self.s_code += ";"
            else:
                self.generic_visit(ast.Expr(value = target))
                self.s_code += " = "
                self.generic_visit(ast.Expr(value = node.value))
                self.s_code += ";"
    
    def visit_Subscript(self, node):
        self.generic_visit(ast.Expr(value = node.value))
        self.s_code += "["
        self.generic_visit(node.slice)
        self.s_code += "]"
        
    def visit_BoolOp(self, node):
        sop = ""
        if type(node.op).__name__ == "And":
            sop = " && "
        elif type(node.op).__name__ == "Or":
            sop = " || "
            
        for val in node.values:
            self.generic_visit(ast.Expr(value = val))
            if val != node.values[len(node.values) - 1]:
                self.s_code += sop

    def visit_BinOp(self, node):
        self.generic_visit(ast.Expr(value = node.left))
        
        sop = node.op

        if type(sop).__name__ == "Add":
            self.s_code += " + "
        elif type(sop).__name__ == "Sub":
            self.s_code += " - "
        elif type(sop).__name__ == "Mult":
            self.s_code += " * "
        elif type(sop).__name__ == "Div":
            self.s_code += " / "
        elif type(sop).__name__ == "Mod":
            self.s_code += " % "
        elif type(sop).__name__ == "MatMul":
            self.s_code += " % "
        elif type(sop).__name__ == "Pow":
            self.s_code += " % "
        elif type(sop).__name__ == "LShift":
            self.s_code += " % "
        elif type(sop).__name__ == "RShift":
            self.s_code += " % "
        elif type(sop).__name__ == "BitOr":
            self.s_code += " | "
        elif type(sop).__name__ == "BirAnd":
            self.s_code += " & "
        elif type(sop).__name__ == "BitXor":
            self.s_code += " % "
        elif type(sop).__name__ == "FloorDiv":
            self.s_code += " / "
        else:
            print ("Invalid operator", sop)
            
        self.generic_visit(ast.Expr(value = node.right))
                
    def declFunction(self, name):
        if name.__contains__('_int') or name.__contains__('_void') or name.__contains__('_byte') or name.__contains__('_char'):
            sid = name.split('_')
            sid.remove('')
            self.s_code += sid[0] + " "
            
            for rid in sid[1:]:
                self.s_code += rid
                
    def declVariable(self, tid):
        if tid.__contains__('_int'):
            self.s_code += "int "
            split_tid = tid[4:]
            tid = self.hasArrString(split_tid)
        elif tid.__contains__('_byte'):
            self.s_code += "byte "
            split_tid = tid[5:]
            tid = self.hasArrString(split_tid)
        elif tid.__contains__('_char'):
            self.s_code += "char "
            split_tid = tid[5:]
            tid = self.hasArrString(split_tid)
        elif tid.__contains__('_boolean'):
            self.s_code += "boolean "
            split_tid = tid[8:]
            tid = self.hasArrString(split_tid)
            
    def declSensor(self, node):
        if type(node).__name__ == "Name":
            sid = node.id.split('_')
            sid.remove('')
            for name in sid:
                if name == sid[len(sid) - 1]:
                    self.s_code += " "
                self.s_code += name
            
        elif type(node).__name__ == "Call":
            sid = node.func.id.split('_')
            sid.remove('')
            for name in sid:
                if name == sid[len(sid) - 1]:
                    self.s_code += " " + name
                elif name == sid[len(sid) -2]:
                    self.s_code += name
                else:
                    self.s_code += name + "_"
        else:
            print ("Invalid Sensor Declaration", node)
        
    
    def hasArrString(self, sid):
        if sid.__contains__('arr') == True:
            sid = sid[3:]
            self.arr = "[" + sid[0:1] + "]"
            self.hasArrString(sid[1:])
        else:
            self.s_code += sid[1:] + self.arr
            self.arr = ""
        
        return sid[1:]
    
    def getStrCode(self):
        return self.s_code
            
       
directory = input("Insert work directory(Absolutely Path) : ")
filename = input("Insert file name(include extension name) : ")
filePath = directory + "\\" + filename

f = open(filePath, 'r+')
content = f.read()
f.close()

pretty = PrettyPrinter2Arduino()
t = ast.parse(content)

pretty.visit(t)
prettyCode = pretty.getStrCode()

f = open(directory + "\\" + "Arduino.ino", "w+")
f.write(prettyCode)
f.close()