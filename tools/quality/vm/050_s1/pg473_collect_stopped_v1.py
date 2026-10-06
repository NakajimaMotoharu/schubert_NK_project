"""Safe stopped-deployment proof: actual private results, no raw material exported."""
import hashlib,json,pathlib,subprocess
R=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
S='a5f9e6a54427ff356626245230496d8667082465'
subprocess.run(['git','diff','--exit-code',S,'--','src','pom.xml'],cwd=R,check=True)
for n in ['pg473-six-full-v1','pg473-stopped-verify-v1','pg473-stopped-activate-v1']:
 assert (W/(n+'.exit')).read_text().strip()=='0'
payload="""import hashlib,json,pathlib,os,stat
assert os.geteuid()==0
p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg473-stopped-deploy')
assert (p/'complete.private').read_bytes()==b'allNewScopesReturnedNormally=true\\noriginalDonePreserved=true\\nrows381=true\\nallBackupPreserved=true\\nstarts0=true\\nstops0=true\\npermits0=true\\nddl0=true\\n'
d=json.loads((p/'native-before.private.json').read_text());assert len(d['oldExec'])==13
for x in d['oldExec']:
 a=pathlib.Path(x['archive']);s=a.lstat();assert a.parent==p and stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and s.st_size==x['bytes']
 assert hashlib.sha256(a.read_bytes()).hexdigest()==x['sha256']
current=pathlib.Path('/opt/schubert-nk/current');assert current.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG473')
assert hashlib.sha256((current/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='ffae42347b43d9654d026f66f10cbf81ce9a98baa30bb33510ff19279d90676d'
print(json.dumps({'newScopesNormal':True,'oldThirteenActualArchivesVerified':True,'rawValuesExported':False,'completeSha256':hashlib.sha256((p/'complete.private').read_bytes()).hexdigest(),'archiveInventorySha256':hashlib.sha256((p/'native-before.private.json').read_bytes()).hexdigest(),'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()}))
"""
ssh=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1','sudo -n python3 -B -']
v=subprocess.run(ssh,input=payload.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
proof=json.loads(v.stdout)
manifest={'id':'PG473-stopped-code-only-v1','branch':'dev-foundation','applicationSource':S,'candidateDigest':'ffae42347b43d9654d026f66f10cbf81ce9a98baa30bb33510ff19279d90676d','fullTests':3356,'suites':502,'staticModulesZero':6,'toolTests':{'java':71,'python':153,'term':28,'control':265},'toolAssertionsAreProductionPT':False,'relatedBUG':[],'relatedYKT':[],'PGD':['PG-D378'],'testIds':['PT-OPS-CODE473001','PT-OPS-CODE473002','PT-OPS-CODE473003'],'rootProof':proof,'runs':{},'formalAccepted':False,'globalCoverage100':False,'oldUnknownNormalized':False,'rawLogsInGit':False}
for n in ['pg473-stopped-verify-v1','pg473-stopped-activate-v1']:
 manifest['runs'][n]={'actualExit':int((W/(n+'.exit')).read_text()),'started':(W/(n+'.started')).read_text().strip(),'completed':(W/(n+'.completed')).read_text().strip(),'privateLogSha256':hashlib.sha256((W/(n+'.private.log')).read_bytes()).hexdigest()}
manifest['tools']={n:hashlib.sha256((R/'tools/quality/vm/050_s1'/n).read_bytes()).hexdigest() for n in ['Pg473StoppedDeployment.java','Pg473StoppedDeploymentTest.java','pg473_stopped_native.py','pg473_stopped_native_test.py']}
out=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG473-stopped-code-only-v1/manifest.json'
assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True)
with out.open('x') as f:f.write(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'actualExit':0,'archives13':True,'scopeNormal':True,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'formal':False}))
