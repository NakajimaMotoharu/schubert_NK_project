"""Versioned shared roles come from actual hashes, not filename guesses or old success transfer."""
import copy
import unittest
from pyflakes.api import checkPath
import pg5704_historical_failure_comparison as entry


class Roles(unittest.TestCase):
    def test_all_six_canonical_roles_version_and_identical_web_copy(self):
        hashes={m:str(i)*64 for i,m in enumerate(entry.MODULES,1)}
        paths={'protocol':'api/lib/schubert-nk-protocol-0.1.0-SNAPSHOT.jar','storage':'api/lib/schubert-nk-storage-0.1.0-SNAPSHOT.jar',
          'bootstrap':'api/lib/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar','api':'api/api.jar','web':'web/web.jar','batch':'operations/batch.jar'}
        manifest={'artifacts':[{'path':paths[m],'sha256':hashes[m]}for m in entry.MODULES]}
        manifest['artifacts'].append({'path':'web/lib/bootstrap-identical.jar','sha256':hashes['bootstrap']})
        self.assertEqual(paths,entry.resolve_roles(manifest,hashes))
        for mutate in(lambda a:a['artifacts'].pop(0),lambda a:a['artifacts'].append(copy.deepcopy(a['artifacts'][0])),
          lambda a:a['artifacts'][0].update(sha256='f'*64),lambda a:a['artifacts'][0].update(path='api/lib/../../outside.jar')):
            bad=copy.deepcopy(manifest);mutate(bad)
            with self.assertRaises(ValueError):entry.resolve_roles(bad,hashes)
        self.assertEqual(0,checkPath(entry.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
