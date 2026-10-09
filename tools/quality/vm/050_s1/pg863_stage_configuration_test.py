"""Independent canonical32 fixtures against actual generated parser."""
import ast
from pg863_stage_candidate_v4 import source
tree=ast.parse(source());payload=next(n.value.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
t=ast.parse(payload);nodes=[n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='configuration_value' or isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='FIELDS'for x in n.targets)]
ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual strict32>','exec'),ns)
names='Id Type Restart RemainAfterExit KillMode SendSIGKILL TimeoutStartUSec TimeoutStopUSec ExecStart ExecStop User Group SupplementaryGroups NoNewPrivileges CapabilityBoundingSet AmbientCapabilities ProtectSystem ProtectHome PrivateTmp PrivateDevices RestrictAddressFamilies ReadWritePaths ReadOnlyPaths Requires After FragmentPath DropInPaths RestrictSUIDSGID UMask LimitCORE MemoryMax TasksMax'.split()
raw=''.join(k+'='+('b a'if k in ('After','Requires')else '')+'\n'for k in names)
v=ns['configuration_value'](raw);assert len(v)==32 and v['After']=='a b'and v['Requires']=='a b'and v['ExecStop']==''
for bad in [None,raw[:-1],raw.replace('ExecStop=\n',''),raw+'Unknown=x\n',raw+'ExecStop=\n',raw.replace('After=b a','After=a a'),raw.replace('After=b a','After=a  b')]:
 try:ns['configuration_value'](bad)
 except ValueError:pass
 else:raise AssertionError('bad32 accepted')
assert "GetAll('org.freedesktop.systemd1.Service')"in payload and "str(stop.signature)!='(sasbttttuii)'"in payload
assert "value['configuration']={u:complete_configuration("in payload
print('STAGE863003 actual strict32 normal+7 negative / typed empty ExecStop connected PASS')
