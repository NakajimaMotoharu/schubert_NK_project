"""SSC286: finite fresh M/A/RODB whole-graph read timing, no actor operations."""
import ast
import base64
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
import pg4052_failed_current_capture as capture
from pg4056_file_profile_compile_dependency import dependency, SHA
from pg4002_literal_invariant_publication_sources import ro
from pg1441_current_cold_refs import source as prior_refs

ROOT = Path(__file__).resolve().parents[2]
SLOT = 'pg4058-original-read-profile-v1'


def contracts():
    tree = ast.parse(prior_refs()); result = ''
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name == 'exec_record': result += ast.unparse(n) + '\n'
        if (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                and isinstance(n.value.func, ast.Name) and n.value.func.id == 'exec'
                and len(n.value.args) == 2 and isinstance(n.value.args[1], ast.Name)
                and n.value.args[1].id == 'CONFIG_CONTRACT'):
            result += 'CONFIG_CONTRACT={}\nexec(' + repr(ast.literal_eval(n.value.args[0])) + ',CONFIG_CONTRACT)\n'
    return result + ro.unused.pinned(W / ro.unused.TOOLS, 'pg3982_configuration_capture.py')


def payload(action):
    if action not in {'compile', 'run'}: raise ValueError('compile or run only')
    raw = capture.payload(); raw = raw[:raw.index('import dbus\nbus=')]
    raw = raw.replace('pg4052-failed-current-capture-v1', SLOT)
    # compile creates the new namespace; run only reopens its exact saved source/jar.
    raw = raw.replace('require(not os.path.lexists(save));os.umask(0o077);save.mkdir(mode=0o700)',
                      "os.umask(0o077);" + ("require(not os.path.lexists(save));save.mkdir(mode=0o700)" if action == 'compile' else "require(save.is_dir())"))
    java = (ROOT / 'tools/quality/RootOriginalReadProfile.java').read_bytes()
    prefix = 'JAVA_B64=' + repr(base64.b64encode(java).decode()) + '\nANNOTATION_B64=' + repr(base64.b64encode(dependency()).decode()) + '\nANNOTATION_SHA=' + repr(SHA) + '\n'
    return prefix + raw + '\n' + contracts() + '\n' + SETUP + ('\n' + COMPILE if action == 'compile' else '\n' + RUN)


SETUP = r'''
import base64,selectors
java_raw=base64.b64decode(JAVA_B64);annotation_raw=base64.b64decode(ANNOTATION_B64);require(hashlib.sha256(annotation_raw).hexdigest()==ANNOTATION_SHA)
java=save/'RootOriginalReadProfile.java';annotation=save/'spotbugs-annotations-4.10.4.jar';classes=save/'classes'
cp=str(root/'operations/batch.jar')+':'+str(root/'operations/lib/*')+':'+str(root/'api/lib/*')+':'+str(annotation)
env={k:v for k,v in os.environ.items()if k not in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH']}
'''

COMPILE = r'''
java.write_bytes(java_raw);annotation.write_bytes(annotation_raw);classes.mkdir(mode=0o700)
args=['/opt/jdk-25.0.4/bin/javac','-Xlint:all','-Werror','-sourcepath','','-cp',cp,'-d',str(classes),str(java)]
r=subprocess.run(args,env=env,capture_output=True,timeout=40);(save/'compile.private.log').write_bytes(r.stdout+r.stderr)
value={'actualExit':r.returncode,'source':data['source']['commit'],'javaSha256':hashlib.sha256(java_raw).hexdigest(),'annotationSha256':ANNOTATION_SHA,'compileCommand':args,'businessOrProfileIssued':False,'formalAccepted':False}
(save/'compile.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))
raise SystemExit(r.returncode)
'''

