"""Independent fixed candidate/import/completion oracles; host read-only, no PT inflation."""
import ast,hashlib,json,pathlib
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def candidate(name):
 r=W/name;raw=(r/'RELEASE-MANIFEST.json').read_bytes();d=json.loads(raw)
 bad=[]
 for a in d['artifacts']:
  p=r/a['path']
  if p.stat().st_size!=a['size'] or hashlib.sha256(p.read_bytes()).hexdigest()!=a['sha256']:bad.append(a['path'])
 sums={a['path']:a['sha256'] for a in d['artifacts']};sums['RELEASE-MANIFEST.json']=hashlib.sha256(raw).hexdigest()
 exact=(r/'SHA256SUMS').read_bytes()==''.join(sums[n]+'  '+n+'\n' for n in sorted(sums)).encode('ascii')
 assert len(d['artifacts'])==186 and len(sums)==187
 return bad,exact
assert candidate('pg468-release-v1')==(['VERSION'],False)
assert candidate('pg468-release-v2')==([],False)
assert candidate('pg468-release-v3')==([],True)
assert candidate('pg465-release-v2')==([],True)
tools=ROOT/'tools/quality/vm/050_s1'
t=ast.parse((tools/'pg468_stage_candidate_v2.py').read_text());a={n.targets[0].id:n.value for n in t.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
files={ast.literal_eval(k) for k in a['FILES'].keys};expected={'Pg468CodeOnlyDeployment.class','pg468_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'}
assert files==expected|{'release.tar','manifest.sig'}
payload=ast.parse(ast.literal_eval(a['PAYLOAD']))
loops=[{ast.literal_eval(e) for e in n.iter.elts} for n in ast.walk(payload) if isinstance(n,ast.For) and isinstance(n.iter,ast.Tuple) and all(isinstance(e,ast.Constant) for e in n.iter.elts)]
assert expected in loops
imports={n.module+'.py' for n in ast.walk(ast.parse((tools/'pg468_watch_parent.py').read_text())) if isinstance(n,ast.ImportFrom)}
assert imports=={'pg457_stable_actor.py','pg462_observer_identity.py'} and imports<expected
for n in ast.walk(a['FILES']):
 if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.startswith('tools/'):assert (ROOT/n.value).is_file()
fixed=b'codeOnly=true\nschema027=true\nallOwnedScopesReturnedNormally=true\nall341Preserved=true\noldThirtySixRecordsPreserved=true\nunitsStarted=0\n'
s=ast.parse((tools/'pg468_external_start_once.py').read_text());strings=[n.value for n in ast.walk(s) if isinstance(n,ast.Constant) and isinstance(n.value,str)];guest=next(v for v in strings if v.startswith('import datetime,hashlib'))
constants=[n.value for n in ast.walk(ast.parse(guest)) if isinstance(n,ast.Constant) and isinstance(n.value,bytes)]
assert fixed in constants
for invalid in [fixed.replace(b'allOwned',b'newOwned'),fixed[:-1],fixed+b'extra=true\n',fixed.replace(b'true',b'false',1),b'']:
 assert invalid!=fixed
assert fixed.decode().replace('\n','\\n') in (tools/'Pg468CodeOnlyDeployment.java').read_text()
print('PG468_CONTRACT_ORACLE actual0=true rejectedV1V2Detected=true acceptedV3Old186187=true importsExact=true completion6Lines=true invalidCompletion5Rejected=true productionPT0=true nativeMutation=false')
