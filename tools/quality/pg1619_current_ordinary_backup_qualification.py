"""Current new-run Backup independent bytes/SQL/config/restore-list qualification.

No new Backup or restore. Full current post is rechecked under fresh ten Ref;
the removed older generation's private-byte proof is explicitly separate.
"""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from pathlib import Path
from pg1446_current_cold_stage import W,SSH
from pg1609_current_ordinary_owned_stop_sources import SOURCE,TOOLS
from pg1613_current_ordinary_stop_independent_post import payload as whole_post
import pg1262_fresh_backup_independent_capture_v2 as backup

SLOT='pg1619-current-ordinary-backup-qualified-v1'

def payload():
    post=json.loads((W/'pg1613-current-ordinary-terminal-post-v1.safe.json').read_bytes())
    if post['actualExit']!=0 or post['productionSource']!=SOURCE or not post['allClientAdvisoryFlock0']:raise ValueError('actual current normal whole post required')
    seals={n:post['proofHashes'][n]['sha256']for n in ['before.private.json','after.private.json','complete.private','parent.private.jsonl']}
    raw=whole_post(seals);raw=raw[:raw.index("result={'actualExit':0")]
    helper=(Path(__file__).parent/'vm/050_s1/pg480_backup_refs.py').read_bytes()
    if hashlib.sha256(helper).hexdigest()!='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7':raise ValueError('qualified metadata primitive source pin refused')
    tree=ast.parse(helper);names={'command','metadata','strict','show','tree','configuration_fields','kernel'}
    constants=[n for n in tree.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
    if len(constants)!=2 or len(nodes)!=7:raise ValueError('qualified metadata primitive declaration closure refused')
    begin=raw.index(";parsed=ast.parse(raw)");end=raw.index("exec(compile(ast.Module(body=constants+nodes,type_ignores=[]),'<sealed terminal metadata>','exec'),globals())")
    raw=raw[:begin]+'\n'+ast.unparse(ast.Module(body=constants+nodes,type_ignores=[]))+raw[end+len("exec(compile(ast.Module(body=constants+nodes,type_ignores=[]),'<sealed terminal metadata>','exec'),globals())"):]
    raw=raw.replace('import ast,datetime,dbus,hashlib,json,os,pathlib,re,stat,subprocess,sys,time','import ast,datetime,dbus,hashlib,json,os,pathlib,re,stat,subprocess')
    # Only the already-qualified independent manifest/config reader is reused.
    # Its old full-post precondition/old operation authority is not executed.
    extra=backup.payload(backup.SEALS);extra=extra[extra.index('\nORACLE_SOURCE='):]
    extra=extra[:extra.index("save=base/'pg1262-fresh-backup-independent-v2'")]
    # CONFIG_SOURCE is injected separately before the independent reader.
    config_source=inspect.getsource(backup.config_contract)
    extra='CONFIG_SOURCE='+repr(config_source)+'\n'+extra
    old="directory=pathlib.Path('/srv/schubert-nk/backup/20261011-050327-9f651096-aef9-4fba-90b0-a653e99f035a')"
    new="folders=[pathlib.Path(p)for p in after['backup']if p.endswith('-0be226b1-bbb7-43d3-aa9e-59d0bda70f9a')];require(len(folders)==1);directory=folders[0]"
    if extra.count(old)!=1:raise ValueError('current run Backup directory selection boundary refused')
    extra=extra.replace(old,new).replace('9f651096-aef9-4fba-90b0-a653e99f035a','0be226b1-bbb7-43d3-aa9e-59d0bda70f9a').replace('2026-10-10T20:03:22.718197Z','2026-10-12T06:23:13.176261Z')
    function='def qualify_backup():\n'+'\n'.join(' '+line for line in extra.splitlines())+'\n return first,listing.stdout\n'
    marker="\nbus=dbus.SystemBus(private=True)"
    if raw.count(marker)!=1:raise ValueError('fresh current Ref lifecycle insertion refused')
    raw=raw.replace(marker,'\n'+function+'\n'+marker)
    marker='native=snapshot();require(native==snapshot())'
    if raw.count(marker)!=1:raise ValueError('complete current Ref scope backup insertion refused')
    raw=raw.replace(marker,'native=snapshot();backup_result,listing_bytes=qualify_backup();require(native==snapshot())')
    raw='HASHES='+repr(post['toolHashes'])+'\nRECEIPT='+repr((W/TOOLS/'pg1609_parent_receipt.py').read_text())+'\n'+raw+'\n'+SAVE
    compile(raw,'<current independent Backup full private qualification>','exec');return raw

SAVE=r'''
save=base/'pg1619-current-ordinary-backup-qualified-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
with(save/'dump-list.private').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(listing_bytes);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'productionSource':data['source']['commit'],'independentBackupManifest':backup_result[0],'physicalConfigSummary':backup_result[1],'ordinaryPgRestoreListExit':0,'dumpListSha256':hashlib.sha256(listing_bytes).hexdigest(),'same24Full32Signed187OriginalNativeResourcesPreserved':True,'normalFreshMetadataScopes':True,'startsStopsReloadsSqlWrites0':True,'retiredOlderGenerationPrivateBytesQualificationPending':True,'formalAccepted':False}))
'''

def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean current operator required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode()
    (out/'payload.private.py').write_bytes(raw)
    from pyflakes.api import check
    if check(raw.decode(),'<actual current Backup qualification>'):raise ValueError('actual complete generated static gate refused')
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr)
    safe={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'formalAccepted':False}
    if r.returncode==0:safe.update(json.loads(r.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return r.returncode

if __name__=='__main__':raise SystemExit(main())
