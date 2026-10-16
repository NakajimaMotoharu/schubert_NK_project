"""All seven finite phases and new signed current, retaining old data/native only."""
import ast
import inspect
import json
import types
from pyflakes.api import check
from unit_metadata_reference_source import scope
import pg3752_current_preservation_readonly as base_reader
import pg3794_hygiene_publication_post as old
import pg4722_ssc299_publication_sources as role
import pg4250_current_admission_image as transport
from pg4434_current_candidate_admission_read import authenticate_host

SLOT='pg4728-ssc299-publication-independent-post-v1'
FULL_BEFORE='/var/lib/pgpt-s1-preservation/pg4704-current-preservation-readonly-v1/sealed-with-native.private.json'
FULL_SHA='5f4800ac6bb4e957db4dde31e60448433dece666788669fb6911ecca1a0615b3'


def readonly_source():
    raw=base_reader.payload()
    prior=json.loads((role.W/'pg3668-current-browser-runtime-retirement-post-v1/manifest.safe.json').read_bytes())
    changes={base_reader.CURRENT:role.SOURCE,base_reader.BOM:role.BOM,'PG3420':'PG4702',
             'pg3420-manifest.sig':'pg4702-manifest.sig',
             "base/'pg3662-native-stop-v1/after.private.json'":'Path('+repr(FULL_BEFORE)+')',
             prior['proofHashes']['after.private.json']['sha256']:FULL_SHA,
             "==34)":"==64)",'native34Preserved':'native64Preserved'}
    # Exact fixed role literals only. No old source/tuple/data payload is rewritten.
    for before,after in changes.items():
        if before not in raw:raise ValueError('one actual new-current reader boundary '+before)
        raw=raw.replace(before,after)
    return raw


def publication():
    ns={**vars(old),'role':role}
    raw=inspect.getsource(old.publication).replace('pg3788_ordinary_publication_contract','pg4722_ordinary_publication_contract')
    exec(compile(raw,'<independent every finite phase oracle>','exec'),ns)
    return ns['publication']()


def payload():
    fixed=json.loads((role.W/'pg4724-frozen-v1.safe.json').read_bytes())
    if type(fixed['actualExit'])is not int or fixed['actualExit']!=0:raise ValueError('actual complete finite publication ABI first')
    raw=readonly_source();tree=ast.parse(raw);last=tree.body[-1]
    if not(isinstance(last,ast.Expr)and isinstance(last.value,ast.Call)and ast.unparse(last.value.func)=='print'):
        raise ValueError('one final full current reader boundary')
    raw=''.join(raw.splitlines(keepends=True)[:last.lineno-1]);start=raw.index('units={}')
    capture=role.ro.unused.pinned(role.W/role.ro.unused.TOOLS,'pg4706_configuration_capture.py')
    extra="\nfor name,item in expected['unitFilesActual'].items():\n p=Path(name);require(metadata(p)+[hashlib.sha256(p.read_bytes()).hexdigest()]==item)\nfor unit,oldcfg in expected['configuration'].items():\n r=subprocess.run(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))],capture_output=True,text=True,timeout=10);require(r.returncode==0);require(complete_configuration(r.stdout,unit)==oldcfg)\n"
    body=raw[start:]+capture+extra
    marker=";require(r.returncode==0 and len(r.stdout)<67108864);tables={};meta={}"
    if body.count(marker)!=1:raise ValueError('one SQL-return-before-parse boundary')
    preserve="""
 index=1+len(list(EVIDENCE.glob('sql-read-*.safe.json')))
 require(len(r.stdout)<67108864 and len(r.stderr)<1048576)
 for label,value in [('stdout',r.stdout),('stderr',r.stderr)]:
  with(EVIDENCE/('sql-read-'+str(index)+'.'+label+'.private')).open('xb')as handle:
   os.fchmod(handle.fileno(),0o600);handle.write(value);handle.flush();os.fsync(handle.fileno())
 with(EVIDENCE/('sql-read-'+str(index)+'.safe.json')).open('x')as handle:
  json.dump({'actualExit':r.returncode,'stdoutSha256':hashlib.sha256(r.stdout).hexdigest(),'stderrSha256':hashlib.sha256(r.stderr).hexdigest()},handle,sort_keys=True);handle.flush();os.fsync(handle.fileno())
 fd=os.open(EVIDENCE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
 require(r.returncode==0);tables={};meta={}
"""
    body=body.replace(marker,preserve,1)
    evidence="\nEVIDENCE=base/"+repr(SLOT)+"\nrequire(not os.path.lexists(EVIDENCE));EVIDENCE.mkdir(mode=0o700)\n"
    result='PUBLICATION_FILES='+repr(fixed['fileHashes'])+'\n'+raw[:start]+old.HELPERS+evidence+publication()+scope(body)
    result+="""
save=EVIDENCE
encoded=json.dumps(expected,sort_keys=True).encode()
with(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for directory in [save,save.parent]:
 fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'productionSource':data['source']['commit'],'candidateSource':data['source']['commit'],'candidateManifestSha256':sha,'postSha256':hashlib.sha256(encoded).hexdigest(),'sevenFinitePhasesVerified':True,'all24And32Unchanged':True,'whole187SignedArtifactBytesVerified':True,'allTenKernelEmpty':True,'allClientAdvisoryFlock0':True,'originalBackupNative64Preserved':True,'canonicalInvalidEpochApprovalCurrentAndOldLinkVerified':True,'unitBytesInodesConfigurationUnchanged':True,'newTenReferencesReturnedNormally':len(refs)==10,'unitExchangeAndReload':False,'newSourceParentNotStarted':True,'oldNativeNotAppliedToNewSource':True,'formalAccepted':False}))
"""
    if check(result,'<all finite phases and current full preservation>'):raise ValueError('all standalone globals required')
    compile(result,'<full independent finite publication post>','exec')
    return result


def main():
    actual=json.loads((role.W/'pg4726-activate-v1.safe.json').read_bytes())
    if not(type(actual.get('actualExit'))is int and actual['actualExit']==0
           and actual.get('sourceQualified')is True and actual.get('candidateSource')==role.SOURCE
           and actual.get('currentApprovalEpochChanged')is True):raise ValueError('genuine original finite publication first')
    authenticate_host()
    execute=types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':role.SOURCE})
    return execute(SLOT,payload(),180)


if __name__=='__main__':raise SystemExit(main())
