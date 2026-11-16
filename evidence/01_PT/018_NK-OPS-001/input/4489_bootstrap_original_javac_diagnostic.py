"""BUG3129 expose the same failed javac diagnostics, preserving the original snapshot."""
from pathlib import Path
import datetime
import hashlib
import json
import shlex
import shutil
import subprocess

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001/evidence'
old=r.parent/'pgpt-runs/PG379/pg36834-bootstrap-compiler-diagnostic-v1'
work=r.parent/'pgpt-runs/PG379/pg36836-bootstrap-original-javac-diagnostic-v1'
out=b/'PG36836-bootstrap-original-javac-diagnostic-v1'
prior=json.loads((b/'PG36834-bootstrap-compiler-diagnostic-v1/manifest.json').read_text())
assert prior['actualExit']==1 and not work.exists() and not out.exists()
work.mkdir();out.mkdir();shutil.copytree(old/'snapshot',work/'snapshot')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
args=next((old/'snapshot/src/schubert-nk-bootstrap/target').glob('*arguments'))
script=old/'snapshot/src/schubert-nk-bootstrap/target/javac.sh'
original=args.read_text(); rewritten=original.replace(str(old),str(work))
assert rewritten.replace(str(work),str(old))==original
newargs=work/'original-maven-javac.arguments';newargs.write_text(rewritten)
tokens=shlex.split(script.read_text().split(' && ',1)[1])
assert tokens[0]==str(r.parent/'toolchain/jdk-25.0.4/bin/javac')
assert tokens[1]=='@'+str(args)
command=[tokens[0],'@'+str(newargs),*tokens[2:]]
assert all(v.startswith('-J--add-') for v in tokens[2:])
assert all(sha(r/p)==h for p,h in prior['inputHashes'].items())
assert not list((work/'snapshot/src/schubert-nk-bootstrap/target/classes').rglob('*.class'))
home=work/'tool-home';home.mkdir()
env={'PATH':str(r.parent/'toolchain/jdk-25.0.4/bin')+':/usr/bin:/bin',
 'JAVA_HOME':str(r.parent/'toolchain/jdk-25.0.4'),'HOME':str(home),'LANG':'C.UTF-8'}
begin=dict(sourceCore=prior['sourceCore'],inputHashes=prior['inputHashes'],
 originalMavenArgumentsSha256=sha(args),originalMavenScriptSha256=sha(script),
 actualArgumentsSha256=sha(newargs),onlyPathPrefixRelocated=True,originalFlagsUnchanged=True,
 command=command,startAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
(out/'begin.safe.json').open('x').write(json.dumps(begin,indent=2)+'\n')
with (out/'javac.stdout.log').open('xb') as stdout,(out/'javac.stderr.log').open('xb') as stderr:
    try:
        result=subprocess.run(command,cwd=work/'snapshot/src/schubert-nk-bootstrap',
                              env=env,stdout=stdout,stderr=stderr,timeout=90)
        exit_code=result.returncode;timeout=False
    except subprocess.TimeoutExpired:exit_code=124;timeout=True
result=dict(begin,actualExit=exit_code,timedOut=timeout,
 terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 diagnosticOnly=True,qualityQualified=False,productTestsExecuted=0,
 actualDbVmNativeServiceActions=0,heldClassfileActions=0,
 logs={name:sha(out/name) for name in ['javac.stdout.log','javac.stderr.log']})
(out/'manifest.json').open('x').write(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(actualExit=exit_code,diagnosticOnly=True,flagsChanged=False)))
