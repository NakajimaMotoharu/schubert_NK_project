"""SSC305 independent full current witness in the frozen failed phase; signals0."""
import ast
import hashlib
import inspect
import json
from pyflakes.api import check
import pg5080_current_bootstrap_before as before
import pg5082_current_bootstrap_sources as role
import pg1722_bootstrap_db_owner_readonly_proof as actor_template
from pg1723_bootstrap_expired_peer_readonly_proof import PEER
from pg1665_unused_pair_contract import fresh_parent as historical_fresh_parent

SLOT = 'pg5092-retained-pair-full-proof-v1'
W = role.W
OBSERVED_SHA = 'ea7fb36a70257112fba4d45e9dcde7750919ba593303aa8c119ea98225f421b4'


def fresh_source():
    raw = inspect.getsource(historical_fresh_parent)
    for old, new in [('fresh_parent(', 'fresh_current_parent('), ('101', '100'),
                     ('other99', 'other98'), ("'29'", "'31'"), ("'32'", "'90'")]:
        raw = raw.replace(old, new)
    return raw


CHILD = r'''
def normalized(v):return json.loads(json.dumps(v))
def refs_actor():
 p=pathlib.Path('/proc/927536');status=dict(l.split(':',1)for l in(p/'status').read_text().splitlines()if ':'in l)
 require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==31055311 and os.readlink(p/'exe')=='/usr/bin/python3.14')
 require(hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==EXPECTED_CHILD['argvSha256'])
 require(not {c for t in(p/'task').iterdir()for c in(t/'children').read_text().split()})
 fds={f.name:{'metadata':list(metadata9(f.stat())),'target':os.readlink(f)}for f in(p/'fd').iterdir()}
 value={'pid':927536,'ticks':31055311,'argvSha256':EXPECTED_CHILD['argvSha256'],'authority':{k:status[k].strip()for k in EXPECTED_CHILD['authority']},'cgroup':(p/'cgroup').read_text(),'fds':fds}
 require(value==EXPECTED_CHILD and set(fds)=={'0','1','2','3','4','5','6'})
 connection=dbus.SystemBus(private=True)
 try:
  daemon=dbus.Interface(connection.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
  names=[];parents=[]
  for name in daemon.ListNames():
   if not str(name).startswith(':'):continue
   pid=int(daemon.GetConnectionUnixProcessID(name))
   if pid==927536:
    require(int(daemon.GetConnectionUnixUser(name))==0);names.append(str(name))
   if pid==927504:parents.append(str(name))
  require(names==EXPECTED_BUS and len(names)==1 and not parents)
 finally:connection.close()
 return {**value,'busNames':names}
def pair():
 a=normalized(actor());fresh_current_parent(EXPECTED_PARENT,a,time.time_ns())
 return {'parent':a,'child':refs_actor(),'peer':same_peer()}
'''

TAIL = r'''
tool=base/TOOL_NAME
require({p.relative_to(tool).as_posix()for p in tool.rglob('*')if p.is_file()}==set(TOOL_HASHES)|{'payload-sha256.json'})
for name,digest in TOOL_HASHES.items():
 p=tool/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
require(json.loads((tool/'payload-sha256.json').read_bytes())==TOOL_HASHES)
failure=base/'pg5082-bootstrap-verify-v3';require({p.name for p in failure.iterdir()}=={'refs-prepare.private.log'})
require(hashlib.sha256((failure/'refs-prepare.private.log').read_bytes()).hexdigest()=='1c6a71bbcae6f487217e5d9b92dafbf4bb461f226d7544edb62e174bfd7f7ab9')
require(not any(os.path.lexists('/etc/schubert-nk/credentials/'+n)for n in ('bootstrap-admin-username','bootstrap-admin-password')))
require(native==after['native'] and len([p for p in native if p.endswith('.exec')])==86)
a=pair();require(a==pair());locks=normalized([owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']])
require(a==pair()and native==snapshot())
save=base/SLOT;require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'productionSource':SOURCE,'pair':a,'locks':locks,'native':native,'toolHashes':TOOL_HASHES,'all24And32And187Unchanged':True,'allTenKernelEmpty':True,'serverPeerAdvisory0':True,'credentialAbsent':True,'signals0':True,'oldCloseUnknown':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
'''


