"""Safe stopped-deployment proof: actual private results, no raw material exported."""
import hashlib,json,pathlib,subprocess
R=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
S='09b448644cfe70c87df9c89aa5c0c1bf6efdeeea'
subprocess.run(['git','diff','--exit-code',S,'--','src','pom.xml'],cwd=R,check=True)
for n in ['pg474-six-full-v2','pg474-stopped-verify-v1','pg474-stopped-activate-v1']:
 assert (W/(n+'.exit')).read_text().strip()=='0'
payload="""import hashlib,json,pathlib,os,stat
assert os.geteuid()==0
p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg474-stopped-deploy')
assert (p/'complete.private').read_bytes()==b'allNewScopesReturnedNormally=true\\noriginalDonePreserved=true\\nrows391=true\\nallBackupPreserved=true\\nstarts0=true\\nstops0=true\\npermits0=true\\nddl0=true\\n'
d=json.loads((p/'native-before.private.json').read_text());assert len(d['oldExec'])==19
for x in d['oldExec']:
 a=pathlib.Path(x['archive']);s=a.lstat();assert a.parent==p and stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and s.st_size==x['bytes']
 assert hashlib.sha256(a.read_bytes()).hexdigest()==x['sha256']
current=pathlib.Path('/opt/schubert-nk/current');assert current.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG474')
assert hashlib.sha256((current/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='3f6b837c12282baca8b2c5fc79c85916421b6940471cca5d544381072120af18'
print(json.dumps({'newScopesNormal':True,'oldSeventeenExecTwoHeapActualArchivesVerified':True,'rawValuesExported':False,'completeSha256':hashlib.sha256((p/'complete.private').read_bytes()).hexdigest(),'archiveInventorySha256':hashlib.sha256((p/'native-before.private.json').read_bytes()).hexdigest(),'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()}))
"""
ssh=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1','sudo -n python3 -B -']
v=subprocess.run(ssh,input=payload.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
proof=json.loads(v.stdout)
manifest={'id':'PG474-stopped-code-only-v1','branch':'dev-foundation','applicationSource':S,'candidateDigest':'3f6b837c12282baca8b2c5fc79c85916421b6940471cca5d544381072120af18','fullTests':3365,'suites':505,'staticModulesZero':6,'toolTests':{'java':71,'python':153,'inventory':37,'term':240,'control':265},'toolAssertionsAreProductionPT':False,'relatedBUG':[],'relatedYKT':[],'PGD':['PG-D379'],'testIds':['PT-OPS-CODE474001','PT-OPS-CODE474002','PT-OPS-CODE474003','PT-OPS-CODE474004'],'rootProof':proof,'runs':{},'formalAccepted':False,'globalCoverage100':False,'oldUnknownNormalized':False,'rawLogsInGit':False}
for n in ['pg474-stopped-verify-v1','pg474-stopped-activate-v1']:
 manifest['runs'][n]={'actualExit':int((W/(n+'.exit')).read_text()),'started':(W/(n+'.started')).read_text().strip(),'completed':(W/(n+'.completed')).read_text().strip(),'privateLogSha256':hashlib.sha256((W/(n+'.private.log')).read_bytes()).hexdigest()}
manifest['tools']={n:hashlib.sha256((R/'tools/quality/vm/050_s1'/n).read_bytes()).hexdigest() for n in ['Pg474StoppedDeployment.java','Pg474StoppedDeploymentTest.java','pg474_stopped_native.py','pg474_stopped_native_test.py']}
out=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG474-stopped-code-only-v1/manifest.json'
assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True)
with out.open('x') as f:f.write(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'actualExit':0,'archives19':True,'scopeNormal':True,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'formal':False}))
