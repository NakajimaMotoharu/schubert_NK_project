"""Post-DONE same ordinary generations A01; no live-parent authority borrowed."""
import ast
import inspect
import json
from pg1192_current_resume_a01_v3 import code as previous
from pg1194_completed_resume_receipt_v2 import payload as receipt_payload
from pg1041_cold_policy_diagnostic import W

OWNERS = {
    'schubert-nk-api.service': ('525675','bfae0cf915c74f7bbf35a7a1ec4f8cd9','52270585599',5227058),
    'schubert-nk-web.service': ('526861','898429f0e6a64d4fa7a6c07e4473fe8a','52284311947',5228431),
    'caddy.service': ('528966','1037150931c04cb6b64b249c0cf916c3','52308064463',5230806),
}
IDENTITIES = {
    'schubert-nk-api.service': ('999','981',('980','981','982','986'),'/opt/jdk-25.0.4/bin/java','dev.codex.schubert.nk.api.bootstrap.ApiProcessMain'),
    'schubert-nk-web.service': ('997','980',('980','982','986'),'/opt/jdk-25.0.4/bin/java','dev.codex.schubert.nk.web.bootstrap.WebProcessMain'),
    'caddy.service': ('993','978',('978',),'/usr/bin/caddy',None),
}


def qualify_actor(unit, status, executable, argv):
    fields={'Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs'}
    if type(unit) is not str or unit not in IDENTITIES or type(status) is not dict or set(status)!=fields or any(type(v) is not str for v in status.values()) or type(argv) is not bytes:
        raise ValueError('same ordinary identity schema refused')
    uid,gid,groups,exe,entry=IDENTITIES[unit]
    if status['Uid'].split()!=[uid]*4 or status['Gid'].split()!=[gid]*4 or tuple(status['Groups'].split())!=groups or status['NoNewPrivs']!='1' or executable!=exe:
        raise ValueError('same ordinary identity refused')
    if any(status[k]!='0000000000000000'for k in ['CapInh','CapPrm','CapEff','CapBnd','CapAmb']) or entry is not None and entry.encode() not in argv.split(b'\0'):
        raise ValueError('same ordinary capabilities entry refused')


def guard():
    m=json.loads((W/'pg1194-completed-resume-receipt-v2.safe.json').read_bytes())
    if m['actualExit']!=0 or m['source']!='d5b00104280028d9ea81b44c1d1c805f3c2861ed' or m['receipt']['endMonotonicUs']!=52530445203:
        raise ValueError('qualified actual new PID1 DONE receipt required')
    s=receipt_payload();s=s[:s.index("private=Path('/var/lib/pgpt-s1-preservation/pg1194-completed-resume-receipt-v2')")]
    s='OWNERS='+repr(OWNERS)+'\nIDENTITIES='+repr(IDENTITIES)+'\n'+inspect.getsource(qualify_actor)+'\n'+s+BODY
    ast.parse(s);return s


BODY=r'''
if result['endMonotonicUs']!=52530445203:raise ValueError('actual completed Root changed')
release=Path('/opt/schubert-nk/current');manifest=(release/'RELEASE-MANIFEST.json').read_bytes()
if str(release.readlink())!='/opt/schubert-nk/releases/0.1.0-PG1068' or hashlib.sha256(manifest).hexdigest()!='0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d':raise ValueError('current signed source changed')
units={UNIT:state}
for unit,(pid,inv,start,ticks) in OWNERS.items():
 raw=subprocess.check_output(['/usr/bin/systemctl','show',unit,'--property=InvocationID,MainPID,ControlPID,Job,ExecMainStartTimestampMonotonic,Result'],text=True,timeout=5)
 v=dict(line.split('=',1)for line in raw.splitlines())
 if v['MainPID']!=pid or v['InvocationID']!=inv or v['ExecMainStartTimestampMonotonic']!=start or v['ControlPID']!='0' or v['Job'] or v['Result']!='success':raise ValueError('same ordinary generation required')
 p=Path('/proc')/pid
 if int((p/'stat').read_text().rpartition(')')[2].split()[19])!=ticks:raise ValueError('same ordinary actor required')
 status=dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)
 fields={'Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs'}
 status={k:status[k].strip()for k in fields}
 qualify_actor(unit,status,str((p/'exe').readlink()),(p/'cmdline').read_bytes())
 units[unit]=v
print(json.dumps(units))
'''


def code():
    s=previous().replace('pg1192','pg1195').replace('PG1192','PG1195')
    tree=ast.parse(s);node=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='GUARD'for t in n.targets))
    literal=ast.get_source_segment(s,node.value);s=s.replace(literal,repr(guard()),1)
    ast.parse(s);return s


if __name__=='__main__':
    env={'__file__':__file__,'__name__':'completed_current_A01'}
    exec(compile(code(),'<completed Root same ordinary A01>','exec'),env);env['main']()
