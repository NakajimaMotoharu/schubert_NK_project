import inspect
import unittest
from pyflakes.api import check
import pg2654_operation_post_signed_candidate as candidate


class ResourceSignedCandidate(unittest.TestCase):
    def test_exact_host_only_source_and_resource_count(self):
        raw=candidate.main_source()
        ns={**candidate.prior.__dict__,'qualify_source':None}
        supplied='\n'.join(k+'=None'for k in ns if k.isidentifier()and k!='main')
        self.assertEqual(0,check(supplied+'\n'+raw,'<whole host signing namespace>'))
        for marker in ['pg2651-operation-post-full-qualified-v1','PG2654','3666','541',"'addedResources':1",'qualify_source()']:
            self.assertIn(marker,raw)
        self.assertNotIn('daemon-reload',raw)
        self.assertIn('verify_added_web',inspect.getsource(candidate.receive))


if __name__=='__main__':unittest.main()
