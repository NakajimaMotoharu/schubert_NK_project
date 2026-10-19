"""Fresh published0ea full11/capacity; prior94 streams are preserved data only."""
import inspect
import json
import types
import pg4730_new_current_readonly as previous
import pg5630_current_publication_post as post
from pg4996_resume_connection import authenticate_host

SOURCE,BOM=post.role.SOURCE,post.role.BOM
SLOT='pg5632-new-current-readonly-v1'
AFTER='/var/lib/pgpt-s1-preservation/'+post.SLOT+'/after.private.json'


def context():
    outer=json.loads((post.role.W/post.SLOT/'manifest.safe.json').read_bytes());r=outer.get('result',{})
    if not(type(outer.get('actualExit'))is int and outer['actualExit']==0 and outer.get('source')==SOURCE
      and r.get('productionSource')==SOURCE and r.get('candidateManifestSha256')==BOM
      and r.get('sevenFinitePhasesVerified')is True and r.get('originalBackupNative94Preserved')is True
      and r.get('newSourceParentNotStarted')is True and r.get('newTenReferencesReturnedNormally')is True):
        raise ValueError('actual same0ea seven-phase/full94 publication post first')
    return r['postSha256']


def payload():
    ns={**vars(previous),'SOURCE':SOURCE,'BOM':BOM,'SLOT':SLOT,'AFTER':AFTER,'AFTER_SHA':context(),'post':post}
    raw=inspect.getsource(previous.payload).replace('pg4706_configuration_capture.py','pg5608_configuration_capture.py').replace('native64Preserved','native94Preserved')
    exec(compile(raw,'<fresh0ea full11/current capacity>','exec'),ns)
    return ns['payload']()


def main():
    authenticate_host();transport=previous.transport
    return types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':SOURCE})(SLOT,payload(),180)


if __name__=='__main__':raise SystemExit(main())
