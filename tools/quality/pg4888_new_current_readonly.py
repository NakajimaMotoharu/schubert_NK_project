"""Fresh actual04bb full state/capacity; old72 exec remain preservation data only."""
import inspect
import json
import types
import pg4730_new_current_readonly as previous
import pg4886_ssc301_302_publication_post as post

SOURCE,BOM=post.role.SOURCE,post.role.BOM
SLOT='pg4888-new-current-readonly-v1'
AFTER='/var/lib/pgpt-s1-preservation/'+post.SLOT+'/after.private.json'


def context():
    outer=json.loads((post.role.W/post.SLOT/'manifest.safe.json').read_bytes());r=outer.get('result',{})
    if not(type(outer.get('actualExit'))is int and outer['actualExit']==0 and outer.get('source')==SOURCE
           and r.get('productionSource')==SOURCE and r.get('candidateManifestSha256')==BOM
           and r.get('sevenFinitePhasesVerified')is True and r.get('originalBackupNative72Preserved')is True
           and r.get('newSourceParentNotStarted')is True and r.get('newTenReferencesReturnedNormally')is True):
        raise ValueError('actual new source seven-phase/full72 publication first')
    return r['postSha256']


def payload():
    digest=context()
    ns={**vars(previous),'SOURCE':SOURCE,'BOM':BOM,'SLOT':SLOT,'AFTER':AFTER,'AFTER_SHA':digest,'post':post}
    raw=inspect.getsource(previous.payload).replace('pg4706_configuration_capture.py','pg4864_configuration_capture.py').replace('native64Preserved','native72Preserved')
    exec(compile(raw,'<fresh04bb full11/capacity source>','exec'),ns);return ns['payload']()


def main():
    previous.authenticate_host()
    execute=types.FunctionType(previous.transport.execute.__code__,{**vars(previous.transport),'SOURCE':SOURCE})
    return execute(SLOT,payload(),180)


if __name__=='__main__':raise SystemExit(main())
