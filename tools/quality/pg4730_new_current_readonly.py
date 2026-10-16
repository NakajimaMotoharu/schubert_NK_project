"""Fresh current825e full state and capacity; no publication/Root/old-session replay."""
import ast
import json
import types
from pyflakes.api import check
from unit_metadata_reference_source import scope
import pg4728_ssc299_publication_post as post
import pg4250_current_admission_image as transport
from pg4434_current_candidate_admission_read import authenticate_host

SOURCE,BOM=post.role.SOURCE,post.role.BOM
SLOT='pg4730-new-current-readonly-v1'
AFTER='/var/lib/pgpt-s1-preservation/pg4728-ssc299-publication-independent-post-v1/after.private.json'
AFTER_SHA='f8dff44c321575ecc5eaa14e76bc9db66bda5850c4d5f81f1d85d4b706a4c601'


def payload():
    proof=json.loads((post.role.W/post.SLOT/'manifest.safe.json').read_bytes())
    if not(type(proof['actualExit'])is int and proof['actualExit']==0
           and proof['source']==SOURCE and proof['result']['postSha256']==AFTER_SHA
           and proof['result']['newSourceParentNotStarted']is True):
        raise ValueError('actual new-current independent publication first')
    raw=post.readonly_source()
    if raw.count(post.FULL_BEFORE)!=1 or raw.count(post.FULL_SHA)!=1:raise ValueError('exact completed full11 before')
    raw=raw.replace(post.FULL_BEFORE,AFTER).replace(post.FULL_SHA,AFTER_SHA)
    last=ast.parse(raw).body[-1]
    if not(isinstance(last,ast.Expr)and ast.unparse(last.value.func)=='print'):raise ValueError('one current reader output')
    raw=''.join(raw.splitlines(keepends=True)[:last.lineno-1]);start=raw.index('units={}')
    capture=post.role.ro.unused.pinned(post.role.W/post.role.ro.unused.TOOLS,'pg4706_configuration_capture.py')
    extra="""
for name,item in expected['unitFilesActual'].items():
 p=Path(name);require(metadata(p)+[hashlib.sha256(p.read_bytes()).hexdigest()]==item)
for unit,oldcfg in expected['configuration'].items():
 r=subprocess.run(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))],capture_output=True,text=True,timeout=10);require(r.returncode==0);require(complete_configuration(r.stdout,unit)==oldcfg)
free=os.statvfs(base).f_bavail*os.statvfs(base).f_frsize;require(free>=12884901888)
"""
    result=raw[:start]+scope(raw[start:]+capture+extra)+"""
print(json.dumps({'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'productionSource':data['source']['commit'],'candidateManifestSha256':sha,'guestBoot':boot,'full11AfterSha256':AFTER_SHA,'guestFreeBytes':free,'all24And32Unchanged':True,'allTenKernelEmpty':True,'allClientAdvisoryFlock0':True,'all187SignatureVerified':True,'native64Preserved':True,'newTenReferencesReturnedNormally':len(refs)==10,'newRootNotStarted':True,'oldNativeCredit':False,'stateChangingActions':0,'formalAccepted':False}))
"""
    if check(result,'<new current fresh full11 and capacity>'):raise ValueError('all actual emitted namespace')
    compile(result,'<fresh new current read only>','exec');return result


def main():
    authenticate_host()
    execute=types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':SOURCE})
    return execute(SLOT,payload(),180)


if __name__=='__main__':raise SystemExit(main())
