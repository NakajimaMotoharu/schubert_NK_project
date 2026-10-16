"""Compare unchanged fresh manager reads with an immutable exact ABI adapter candidate.

The candidate is compiled into a private measurement classpath, never into the release.
Every native read, owner RPC, deadline and close remains in place; no Root capture occurs.
"""
import base64
import hashlib
import inspect
import subprocess
import pg4394_root_read_cost as previous
from pg4060_original_profile_dual_stack import once

SLOT = 'pg4400-exact-native-adapter-cost-v1'


def candidate():
    path = previous.previous.W.parents[1] / 'pgpt-foundation/src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/LinuxSystemdSession.java'
    root = previous.previous.W.parents[1] / 'pgpt-foundation'
    name = str(path.relative_to(root))
    raw = subprocess.check_output(['git', 'show', '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e:' + name], cwd=root, text=True)
    raw = once(raw, 'entry.getKey(), Linker.nativeLinker().downcallHandle(address, entry.getValue()));',
               'entry.getKey(), Linker.nativeLinker().downcallHandle(address, entry.getValue())'
               '.asSpreader(Object[].class, entry.getValue().argumentLayouts().size())'
               '.asType(java.lang.invoke.MethodType.methodType(Object.class, Object[].class)));')
    return once(raw, 'Object value = handle.invokeWithArguments(arguments);',
                'Object value = (Object) handle.invokeExact(arguments);')


def payload():
    raw = previous.payload()
    raw = once(raw, 'SLOT=' + repr(previous.SLOT), 'SLOT=' + repr(SLOT))
    marker = "with(save/'stdout.private.json').open('xb')as out,(save/'stderr.private.log').open('xb')as err:"
    program = r'''
candidate_classes=save/'candidate-classes';candidate_classes.mkdir(mode=0o700)
candidate_source=save/'LinuxSystemdSession.java';candidate_source.write_bytes(base64.b64decode(CANDIDATE))
assert hashlib.sha256(candidate_source.read_bytes()).hexdigest()==CANDIDATE_SHA
with(save/'candidate-compile.private.log').open('xb')as log:
 result=subprocess.run(['/opt/jdk-25.0.4/bin/javac','--release','25','-Xlint:all','-Werror','-sourcepath','','-cp',cp,'-d',str(candidate_classes),str(candidate_source)],stdout=log,stderr=log)
assert result.returncode==0
results=[]
for phase in ['original','candidate','candidate','original']:
 output=save/('comparison-'+str(len(results))+'.private.json');error=save/('comparison-'+str(len(results))+'.stderr.private.log')
 classpath=(str(candidate_classes)+':'if phase=='candidate'else'')+str(classes)+':'+cp
 with output.open('xb')as stdout,error.open('xb')as stderr:
  comparison=subprocess.Popen(['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',classpath,'dev.codex.schubert.nk.batch.platform.RootReadCost'],stdout=stdout,stderr=stderr)
  pidpath=Path('/proc')/str(comparison.pid)
  owner={'pid':comparison.pid,'ticks':int((pidpath/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256((pidpath/'cmdline').read_bytes()).hexdigest()}
  (save/('comparison-'+str(len(results))+'.owner.private.json')).write_text(json.dumps(owner))
  code=comparison.wait();stdout.flush();stderr.flush();os.fsync(stdout.fileno());os.fsync(stderr.fileno())
 assert code==0
 value=json.loads(output.read_bytes());assert value['actualExit']==0 and value['rootCaptureCalled']is False and value['authority']is False
 results.append({'phase':phase,'actualExit':code,'result':value})
assert manifest.read_bytes()==before
value={'actualExit':0,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','candidateSourceSha256':CANDIDATE_SHA,'operationsIssued':0,'measurementOnly':True,'authority':False,'formalAccepted':False,'comparisons':results}
(save/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))
raise SystemExit(0)
'''
    return ('import base64\nCANDIDATE=' + repr(base64.b64encode(candidate().encode()).decode())
            + '\nCANDIDATE_SHA=' + repr(hashlib.sha256(candidate().encode()).hexdigest()) + '\n'
            + once(raw, marker, program + '\n' + marker))


def main():
    ns = {**vars(previous.previous), 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(previous.previous.main), '<exact immutable ABI finite measurement>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    main()
