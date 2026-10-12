"""Fresh closed Root13 WARNING before sealed candidate maintenance; no mutation authority."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pathlib import Path
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1838_warning_terminal_independent_post import payload as previous,SEALS
from pg1833_readonly_parent_state_sources import SOURCE,TOOLS

SLOT='pg1849-warning-completed-current-before-v1'


def payload(post):
    seals={n:post['proofHashes'][n]['sha256']for n in SEALS}
    raw=previous(seals)
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='result'for t in n.targets))
    raw=''.join(raw.splitlines(keepends=True)[:node.lineno-1])+'''
save=base/'pg1849-warning-completed-current-before-v1'
require(not os.path.lexists(save));save.mkdir(mode=0o700)
actual=json.dumps(after,sort_keys=True).encode()
native_raw=json.dumps(native,sort_keys=True).encode()
for name,body in [('before.private.json',actual),('native-before.private.json',native_raw)]:
 with(save/name).open('xb')as f:
  os.fchmod(f.fileno(),0o600);f.write(body);f.flush();os.fsync(f.fileno())
for path in [save,save.parent]:
 fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
print(json.dumps({'actualExit':0,'productionSource':data['source']['commit'],'privateBeforeSha256':hashlib.sha256(actual).hexdigest(),'nativeBeforeSha256':hashlib.sha256(native_raw).hexdigest(),'genuineCompletion':summary,'all24UnchangedTwice':True,'allTenUnitsKernelEmpty':True,'allActorGone':True,'allClientAdvisoryFlock0':True,'whole187SignedArtifactBytesVerified':True,'nativeFiles':sum(p.endswith('.exec')for p in native),'normalFreshReadonlyScopes':True,'startsStopsReloadsSqlWrites0':True,'rawExported':False,'formalAccepted':False}))
'''
    helper=(Path(__file__).parent/'vm/050_s1/pg480_backup_refs.py').read_bytes()
    if hashlib.sha256(helper).hexdigest()!='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7':raise ValueError('fixed independent readonly primitive bytes required')
    tree=ast.parse(helper);names={'command','metadata','strict','show','tree','configuration_fields','kernel'}
    definitions=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
    constants=[n for n in tree.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
    if len(definitions)!=7 or len(constants)!=2:raise ValueError('exact readonly declaration set required')
    calls=[n for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='exec'and any(isinstance(c,ast.Constant)and c.value=='<sealed terminal metadata>'for c in ast.walk(n))]
    if len(calls)!=1:raise ValueError('one dynamic sealed primitive boundary required')
    raw=raw.replace(ast.get_source_segment(raw,calls[0]),ast.unparse(ast.Module(body=constants+definitions,type_ignores=[])),1)
    raw=raw.replace('subprocess, sys, time','subprocess')
    fixed=json.loads((W/'pg1834-frozen-v1.safe.json').read_bytes())
    receipt=(W/TOOLS/'pg1833_parent_receipt.py').read_text()
    return 'HASHES='+repr(fixed['fileHashes'])+'\nRECEIPT='+repr(receipt)+'\n'+raw


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean source required')
    post=json.loads((W/'pg1838-warning-terminal-independent-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or post['productionSource']!=SOURCE or post['allClientAdvisoryFlock0']is not True:raise ValueError('real closed current root required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload(post)
    (out/'payload.private.py').write_text(raw);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:result.update(json.loads(r.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