RUN = r'''
require(java.read_bytes()==java_raw and annotation.read_bytes()==annotation_raw)
compiled=json.loads((save/'compile.safe.json').read_bytes());require(compiled['actualExit']==0 and compiled['javaSha256']==hashlib.sha256(java_raw).hexdigest())
require(not os.path.lexists(save/'run-reserved.private'));(save/'run-reserved.private').write_bytes(b'one readonly diagnostic\n')
for filename,expected in old['unitFilesActual'].items():
 p=Path(filename);require(metadata(p)+[hashlib.sha256(p.read_bytes()).hexdigest()]==expected)
def config():
 value={}
 for name in old['units']:
  rawcfg=command(['systemctl','show',name,'--property='+','.join(sorted(FIELDS))],1048576).decode();item=complete_configuration(rawcfg,name)
  require(CONFIG_CONTRACT['same'](old['configuration'][name],item,exec_record));value[name]=item
 return value
def inodes(pid):
 result=set()
 for p in (Path('/proc')/str(pid)/'fd').iterdir():
  try:
   value=str(p.readlink())
   if value.startswith('socket:[')and value.endswith(']'):result.add(value[8:-1])
  except (FileNotFoundError,ProcessLookupError):pass
 return result
def peers(value,owned=None):
 table={}
 for line in Path('/proc/net/tcp').read_text().splitlines()[1:]:
  v=line.split()
  if v[3]=='01':table[(v[1],v[2])]=v[9]
 actual=value['database']['peers'];require(len(actual)==(4 if owned else 3))
 roles={'schubert_app':('schubert-nk-api.service',2),'schubert_web_session':('schubert-nk-web.service',1)};counts={k:0 for k in roles}
 for row in actual:
  require(row['address']=='127.0.0.1'and type(row['port'])is int and row['port']>0)
  if owned and row['pid']==owned[1]:
   require(row['user']=='schubert_batch'and row['application']=='PG286-original-profile');pid=owned[0]
  else:
   require(row['user']in roles);unit,_=roles[row['user']];counts[row['user']]+=1;pid=value['actors'][unit]['pid']
  client='0100007F:'+format(row['port'],'04X');server='0100007F:1538'
  require(table.get((client,server))in inodes(pid)and table.get((server,client))in inodes(row['pid']))
 require(counts=={k:v[1]for k,v in roles.items()})
 if owned:
  locks=value['database']['locks'];require(len(locks)==1 and locks[0]['pid']==owned[1]and locks[0]['classid']==0 and locks[0]['objid']==71419602 and locks[0]['objsubid']==1 and locks[0]['mode']=='ExclusiveLock'and locks[0]['granted'])
  require(len(value['flocks'])==2 and all(line.split()[4]==str(owned[0])for line in value['flocks']))
 else:require(not value['database']['locks']and not value['flocks'])
def same_values(before,after):
 for key in ['units','actors','durable','native','startup','runtime']:require(before[key]==after[key])
 require(before['database']['rows']==after['database']['rows'])
def save_private(name,value):
 encoded=json.dumps(value,sort_keys=True).encode()
 with(save/name).open('xb')as f:f.write(encoded);f.flush();os.fsync(f.fileno())
 return hashlib.sha256(encoded).hexdigest()
import dbus
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[];child=None
try:
 for unit in old['units']:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 baseline=snapshot();baseline2=snapshot();peers(baseline);peers(baseline2);same_values(baseline,baseline2);fixed_config=config();before_sha=save_private('before.private.json',baseline)
 args=['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',str(classes)+':'+cp,'dev.codex.schubert.nk.batch.file.RootOriginalReadProfile']
 error=(save/'java-stderr.private.log').open('xb');child=subprocess.Popen(args,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=error,text=True,bufsize=1)
 def frame():
  sel=selectors.DefaultSelector();sel.register(child.stdout,selectors.EVENT_READ)
  try:require(bool(sel.select(60)));line=child.stdout.readline();require(0<len(line)<200);return line.strip()
  finally:sel.close()
 ready=frame();require(re.fullmatch(r'ORIGINAL_PROFILE_READY [1-9][0-9]{0,9}',ready)is not None);backend=int(ready.split()[1]);owned=(child.pid,backend)
 for phase in ['ready','measured']:
  current1=snapshot();current2=snapshot();peers(current1,owned);peers(current2,owned);same_values(baseline,current1);same_values(current1,current2);require(config()==fixed_config)
  save_private(phase+'.private.json',current2)
  child.stdin.write('CONTINUE\n');child.stdin.flush()
  require(frame()==('ORIGINAL_PROFILE_MEASURED'if phase=='ready'else'ORIGINAL_PROFILE_CLOSED'))
 post=snapshot();post2=snapshot();peers(post);peers(post2);same_values(baseline,post);same_values(post,post2);require(config()==fixed_config);after_sha=save_private('after.private.json',post2)
 child.stdin.write('CONTINUE\n');child.stdin.flush();remaining=child.communicate(timeout=20)[0];error.close();require(child.returncode==0)
 lines=remaining.splitlines();require(lines[-1]=='ORIGINAL_PROFILE_NORMAL_RETURN'and all(re.fullmatch(r'READONLY_PROFILE1 phase=[A-Za-z-]+ count=[0-9]+ nanos=[0-9]+',l)for l in lines[:-1]));(save/'profile.safe.log').write_text(remaining)
 require(manifest.read_bytes()==raw and current.resolve(strict=True)==root and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot)
finally:
 # ABORT is only our diagnostic's stdin: it raises and unwinds its read-only scopes.
 # No signal or retry of an unknown owner; retain Ref/isolation if bounded return is unknown.
 if child is not None and child.poll()is None:
  (save/'interrupted-child.private.json').write_text(json.dumps({'pid':child.pid,'source':data['source']['commit'],'notAccepted':True}))
  try:
   child.stdin.write('ABORT\n');child.stdin.flush();child.wait(timeout=20)
  except (BrokenPipeError,subprocess.TimeoutExpired):
   import time
   (save/'unknown-owner.private').write_bytes(b'no signal; retained observer refs\n')
   while True:time.sleep(1)
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()
value={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'javaSha256':hashlib.sha256(java_raw).hexdigest(),'compileSha256':hashlib.sha256((save/'compile.safe.json').read_bytes()).hexdigest(),'profile':lines[:-1],'newMARDDBTenRefNormalClose':True,'all24OriginalBackupNativeUnitConfigUnchanged':True,'ordinaryPoolsFreshSocketMatched':True,'parent143StillFailed':True,'beforeSha256':before_sha,'afterSha256':after_sha,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorityOrCoverageClaim':False,'signalStartStopReloadDbWrites':0,'formalAccepted':False}
(save/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))
'''


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {'compile', 'run'}: raise SystemExit('compile or run')
    action = sys.argv[1]; os.umask(0o077); out = W / (SLOT + '-' + action); out.mkdir()
    raw = payload(action); compile(raw, '<fresh owned readonly original profile>', 'exec'); (out / 'payload.private.py').write_text(raw)
    with management_gate(P / 'current-management-critical.lock'):
        r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), capture_output=True, timeout=300)
    (out / 'stdout.safe.json').write_bytes(r.stdout); (out / 'stderr.private.log').write_bytes(r.stderr)
    value = {'actualExit': r.returncode, 'source': capture.SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'action': action, 'formalAccepted': False}
    if r.returncode == 0: value['result'] = json.loads(r.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value)); return r.returncode


if __name__ == '__main__': raise SystemExit(main())
