"""Fresh enriched2741 whole post before existing-only Bootstrap; readonly only."""
import hashlib
import ast
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1707_new_source_stop_independent_post import payload as whole_post
from pg1703_new_source_owned_stop_sources import SOURCE,TOOLS
from pg1700_new_source_live_binding import DIGEST

SLOT='pg1718-current-bootstrap-before-v1'
EXTRA=r'''
dependency_fields={'Requires','Before','After','PartOf','BindsTo'}
def deps():
 result={}
 for u in UNITS:
  raw=subprocess.check_output(['/usr/bin/systemctl','show',u,'--property='+','.join(sorted(dependency_fields))],timeout=5,text=True)
  values=dict(line.split('=',1)for line in raw.splitlines());require(set(values)==dependency_fields);result[u]=values
 return result
raw_dependencies=deps();graph=dependency_graph(raw_dependencies,UNITS)
paths={name:pathlib.Path('/run/schubert-nk')/name for name in ('backup-request','cleanup-request','expiry-request')}
paths['runtime-parent']=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')
namespace={name:{'metadata':metadata(p),'entries':sorted(q.name for q in p.iterdir()),'xattrs':os.listxattr(p)}for name,p in paths.items()}
require(all(p.is_dir()and not p.is_symlink()and not namespace[n]['entries']and not namespace[n]['xattrs']for n,p in paths.items()))
require(not any(os.path.lexists('/etc/schubert-nk/credentials/'+n)for n in ('bootstrap-admin-username','bootstrap-admin-password')))
users=after['rows']['schubert.app_users'];require(len(users)==1 and users[0]['role']=='ADMIN')
value={**after,'dependencies':graph,'namespace':namespace,'credentials':tree(pathlib.Path('/etc/schubert-nk/credentials')),'parentPid1':after['pid1'],'native':native,'oldProofs':tree(root),'source':SOURCE,'manifestSha256':BOM}
require(value['credentials']==after['extraDurable']['credentials']and raw_dependencies==deps()and native==snapshot())
save=base/'pg1718-current-bootstrap-before-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
snapshot_raw=json.dumps(value,sort_keys=True).encode()
with(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(snapshot_raw);f.flush();os.fsync(f.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
'''


def payload():
    post=json.loads((W/'pg1707-new-source-terminal-post-v1.safe.json').read_bytes())
    if post.get('actualExit')!=0 or post.get('productionSource')!=SOURCE or post.get('allClientAdvisoryFlock0')is not True:
        raise ValueError('current whole independent post required')
    seals={n:post['proofHashes'][n]['sha256']for n in ['before.private.json','after.private.json','complete.private','parent.private.jsonl']}
    raw=whole_post(seals);raw=raw[:raw.index("result={'actualExit':0")]
    helper=(Path(__file__).parent/'vm/050_s1/pg480_backup_refs.py').read_bytes()
    if hashlib.sha256(helper).hexdigest()!='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7':
        raise ValueError('fixed metadata source pin refused')
    parsed=ast.parse(helper);names={'command','metadata','strict','show','tree','configuration_fields','kernel'}
    nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in names]
    constants=[n for n in parsed.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
    if len(nodes)!=7 or len(constants)!=2:raise ValueError('whole primitive definition closure required')
    begin=raw.index(';parsed=ast.parse(raw)')
    boundary="exec(compile(ast.Module(body=constants+nodes,type_ignores=[]),'<sealed terminal metadata>','exec'),globals())"
    end=raw.index(boundary,begin)
    raw=raw[:begin]+'\n'+ast.unparse(ast.Module(body=constants+nodes,type_ignores=[]))+raw[end+len(boundary):]
    raw=raw.replace('import ast,datetime,dbus,hashlib,json,os,pathlib,re,stat,subprocess,sys,time',
                    'import ast,datetime,dbus,hashlib,json,os,pathlib,re,stat,subprocess')
    graph=(Path(__file__).parent/'vm/050_s1/pg529_dependency_graph.py').read_text().replace('import re\n','')
    raw=raw.replace('bus=dbus.SystemBus(private=True);',graph+'\nbus=dbus.SystemBus(private=True);')
    marker=' native=snapshot();require(native==snapshot())'
    if raw.count(marker)!=1:raise ValueError('one enriched current Ref scope required')
    raw=raw.replace(marker,marker+'\n'+'\n'.join(' '+line if line else line for line in EXTRA.splitlines()))
    raw='SOURCE='+repr(SOURCE)+'\nBOM='+repr(DIGEST)+'\nHASHES='+repr(post['toolHashes'])+'\nRECEIPT='+repr((W/TOOLS/'pg1703_parent_receipt.py').read_text())+'\n'+raw
    raw+="\nprint(json.dumps({'actualExit':0,'productionSource':SOURCE,'beforeSha256':hashlib.sha256(snapshot_raw).hexdigest(),'whole24Full32Signed187AndResourcesUnchanged':True,'existingSingleAdminVerified':True,'bootstrapCredentialsAbsent':True,'emptyFourNamespacesVerified':True,'batchRows':len(value['rows']['schubert.batch_runs']),'normalNewReferences':True,'startsStopsWrites0':True,'formalAccepted':False}))\n"
    from pyflakes.api import check
    if check(raw,'<actual current enriched Bootstrap before>'):raise ValueError('generated static closure refused')
    compile(raw,'<current existingADMIN whole baseline>','exec')
    return raw


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean frozen operator required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode()
    (out/'payload.private.py').write_bytes(raw)
    result=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(result.stderr)
    safe={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False}
    if result.returncode==0:safe.update(json.loads(result.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return result.returncode


if __name__=='__main__':raise SystemExit(main())
