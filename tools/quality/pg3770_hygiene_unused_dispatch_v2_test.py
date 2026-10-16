import inspect
import json
import unittest
import pg3770_hygiene_unused_dispatch_v2 as c
import pg3772_hygiene_unused_post_v2 as post


class V2(unittest.TestCase):
    def test_new_reservations_and_exact_source_current_before_without_replaying_failed_v1(self):
        raw=c.source()
        for s in ['pg3768-frozen-v1','pg3770-stage-v1.exit',c.role.ARCHIVE,'pg3748-manifest-v1.sig','reserved actual action must not be replayed','pg3754-current-before-view-v1']:self.assertIn(s,raw)
        for s in ['pg3760-place-v1','pg3758-frozen','pg3756-hygiene-unused-tools-v1']:self.assertNotIn(s,raw+c.STAGE)
        ns=c.runtime_namespace(json.loads((c.W/'pg3748-candidate-build-v1.safe.json').read_bytes()),c.before_record());self.assertEqual(c.GUEST,ns['GUEST']);self.assertEqual(c.compiler.TARGET,ns['TARGET'])
        observed=c.role.bind(inspect.getsource(post.previous.main));self.assertIn('pg3770-place-v1.safe.json',observed);self.assertNotIn('pg3760-place-v1',observed)
        payload=post.previous.payload();compile(payload,'<independent unchanged current/candidate full post>','exec')


if __name__=='__main__':unittest.main()
