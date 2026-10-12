"""New candidate-only hostRO from current completed-DONE/whole-input profile.

Only role-specific constants are changed in the isolated RO method; current
identity and original DONE remain the certified PG1544 cohort.
"""
import ast
import inspect
from pg1681_closed_candidate_sources import sources as completed
from pg1681_input_closure_contract import STANDARD, canonical
from pg1300_current_candidate_ro_sources import RO_METHOD, CANDIDATE_BEFORE
from pg835_pending_v5 import METHOD, ORACLE

TOOLS='pg1686-completed-candidate-ro-tools-v1'
SAVE='pg1689-completed-candidate-host-ro-v1'
CLASS='Pg1686CandidateRo'
BOM='195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1'
SOURCE='2741c4546afad6c1e8b6efbd53dfb58144edf7bb'


def once(raw,old,new):
    if raw.count(old)!=1:raise ValueError('one explicit completed RO boundary required')
    return raw.replace(old,new)


def method():
    raw=RO_METHOD
    for a,b in [('PG1292','PG1638'),('pg1292','pg1638'),('769ddb15cd735c25fef581b5f9850ef9d0053c0f',SOURCE),('ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99',BOM),('PG1068','PG1544'),('pg1068','pg1544'),('d5b00104280028d9ea81b44c1d1c805f3c2861ed','4d6bcbddb417b76d27e52d5d9640752c300edccf')]:raw=raw.replace(a,b)
    if not raw.endswith('  }\n'):raise ValueError('one final candidate tuple restoration required')
    return raw[:-4]+'    verifyCurrentIdentity();\n  }\n'


def sources():
    result={}
    for name,raw in completed(BOM).items():
        if name=='pg1681_input_preflight.py':continue
        for a,b in [('Pg1640UnusedStage',CLASS),('Pg1640','Pg1686'),('pg1640','pg1686'),('PG1640','PG1686'),('Pg1660CurrentIdentityTest','Pg1686CurrentIdentityTest'),('Pg1681InputBoundaryTest','Pg1686InputBoundaryTest'),('pg1681_input_preflight.py','pg1686_input_preflight.py'),('pg1681-completed-unused-tools-v4',TOOLS),('pg1684-completed-unused-placement-v4',SAVE)]:
            name=name.replace(a,b);raw=raw.replace(a,b)
        if name==CLASS+'.java':
            raw=once(raw,'"place".equals(args[0])','"prepare-ro".equals(args[0])')
            raw=once(raw,'"place",Integer.toString(pid)','"prepare-ro",Integer.toString(pid)')
            raw=once(raw,'"place".equals(name)','"ro".equals(name)')
            raw=once(raw,'phase="SIGNED_UNUSED_PLACEMENT";refs.check("place");','phase="CANDIDATE_RO";candidateReadOnly();refs.check("ro");')
            mount=METHOD.replace('PG832','PG1638').replace('\\\\n','\\n')
            raw=once(raw,'  public static void main',mount+'\n'+method()+'\n  public static void main')
            raw=raw.replace('unusedCandidatePlaced=true','candidateReadOnlyVerified=true')
        elif name=='Pg1686StopLabelTest.java':
            oracle=ORACLE.replace('PG832','PG1638').replace('Pg835PendingDeployment',CLASS).replace('\\\\n','\\n')
            raw=once(raw,'    System.out.println(',oracle+'\n    System.out.println(')
        elif name=='pg1686_native_owned_stop.py':
            raw=raw.replace("b'place'","b'prepare-ro'").replace("'place'","'ro'")
        elif name=='pg1686_native_refs.py':
            raw=once(raw,"sys.argv[1]=='place'","sys.argv[1]=='prepare-ro'")
            tree=ast.parse(raw);main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
            main.body=[n for n in main.body if not(isinstance(n,ast.FunctionDef)and n.name=='place_candidate')]
            raw=ast.unparse(tree)+'\n'
            before=CANDIDATE_BEFORE.replace('PG1292','PG1638').replace('769ddb15cd735c25fef581b5f9850ef9d0053c0f',SOURCE).replace('ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99',BOM)
            raw=once(raw,'    held = owner()',before+'\n    held = owner()')
            raw=raw.replace("if action == 'place':","if action == 'ro':")
            raw=once(raw,'            place_candidate()','            candidate_ro_post(candidate_before)')
        if name.endswith('.py'):ast.parse(raw)
        result[name]=raw
    result['pg1686_input_preflight.py']=preflight()
    return result


PREFLIGHT=r'''
import hashlib,json,os,pathlib,stat
def require(v):
 if not v:raise ValueError('completed RO input closure refused')
require(os.geteuid()==0)
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1686-completed-candidate-ro-tools-v1')
pins=json.loads((root/'payload-sha256.json').read_bytes())
require({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==set(pins)|{'payload-sha256.json'})
for name,digest in pins.items():
 canonical(name);p=root/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
 if name.endswith('.py'):
  for node in ast.walk(ast.parse(p.read_bytes())):
   modules=[a.name for a in node.names]if isinstance(node,ast.Import)else[node.module]if isinstance(node,ast.ImportFrom)else[]
   for module in modules:
    require(type(module)is str)
    base=module.split('.')[0]
    require(base+'.py'in pins if base.startswith('pg')else base in STANDARD or base=='dbus')
require('Pg1686CandidateRo.class'in pins and 'Pg1686CandidateRo$References.class'in pins)
candidate=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638')
raw=(candidate/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(raw).hexdigest()=='195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1')
data=json.loads(raw);require(data['source']['commit']=='2741c4546afad6c1e8b6efbd53dfb58144edf7bb'and len(data['artifacts'])==187)
for row in data['artifacts']:
 canonical(row['path']);p=candidate/row['path'];require(p.stat().st_size==row['size']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'])
require(str(pathlib.Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG1544')
require(not pathlib.Path('/var/lib/pgpt-s1-preservation/pg1689-completed-candidate-host-ro-v1').exists())
print('PG1681_INPUT_CLOSURE_READY',flush=True)
'''


def preflight():
    return 'import ast\nfrom pathlib import PurePosixPath\nSTANDARD=frozenset('+repr(tuple(sorted(STANDARD)))+')\n'+inspect.getsource(canonical)+'\n'+PREFLIGHT
