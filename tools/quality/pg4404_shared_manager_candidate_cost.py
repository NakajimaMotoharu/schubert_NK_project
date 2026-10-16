"""Private ABBA for actual Child NativeIo against shared fresh reader; no release change."""
import base64
import inspect
from pathlib import Path
import pg4402_child_unit_read_cost as previous
from pg4060_original_profile_dual_stack import once

SLOT = 'pg4404-shared-manager-candidate-cost-v1'


def candidates():
    root = Path(__file__).resolve().parents[2]
    base = root / 'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap'
    return {name: (base / name).read_bytes() for name in
            ['SystemManagerObservation.java', 'LinuxSystemdSession.java', 'ChildStartupContext.java']}


def payload():
    raw = previous.payload()
    raw = once(raw, 'SLOT=' + repr(previous.SLOT), 'SLOT=' + repr(SLOT))
    marker = "with(save/'stdout.private.json').open('xb')as out,(save/'stderr.private.log').open('xb')as err:"
    program = r'''
candidate_classes=save/'candidate-classes';candidate_classes.mkdir(mode=0o700)
candidate_sources=[];candidate_hashes={}
for name,encoded in CANDIDATES.items():
 p=save/name;decoded=base64.b64decode(encoded)
 with p.open('xb')as f:f.write(decoded);f.flush();os.fsync(f.fileno())
 p.chmod(0o400);candidate_sources.append(str(p));candidate_hashes[name]=hashlib.sha256(decoded).hexdigest()
with(save/'candidate-compile.private.log').open('xb')as log:
 result=subprocess.run(['/opt/jdk-25.0.4/bin/javac','--release','25','-Xlint:all','-Werror','-sourcepath','','-cp',cp,'-d',str(candidate_classes)]+candidate_sources,stdout=log,stderr=log)
assert result.returncode==0
results=[]
for phase in ['original','candidate','candidate','original']:
 number=str(len(results));output=save/('comparison-'+number+'.private.json');error=save/('comparison-'+number+'.stderr.private.log')
 classpath=(str(candidate_classes)+':'if phase=='candidate'else'')+str(classes)+':'+cp
 with output.open('xb')as stdout,error.open('xb')as stderr:
  comparison=subprocess.Popen(['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',classpath,'dev.codex.schubert.nk.bootstrap.ChildUnitReadCost'],stdout=stdout,stderr=stderr)
  pidpath=Path('/proc')/str(comparison.pid)
  owner={'pid':comparison.pid,'ticks':int((pidpath/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256((pidpath/'cmdline').read_bytes()).hexdigest()}
  (save/('comparison-'+number+'.owner.private.json')).write_text(json.dumps(owner))
  code=comparison.wait();stdout.flush();stderr.flush();os.fsync(stdout.fileno());os.fsync(stderr.fileno())
 assert code==0
 value=json.loads(output.read_bytes());assert value['actualExit']==0 and value['rootCaptureCalled']is False and value['authority']is False
 results.append({'phase':phase,'actualExit':code,'result':value})
assert manifest.read_bytes()==before
value={'actualExit':0,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','candidateSourceSha256':candidate_hashes,'operationsIssued':0,'measurementOnly':True,'authority':False,'formalAccepted':False,'comparisons':results}
(save/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))
raise SystemExit(0)
'''
    prefix = 'import base64\nCANDIDATES=' + repr({k: base64.b64encode(v).decode() for k, v in candidates().items()}) + '\n'
    return prefix + once(raw, marker, program + '\n' + marker)


def main():
    ns = {**vars(previous.previous.previous), 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(previous.previous.previous.main), '<shared fixed reader finite ABBA>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    main()
