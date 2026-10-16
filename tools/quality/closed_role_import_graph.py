"""Execute the actual frozen input import loop against all frozen Python bytes."""
import ast


def check_graph(preflight,files,pins,required_classes):
    def require(value):
        if value is not True:raise ValueError('actual frozen role import graph refused')
    require(type(preflight)is str and type(files)is dict and type(pins)is dict and type(required_classes)is tuple)
    require(set(files)=={n for n in pins if n.endswith('.py')}and bool(files))
    tree=ast.parse(preflight)
    tables=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='STANDARD'for t in n.targets)]
    loops=[n for n in ast.walk(tree)if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='node']
    require(len(tables)==len(loops)==1)
    table=tables[0].value;require(isinstance(table,ast.Call)and isinstance(table.func,ast.Name)and table.func.id=='frozenset'and len(table.args)==1 and not table.keywords)
    members=ast.literal_eval(table.args[0]);require(type(members)is tuple and bool(members)and all(type(v)is str for v in members)and len(members)==len(set(members)))
    standard=frozenset(members)
    class Reader:
        def __init__(self,value):self.value=value
        def read_bytes(self):return self.value
    code=compile(ast.Module(body=loops,type_ignores=[]),'<actual frozen input loop>','exec')
    for name,raw in files.items():
        require(type(raw)is bytes)
        ns={'ast':ast,'p':Reader(raw),'pins':pins,'STANDARD':standard,'require':require};exec(code,ns)
    require(all(type(n)is str and n in pins for n in required_classes))
    return {'actualExit':0,'pythonFiles':len(files),'physicalFiles':len(pins),'standardImports':sorted(standard),'requiredClasses':list(required_classes),'allActualImportLoopsPassed':True}
