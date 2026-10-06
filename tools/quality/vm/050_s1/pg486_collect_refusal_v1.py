"""Retain full-v1 format refusal and five partial modules; never full/formal PASS."""
import hashlib,json,pathlib,shutil,xml.etree.ElementTree as E,os
os.umask(0o077)
root=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');work=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');base=work/'pg486-six-full-v1'
def read(s):return pathlib.Path(str(base)+s).read_text().strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert read('.exit')=='1';log=read('.log');assert 'CleanupTerminalRepositoryTest.java' in log and 'format violations' in log
saved=work/'pg486-refused-host-v1';assert not saved.exists();saved.mkdir(mode=0o700);rows=[]
for module in ['protocol','storage','bootstrap','api','web']:
 source=root/'src'/('schubert-nk-'+module)/'target';dest=saved/module;shutil.copytree(source,dest)
 for p in [dest,*dest.rglob('*')]:p.chmod(0o700 if p.is_dir() else 0o600)
 suites=list((dest/'surefire-reports').glob('TEST-*.xml'));assert suites
 values=[E.parse(p).getroot() for p in suites];assert all(all(int(s.get(k,'0'))==0 for k in ['failures','errors','skipped']) for s in values)
 rows.append({'module':module,'tests':sum(int(s.get('tests')) for s in values),'suites':len(values),'partialOnly':True})
assert not list((root/'src/schubert-nk-batch/target/surefire-reports').glob('TEST-*.xml'))
out=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG486-full-refusal-v1/manifest.json';assert not out.exists();out.parent.mkdir(parents=True)
data={'id':'PG486-full-refusal-v1','source':read('.source'),'branch':'dev-foundation','started':read('.started'),'completed':read('.completed'),'actualExit':1,'bug':'BUG-787','testId':'PT-OPS-CTERM010','partialModules':rows,'batch':'NOT_RUN_FORMAT_REFUSED','fullAccepted':False,'coverage100':False,'formal':False,'nativeAccepted':False,'logSha256':sha(pathlib.Path(str(base)+'.log')),'sourceFilesSha256':sha(pathlib.Path(str(base)+'.source-files.sha256')),'rawLogXmlInGit':False}
with out.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
print(json.dumps({'fullAccepted':False,'actualExit':1,'fivePartialFrozen':True,'batchNotRun':True,'manifestSha256':sha(out)}))
