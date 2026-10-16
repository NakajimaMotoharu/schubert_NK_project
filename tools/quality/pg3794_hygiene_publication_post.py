"""Independent seven-phase publication and all original-data/resource post, no Root start."""
import ast
import hashlib
import inspect
import json
from pyflakes.api import check
from pg1696_completed_publication_independent_post import PUBLIC_AFTER
from unit_metadata_reference_source import scope
import pg3752_current_preservation_readonly as readonly
import pg3786_hygiene_ro_post as transport
import pg3788_hygiene_publication_sources as role

SLOT='pg3794-hygiene-publication-independent-post-v1'
HELPERS=r'''
import pathlib,re
def metadata9(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def strict(path,mode,bound):
 s=path.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,mode,1)and not os.listxattr(path)and s.st_size<=bound)
 value=path.read_bytes();require(len(value)==s.st_size and metadata9(path.lstat())==metadata9(s));return value
after={k:v for k,v in expected.items()if k!='native'}
require(len(after)==10)
'''


def publication():
    raw=PUBLIC_AFTER
    for a,b in [('pg1694-completed-ordinary-publication-v1',role.SAVE),('pg1691-completed-publication-tools-v1',role.TOOLS),('pg1691_ordinary_publication_contract','pg3788_ordinary_publication_contract'),('9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37',role.BEFORE),('genuineParentDone=true\\n','genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true\\n')]:raw=raw.replace(a,b)
    marker="oracle['verify'](public_first,public_last,'release',expected_epoch,lower,upper)"
    if raw.count(marker)!=1:raise ValueError('independent every-phase oracle required')
    raw=raw.replace(marker,"require(len(phases)>=7 and len({stamp for stamp,phase,observed in phases})==len(phases))\nrequire(tuple(dict.fromkeys(phase for stamp,phase,observed in phases))==oracle['PHASES'])\nfor stamp,phase,observed in phases:oracle['verify'](public_first,observed,phase,expected_epoch,lower,upper)")
    raw=raw.replace('after=json.loads(published_raw)','after=json.loads(published_raw)\nrequire(json.loads(pub_before)==old_after)')
    return raw+"\nexpected={**expected,'startup':after['startup']}\nrequire(not(publication/'daemon-reload-reserved.private').exists()and not(publication/'morning-unit-old.private').exists())\n"


def payload():
    fixed=json.loads((role.W/'pg3790-frozen-v1.safe.json').read_bytes())
    if fixed['actualExit']!=0:raise ValueError('genuine fixed publication ABI required')
    raw=readonly.payload()
    for a,b in [(readonly.CURRENT,role.SOURCE),(readonly.BOM,role.BOM),('PG3420','PG3748'),('pg3420-manifest.sig','pg3748-manifest.sig')]:raw=raw.replace(a,b)
    tree=ast.parse(raw);last=tree.body[-1]
    if not isinstance(last,ast.Expr)or not isinstance(last.value,ast.Call)or not isinstance(last.value.func,ast.Name)or last.value.func.id!='print':raise ValueError('one final full reader boundary required')
    raw=''.join(raw.splitlines(keepends=True)[:last.lineno-1])
    start=raw.index('units={}')
    capture=role.ro.mapping.pinned(role.W/role.ro.unused.TOOLS,'pg3766_configuration_capture.py')
    extra="\nfor name,item in expected['unitFilesActual'].items():\n p=Path(name);require(metadata(p)+[hashlib.sha256(p.read_bytes()).hexdigest()]==item)\nfor unit,oldcfg in expected['configuration'].items():\n r=subprocess.run(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))],capture_output=True,text=True,timeout=10);require(r.returncode==0);require(complete_configuration(r.stdout,unit)==oldcfg)\n"
    body=raw[start:]+capture+extra
    result='PUBLICATION_FILES='+repr(fixed['fileHashes'])+'\n'+raw[:start]+HELPERS+publication()+scope(body)
    result+="""
save=base/'pg3794-hygiene-publication-independent-post-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
encoded=json.dumps(expected,sort_keys=True).encode()
with(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for directory in [save,save.parent]:
 fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'productionSource':data['source']['commit'],'candidateSource':data['source']['commit'],'candidateManifestSha256':sha,'postSha256':hashlib.sha256(encoded).hexdigest(),'sevenFinitePhasesVerified':True,'all24And32Unchanged':True,'whole187SignedArtifactBytesVerified':True,'allTenKernelEmpty':True,'allClientAdvisoryFlock0':True,'originalBackupNative34Preserved':True,'canonicalInvalidEpochApprovalCurrentAndOldLinkVerified':True,'unitBytesInodesConfigurationUnchanged':True,'newTenReferencesReturnedNormally':len(refs)==10,'unitExchangeAndReload':False,'newSourceParentNotStarted':True,'oldNativeNotAppliedToNewSource':True,'formalAccepted':False}))
"""
    if check(result,'<all independent seven-phase full publication post>'):raise ValueError('whole independent namespace required')
    compile(result,'<publication all24/config32/187/native34/finite sevenphase>','exec');return result


def main():
    raw=inspect.getsource(transport.main).replace('pg3784-prepare-ro-v1.safe.json','pg3792-activate-v1.safe.json')
    raw=raw.replace("actual.get('currentApprovalEpochChanged')is not False","actual.get('currentApprovalEpochChanged')is not True")
    namespace={**transport.__dict__,'role':role,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<separate publication post observer>','exec'),namespace);return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
