"""Pure path/schema negative checks and isolated four-stage set-e checks; no Git/remote/product PT."""
from pathlib import Path
import json,hashlib,copy,sys,tempfile,subprocess,shlex,datetime
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'));import public_delta_path_policy as policy
b=r/'evidence/01_PT/018_NK-OPS-001';n=policy.PUBLIC_NAMESPACE_METADATA;raw=subprocess.check_output(['git','show','HEAD:'+n]);assert raw==(r/n).read_bytes();sha=lambda v:hashlib.sha256(v).hexdigest();pin=sha(raw);cases=[]
def accept(name,call):
 call();cases.append(dict(id=name,result='PASS',expected='ACCEPT'))
def reject(name,call):
 try:call()
 except (ValueError,TypeError):cases.append(dict(id=name,result='PASS',expected='REJECT'));return
 raise AssertionError(name)
accept('PATH001-ordinary',lambda:policy.validate_path('src/example.java'))
accept('PATH002-pinned-candidate-name',lambda:policy.validate_path(n))
for i,p in enumerate(sorted(policy.PROTECTED),3):reject(f'PATH{i:03}-protected',lambda p=p:policy.validate_path(p))
for i,p in enumerate(['evidence/01_PT/private-other.json','src/../documents/x.md','/src/x.java','program/characterization/baseline/current/wire.json','evidence/01_PT/x.private.log','evidence/01_PT/raw/output.json','evidence/01_PT/x.raw.json'],5):reject(f'PATH{i:03}-forbidden',lambda p=p:policy.validate_path(p))
accept('META001-known-pinned-public',lambda:policy.validate_metadata(raw,pin));reject('META002-mismatched-sha',lambda:policy.validate_metadata(raw,'0'*64))
data=json.loads(raw)
for key,change in [('extra-key',lambda d:d.update(secretValue='forbidden-schema-only')),('bool-zero',lambda d:d.update(wholeScopeAccepted=0)),('private-row-path',lambda d:d['rows'][0].update(path='evidence/01_PT/private/raw.json')),('sha-shape',lambda d:d['rows'][0].update(sha256='A'*64)),('line-bool',lambda d:d['rows'][0].update(line=True)),('unknown-status',lambda d:d['rows'][0].update(status='NOT_A_CANDIDATE'))]:
 bad=copy.deepcopy(data);change(bad);encoded=json.dumps(bad).encode();reject('META-'+key,lambda encoded=encoded:policy.validate_metadata(encoded,sha(encoded)))
# The actual workflow uses this exact set-e sequential pattern plus independent exit checks.
with tempfile.TemporaryDirectory(prefix='public-scan-tool-check-',dir=r.parent/'pgpt-runs/PG379') as tmp:
 for failure_at in [0,1,2,None]:
  trace=Path(tmp)/('trace-'+str(failure_at));stages=['scan','stage','commit','push'];lines=['set -e']
  for i,name in enumerate(stages):
   lines.append('echo '+shlex.quote(name)+' >> '+shlex.quote(str(trace)))
   lines.append('false' if i==failure_at else 'true')
  result=subprocess.run(['/bin/bash','-c','\n'.join(lines)],capture_output=True,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},timeout=10)
  actual=trace.read_text().splitlines();expected=stages if failure_at is None else stages[:failure_at+1]
  assert actual==expected and result.returncode==(0 if failure_at is None else 1),(failure_at,actual,expected)
  cases.append(dict(id='CHAIN-'+str(failure_at),result='PASS',expectedStages=expected,actualStages=actual,actualExit=result.returncode,realGitOrRemoteActions=False))
out=b/'evidence/PG37564-public-path-failclosed-tool-selfcheck-v1';assert not out.exists();out.mkdir();binding=dict(publicPath=n,sourceCommit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),sha256=pin,schema='PUBLIC_SOURCE_NAMESPACE_CANDIDATE63_EXACT_KEYS_NOT_RAW',protectedExceptionsAllowed=False)
(out/'binding.json').write_text(json.dumps(binding,indent=2)+'\n');v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),toolTests=len(cases),failed=0,cases=cases,binding=binding,pathPolicySha256=sha((r/'tools/quality/public_delta_path_policy.py').read_bytes()),protectedOrPrivateInputsRead=False,allSchemaNegativesReject=True,realGitRemoteProductRootVmDbOrAuthorityActions=0,productTestsExecuted=0,formalUpdated=False,newAcceptance=0);(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(dict(actualExit=0,toolTests=len(cases),failed=0,productTests=0))
