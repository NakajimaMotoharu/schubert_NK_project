"""Fresh a2ecc full state/capacity; prior80 native are not candidate success."""
import inspect
import json
import types
import pg4730_new_current_readonly as previous
import pg5014_ssc304_publication_post as post
from pg4996_resume_connection import authenticate_host

SOURCE, BOM = post.role.SOURCE, post.role.BOM
SLOT = 'pg5016-new-current-readonly-v1'
AFTER = '/var/lib/pgpt-s1-preservation/' + post.SLOT + '/after.private.json'


def context():
    outer = json.loads((post.role.W / post.SLOT / 'manifest.safe.json').read_bytes())
    r = outer.get('result', {})
    if not (type(outer.get('actualExit')) is int and outer['actualExit'] == 0
            and outer.get('source') == SOURCE and r.get('productionSource') == SOURCE
            and r.get('candidateManifestSha256') == BOM and r.get('sevenFinitePhasesVerified') is True
            and r.get('originalBackupNative80Preserved') is True and r.get('newSourceParentNotStarted') is True
            and r.get('newTenReferencesReturnedNormally') is True):
        raise ValueError('actual new source seven-phase/full80 publication first')
    return r['postSha256']


def payload():
    ns = {**vars(previous), 'SOURCE': SOURCE, 'BOM': BOM, 'SLOT': SLOT,
          'AFTER': AFTER, 'AFTER_SHA': context(), 'post': post}
    raw = inspect.getsource(previous.payload).replace('pg4706_configuration_capture.py', 'pg4986_configuration_capture.py')
    raw = raw.replace('native64Preserved', 'native80Preserved')
    exec(compile(raw, '<fresha2ecc/full80 capacity>', 'exec'), ns)
    return ns['payload']()


def main():
    authenticate_host()
    execute = types.FunctionType(previous.transport.execute.__code__, {**vars(previous.transport), 'SOURCE': SOURCE})
    return execute(SLOT, payload(), 180)


if __name__ == '__main__':
    raise SystemExit(main())