def observation():
    raw = (W / 'pg5090-retained-pair-observe-v1/stdout.private.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != OBSERVED_SHA:
        raise ValueError('same immutable discovery required, not signal permission')
    value = json.loads(raw)
    def narrow(v):
        return {**{k: v[k] for k in ('pid', 'ticks', 'argvSha256', 'authority', 'cgroup')},
                'fds': {n: {k: r[k] for k in ('metadata', 'target')} for n, r in v['fds'].items()}}
    return narrow(value['parent']), narrow(value['child']), value['childBusNames']


def payload():
    fixed = json.loads((W / 'pg5084-frozen-v1.safe.json').read_bytes())
    if fixed['actualExit'] != 0 or fixed['productionSource'] != role.SOURCE:
        raise ValueError('actual current149 frozen first')
    parent, child, names = observation()
    cp = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
    cp += ':/opt/schubert-nk/releases/0.1.0-PG4980/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG4980/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG4980/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG4980/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
    argv = ['/opt/jdk-25.0.4/bin/java', '--enable-native-access=ALL-UNNAMED', '-cp', cp, 'Pg5082BootstrapExisting', 'verify']
    helpers = actor_template.ACTOR[:actor_template.ACTOR.index('def same_peer():')]
    for old, new in [('383695', '927504'), ('7281859', '31055084'), ('383693', '927502'),
                     ('require(not children)', 'require(children=={927536})'), ('len(fds)==99', 'len(fds)==100')]:
        helpers = helpers.replace(old, new)
    helpers += PEER.replace('/proc/383695', '/proc/927504') + '\n' + fresh_source() + '\n' + CHILD
    tree = ast.parse(before.payload())
    scope = next(n for n in tree.body if isinstance(n, ast.Try) and n.finalbody
                 and any(isinstance(v, ast.FunctionDef) and v.name == 'snapshot' for v in n.body))
    snapshot = next(n for n in scope.body if isinstance(n, ast.FunctionDef) and n.name == 'snapshot')
    loops = [n for n in snapshot.body if isinstance(n, ast.For) and ast.unparse(n.iter) == "('maintenance.lock', 'startup-admission.lock')"]
    if len(loops) != 1:
        raise ValueError('one exact held-lock boundary required')
    loops[0].body = ast.parse('owned_lock(name)').body
    cut = next(i for i, n in enumerate(scope.body) if isinstance(n, ast.Import) and any(a.name == 'pwd' for a in n.names))
    scope.body = scope.body[:cut] + ast.parse(TAIL).body
    # Drop the original outgoing enriched-before print; retain the normal finally.
    tree.body = tree.body[:tree.body.index(scope) + 1]
    tree.body += ast.parse("print(json.dumps({'actualExit':0,'productionSource':SOURCE,'proofSha256':hashlib.sha256(encoded).hexdigest(),'parentPid':927504,'parentTicks':31055084,'childPid':927536,'childTicks':31055311,'parentFdCount':100,'childFdCount':7,'allOriginalValuesUnchanged':True,'serverPeerAdvisory0':True,'normalNewRefScope':True,'signals0':True,'oldCloseUnknown':True,'formalAccepted':False}))").body
    at = next(i for i, n in enumerate(tree.body) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'bus' for t in n.targets))
    tree.body[at:at] = ast.parse(helpers).body
    header = ('EXPECTED_ARGV=' + repr(b'\0'.join(v.encode() for v in argv) + b'\0')
              + '\nEXPECTED_PARENT=' + repr(parent) + '\nEXPECTED_CHILD=' + repr(child)
              + '\nEXPECTED_BUS=' + repr(names) + '\nTOOL_HASHES=' + repr(fixed['fileHashes'])
              + '\nTOOL_NAME=' + repr(role.TOOLS) + '\nSLOT=' + repr(SLOT) + '\n')
    raw = header + ast.unparse(ast.fix_missing_locations(tree)) + '\n'
    if check(raw, '<current held100/7 full independent witness>'):
        raise ValueError('complete independent witness globals required')
    return raw


if __name__ == '__main__':
    raise SystemExit(before.admission.execute(SLOT, payload(), 180))
