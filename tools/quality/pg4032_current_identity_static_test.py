import inspect
import unittest
from pyflakes.api import check
import pg4032_current_identity_static as review


class FreshCurrentTypedIdentity(unittest.TestCase):
    def test_complete_current_typed_payload_and_exact_prior_counts(self):
        raw = '\n'.join(inspect.getsource(fn) for fn in [review.previous.require, review.previous.facts]) + '\n' + review.server_source()
        self.assertEqual(0, check(raw, '<all current65 type/JDK facts>')); compile(raw, '<all current typed positive-conjunct scopes>', 'exec')
        for marker in ['PG4030-current-standalone-static-v1', 'PG3968-literal-invariant-whole-qualified-v1', 'source-full-PG3966', 'new==30', '1394-new', '259+new', "'newSourceRequalifiedScopes':new-28", 'JDK_IDENTITY_CONTRACT_OK']:
            self.assertIn(marker, raw)
        for marker in ['source-full-PG3734', 'management_gate', 'systemctl', "row['disposition']=='UNCLASSIFIED'and", 'PG3744-pmd-contract-classification-v1']:
            self.assertNotIn(marker, raw)
        main = review.main_source(); compile(main, '<complete current typed source emission>', 'exec')
        self.assertIn('server_source() if x is server', main)


if __name__ == '__main__': unittest.main()
