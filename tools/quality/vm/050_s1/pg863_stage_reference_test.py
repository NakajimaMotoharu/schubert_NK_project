"""Literal ten-Ref order/close oracle from the actual v6 generated class."""
import ast,types
from pg863_stage_candidate_v6 import source
t=ast.parse(source());payload=next(n.value.value for n in t.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='PAYLOAD'for x in n.targets));p=ast.parse(payload)
c=next(n for n in p.body if isinstance(n,ast.ClassDef)and n.name=='StageReferences')
expected=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']
events=[]
class Manager:
 def LoadUnit(self,u):events.append(('load',u))
 def RefUnit(self,u):events.append(('ref',u))
 def UnrefUnit(self,u):events.append(('unref',u))
manager=Manager()
class Bus:
 def get_object(self,*a):return manager
 def close(self):events.append(('close',))
fake=types.SimpleNamespace(SystemBus=lambda private:Bus(),Interface=lambda obj,name:obj)
ns={'dbus':fake};exec(compile(ast.Module(body=[c],type_ignores=[]),'<actual all ten Ref>','exec'),ns)
with ns['StageReferences']():assert events==[e for u in expected for e in [('load',u),('ref',u)]]
assert events==[e for u in expected for e in [('load',u),('ref',u)]]+[('unref',u)for u in reversed(expected)]+[('close',)]
events.clear()
try:
 with ns['StageReferences']():raise ValueError('read refused')
except ValueError:pass
else:raise AssertionError('failure normalized')
assert events[-11:]==[('unref',u)for u in reversed(expected)]+[('close',)]
outer=next(n for n in p.body if isinstance(n,ast.With));assert isinstance(outer.items[0].context_expr.func,ast.Name)and outer.items[0].context_expr.func.id=='StageReferences'
text=ast.unparse(outer);assert text.index('before = protected()')<text.index('root.mkdir(')<text.index('assert protected() == before')
for name,oldmodule in [('validate_baseline','pg863_stage_candidate_v2'),('metadata','pg863_stage_candidate_v3'),('configuration_value','pg775_configuration')]:
 actual=next(n for n in ast.walk(p)if isinstance(n,ast.FunctionDef)and n.name==name)
 if name=='configuration_value':continue # fields deliberately strict32, parser same body
 import inspect,importlib
 old=ast.parse(inspect.getsource(getattr(importlib.import_module(oldmodule),name))).body[0]
 assert ast.dump(actual,include_attributes=False)==ast.dump(old,include_attributes=False)
print('STAGE863005 actual all-ten load/ref-before-capture/reverse-close/error propagation PASS; mutation0')
