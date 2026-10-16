"""SSC300 current stopped-data enriched Bootstrap baseline, no credential or start authority."""
import ast
import hashlib
import json
from pathlib import Path
from pyflakes.api import check
import pg1718_current_bootstrap_before as old
import pg4778_new_current_owned_post as post
import pg4752_new_current_admission_image as admission

SLOT='pg4818-new-current-bootstrap-before-v1'
SOURCE,BOM=admission.SOURCE,admission.BOM
AFTER='b4f07e80538b7eab36e1ba87523097891252e5f14f9f1d86ad8106c753c740c3'


def payload():
    manifest=json.loads((admission.W/post.SLOT/'manifest.safe.json').read_bytes())
    original=(admission.W/post.SLOT/'payload.private.py').read_bytes()
    if not(type(manifest['actualExit'])is int and manifest['actualExit']==0 and manifest['productionSource']==SOURCE and manifest['all24UnchangedTwice']and manifest['allClientAdvisoryFlock0']and manifest['allTenUnitsKernelEmpty']and manifest['nativePhysicalFiles']==70 and manifest['proofHashes']['after.private.json']['sha256']==AFTER and hashlib.sha256(original).hexdigest()==manifest['payloadSha256']):raise ValueError('exact actual stopped all24/70/current source proof first')
    raw=original.decode();tree=ast.parse(raw)
    assignments=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='save'for t in n.targets)]
    if len(assignments)!=1:raise ValueError('one output namespace')
    n=assignments[0]
    if ast.unparse(n.value)!="base / 'pg4778-new-current-owned-post-v1'":raise ValueError('exact old evidence output')
    raw=raw.replace(ast.get_source_segment(raw,n),"save=base/"+repr(SLOT),1)
    boundary="result={'actualExit':0"
    # Preserve the actual full post validation, cut only the outgoing result.
    variants=[i for i,s in enumerate(raw.splitlines())if s.lstrip().startswith('result =')or s.lstrip().startswith(boundary)]
    if len(variants)!=1:raise ValueError('one final result')
    lines=raw.splitlines();raw='\n'.join(lines[:variants[0]])+'\n'
    graph=(Path(old.__file__).parent/'vm/050_s1/pg529_dependency_graph.py').read_text().replace('import re\n','')
    buses=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='bus'for t in n.targets)]
    if len(buses)!=1:raise ValueError('one actual top-level metadata owner construction')
    lines=raw.splitlines(keepends=True);lines.insert(buses[0].lineno-1,graph+'\n');raw=''.join(lines)
    line='    require(native == snapshot())';indent='    '
    if raw.count(line)!=1:raise ValueError('one actually held tenRef native boundary')
    extra=old.EXTRA.replace('pg1718-current-bootstrap-before-v1',SLOT)
    role_check=r'''
import pwd,grp
coverage=pathlib.Path('/run/schubert-nk/pt-coverage');role=coverage/'ordinary-bootstrap196'
require({p.name for p in coverage.iterdir()if p.is_dir()}=={'backup','cleanup','expiry','inspector','ordinary-api193','ordinary-bootstrap196','ordinary-inspector196','ordinary-web193','parent','root-api','root-api193','root-web193'})
s=role.lstat();identity=pwd.getpwnam('schubert-api');group=grp.getgrnam('schubert-api')
require((identity.pw_uid,identity.pw_gid,group.gr_gid)==(999,981,981))
require(stat.S_ISDIR(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(999,981,0o700)and not os.listxattr(role))
fs=subprocess.run(['findmnt','-T',str(role),'-n','-o','FSTYPE,OPTIONS'],capture_output=True,text=True,timeout=5);require(fs.returncode==0)
parts=fs.stdout.strip().split();require(len(parts)==2 and parts[0]=='tmpfs'and 'rw'in parts[1].split(',')and 'ro'not in parts[1].split(','))
require(role.as_posix()in json.dumps(after['configuration']['schubert-nk-bootstrap-admin.service']))
'''
    extra=role_check+extra
    raw=raw.replace(line,line+'\n'+'\n'.join(indent+s if s else ''for s in extra.splitlines()),1)
    raw+="\nprint(json.dumps({'actualExit':0,'productionSource':SOURCE,'beforeSha256':hashlib.sha256(snapshot_raw).hexdigest(),'whole24Full32Signed187AndResourcesUnchanged':True,'existingSingleAdminVerified':True,'bootstrapCredentialsAbsent':True,'emptyFourNamespacesVerified':True,'batchRows':len(value['rows']['schubert.batch_runs']),'nativePhysicalFiles':len([p for p in native if p.endswith('.exec')]),'normalNewReferences':True,'startsStopsWrites0':True,'formalAccepted':False}))\n"
    raw='SOURCE='+repr(SOURCE)+'\nBOM='+repr(BOM)+'\n'+raw
    if check(raw,'<complete current stopped enriched Bootstrap before>'):raise ValueError('complete emitted namespace')
    compile(raw,'<read-only existing ADMIN/current all24 before>','exec');return raw


if __name__=='__main__':raise SystemExit(admission.execute(SLOT,payload(),120))
