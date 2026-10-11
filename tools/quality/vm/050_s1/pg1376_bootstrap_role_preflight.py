"""Fresh independent全current/no resource ownership plus missing one-role/effective/NSS."""
import inspect
import pg1340_published_stop_independent_post_v4 as previous
import pg1369_bootstrap_role_policy as policy
from pg1334_published_owned_stop_sources_v2 import SOURCE

def payload(seals):
    raw=previous.payload(seals)
    marker='bus=dbus.SystemBus(private=True);'
    raw=raw.replace(marker,'import types\npolicy=types.ModuleType("independent_role");exec('+repr(inspect.getsource(policy))+',policy.__dict__)\n'+marker)
    marker=' native=snapshot();require(native==snapshot())'
    if raw.count(marker)!=1:raise ValueError('one current native scope required')
    raw=raw.replace(marker,marker+'''
 policy.before_valid(native)
 role=pathlib.Path('/run/schubert-nk/pt-coverage/ordinary-bootstrap196');require(not os.path.lexists(role))
 require(command(['id','-u','schubert-api']).strip()==b'999'and command(['id','-g','schubert-api']).strip()==b'981')
 unit='schubert-nk-bootstrap-admin.service';cfg=complete_configuration(command(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))]).decode(),unit)
 require(show(unit,{'LoadState','Type'})=={'LoadState':'loaded','Type':'oneshot'}and cfg['User']=='schubert-api'and cfg['Group']=='schubert-api'and str(role)in cfg['ReadWritePaths'].split()and '-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid=BOOTSTRAP-'in cfg['ExecStart'])
 require(not os.listxattr(role.parent)and command(['findmnt','--target',str(role.parent),'--output','FSTYPE','--noheadings']).strip()==b'tmpfs')
''')
    raw=raw.replace('pg1340-published-terminal-post-v4','pg1376-bootstrap-role-preflight-v1').replace('PG1340-published-terminal-post-v4','PG1376-bootstrap-role-preflight-v1')
    compile(raw,'<whole current one missing role guard>','exec');return raw

def source():
    return previous.source().replace('pg1340-published-terminal-post-v4','pg1376-bootstrap-role-preflight-v1')

def main():
    env=dict(previous.previous.transport.__dict__,SOURCE=SOURCE,payload=payload)
    exec(compile(source(),'<current one-role guard transport>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
