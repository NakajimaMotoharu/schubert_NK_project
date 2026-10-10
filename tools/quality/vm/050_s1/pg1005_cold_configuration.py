"""Narrow current cold declaration closure, reuses PG1004 data proof without rerun.
No body/store mutation; frozen independent parser distinguishes declarations/history.
"""
import ast
import hashlib
from pathlib import Path
from pg1002_cold_readonly import payload,capture

R=Path(__file__).resolve().parent
def source():
    full=payload()
    # Keep only pure definitions and constants, not snapshot() or its full DB/tree work.
    tree=ast.parse(full);wanted={'require','command','show','cold','configuration_value','complete_configuration'}
    nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))or
      (isinstance(n,ast.FunctionDef)and n.name in wanted)or
      (isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)for t in n.targets))]
    header=ast.unparse(ast.Module(body=nodes,type_ignores=[]))
    # Assignment subset must stop before old baseline/observer execution state.
    header=header[:header.index('base = pathlib.Path(')]
    original=(R/'pg477_unit_references.py').read_bytes()
    assert hashlib.sha256(original).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4'
    parser=next(n for n in ast.parse(original).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record')
    matching=(R/'pg847_configuration.py').read_text().replace('FIELDS','CONFIG_FIELDS')
    scope=(R/'pg1004_cold_refs.py').read_text()
    body=r'''
os.umask(0o077)
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
checkpoint=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1004-cold-readonly-v3/after.private.json').read_bytes()
require(hashlib.sha256(checkpoint).hexdigest()=='1cbb10fa83df138d5f3fe6b40b8107e16475e280745797f6e9e5a58d030073a9')
sealed=json.loads(checkpoint)
old=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg989-bootstrap-post-v4/after.private.json').read_bytes())
FIELDS=set('Id LoadState ActiveState SubState Job MainPID ControlPID InvocationID Type Restart RemainAfterExit Result ExecMainCode ExecMainStatus ExecMainStartTimestampMonotonic ExecMainExitTimestampMonotonic KillMode SendSIGKILL'.split())
import dbus
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
def read():
 values={}
 for name in old['units']:
  state=show(name);require(cold(state)and state==sealed['units'][name])
  raw=command(['systemctl','show',name,'--property='+','.join(sorted(CONFIG_FIELDS))],1048576).decode()
  v=complete_configuration(raw,name)
  require(same(old['configuration'][name],v,exec_record))
  start=exec_record(v['ExecStart']);require(start is not None and start[3:]==('n/a','n/a','0','(null)','0/0'))
  require(v['ExecStop']==''and v==sealed['configuration'][name])
  values[name]=v;require(state==show(name))
 return values
def both():
 a=read();b=read();require(a==b);return a
current=with_references(manager,bus,list(old['units']),both)
result={'run':'PG1005-cold-configuration-v1','actualExit':0,'boot':BOOT,'source':SOURCE,
 'allTenFull32ColdDeclarationsVerifiedTwice':True,'metadataRefsClosed':True,'businessActions':0,
 'v3DataProofReusedNotNewAchievement':True,'warmExitHistoryNotRestored':True,'formalAccepted':False,
 'dataCheckpointSha256':hashlib.sha256(checkpoint).hexdigest(),
 'configurationSha256':hashlib.sha256(json.dumps(current,sort_keys=True).encode()).hexdigest()}
print(json.dumps(result,sort_keys=True))
'''
    result=header+'\n'+ast.unparse(parser)+'\n'+matching+'\n'+scope+'\n'+body
    ast.parse(result);return result

if __name__=='__main__':capture('pg1005-cold-configuration-v1',source())
