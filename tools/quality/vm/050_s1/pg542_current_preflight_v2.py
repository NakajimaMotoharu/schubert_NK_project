"""Fresh post-retirement VM diagnosis, no locks/Unit action/DB write/native export."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

os.umask(0o077)
R=Path(__file__).resolve().parent
T=R.parents[3]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
RUN='PG542-current-preflight-v2'
source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()
assert subprocess.check_output(['git','diff','HEAD','--','src','tools','pom.xml'],cwd=T)==b''
assert not subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','src','tools'],cwd=T)
base=R/'pg538_collect_bootstrap_native_v1.py'
raw=base.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='753e590029efb72d5db4ce14b54e402202ff572f3faeec6d7d8b47b570e47a6c'
assign=next(n for n in ast.parse(raw).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name)and t.id=='payload'for t in n.targets))
assert isinstance(assign.value,ast.Constant) and isinstance(assign.value.value,str)
payload=assign.value.value
payload=payload.replace("names={'command','metadata','strict','tree','show'}","names={'command','metadata','strict','tree','show','kernel'}").replace('assert len(nodes)==5','assert len(nodes)==6')
contract=(R/'pg542_current_contract.py').read_text()
extra="""
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
live={u:show(u,FIELDS)for u in UNITS}
assert current_units(live)
for u in UNITS:kernel(u)
"""
# Add the contract only after sealed constants/functions exist. Its UNITS is the same literal set.
anchor="before_raw=strict(root/'before.private.json',0o600,33554432)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,contract+'\n'+extra+'\n'+anchor)
tail="""
current=pathlib.Path('/opt/schubert-nk/current')
assert str(current.readlink())==after['current']=='/opt/schubert-nk/releases/0.1.0-PG495'
manifest=(current/'RELEASE-MANIFEST.json').read_bytes()
assert hashlib.sha256(manifest).hexdigest()=='f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44'
assert json.loads(manifest)['source']['commit']=='a2e98ce9e96c42425921e3686e8ae7a94bff9e6c'
runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf')
m=metadata(runtime)
assert m[2:6]==[0,0,stat.S_IFREG|0o644,1] and m[6]==643 and 'system.posix_acl_access'not in os.listxattr(runtime)
assert hashlib.sha256(runtime.read_bytes()).hexdigest()=='3992c3bcbe97066de238cb97678bb71537643bb598dd5b63a702b15d9e2e44e3'
assert m==metadata(runtime) and {p.name for p in runtime.parent.iterdir()}=={runtime.name}
current_units({u:show(u,FIELDS)for u in UNITS})
for u in UNITS:kernel(u)
print(json.dumps({'actualDeployedSource':'a2e98ce9e96c42425921e3686e8ae7a94bff9e6c',
 'bomSha256':hashlib.sha256(manifest).hexdigest(),'knownRuntimePresent':True,'runtimeSha256':hashlib.sha256(runtime.read_bytes()).hexdigest(),
 'loadedUnitCount':len(live),'allBusinessKernelEmpty':True,'boot':'cc9ed874-7f4f-450e-a188-8de1e42c8441',
 'signatureCryptographicallyReverified':False,'mutationAuthority':False,'actions':0}))
"""
tail=tail.replace("==after['current']=='/opt/schubert-nk/releases/0.1.0-PG495'", "=='/opt/schubert-nk/releases/0.1.0-PG495'")
assert "after['current']" not in tail
payload=payload.replace("before=json.loads(before_raw);after=json.loads(after_raw);assert set(before)==set(after)",
                        "before=json.loads(before_raw);after=json.loads(after_raw);assert set(before)==set(after);assert post_retirement_schema(after)")
payload += tail
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes',
     '-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222',
     'ubuntu@127.0.0.1','sudo -n python3 -B -']
stem=W/RUN.lower();assert not Path(str(stem)+'.private.log').exists()
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
r=subprocess.run(ssh,input=payload.encode(),capture_output=True,timeout=45)
with Path(str(stem)+'.private.log').open('xb')as f:f.write(r.stdout);f.write(r.stderr)
assert r.returncode==0 and not r.stderr
lines=r.stdout.splitlines();assert len(lines)==2
preservation=json.loads(lines[0]);current=json.loads(lines[1])
assert preservation['all24Unchanged'] and preservation['batchRows']==462 and preservation['nativeFiles']==9
assert current['loadedUnitCount']==10 and not current['mutationAuthority']
summary={'run':RUN,'source':source,'startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'actualExit':r.returncode,'preservation':preservation,'current':current,'formalAccepted':False,
         'baseSourceSha256':hashlib.sha256(raw).hexdigest(),'contractSha256':hashlib.sha256(contract.encode()).hexdigest(),
         'helperSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'privateLogSha256':hashlib.sha256(Path(str(stem)+'.private.log').read_bytes()).hexdigest(),
         'sourceUnchanged':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()==source,
         'rawExportedToGit':False,'newStreamExported':False,'unitActions':0,'dbUpdates':0}
assert summary['sourceUnchanged']
with Path(str(stem)+'.safe.json').open('x')as f:json.dump(summary,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'run':RUN,'actualExit':0,'loadedUnitCount':10,'kernelEmpty':True,'rows462Unchanged':True,
                 'native9Unchanged':True,'knownRuntimePresent':True,'authority':False,
                 'safeSha256':hashlib.sha256(Path(str(stem)+'.safe.json').read_bytes()).hexdigest()}))
