import ast
import unittest
from pg1171_wrong_runtime_post import payload


class RuntimePostTest(unittest.TestCase):
    def test_fixed_retirement_proofs_and_all_data_resource_post(self):
        s=payload();ast.parse(s)
        for part in ['989635f8087b6c99dc950517566728b9a7a00cf37fed31d03451ac6089c88d70','sameEmptyRuntimeDirectory755','oldBad647BytesPrivatelyPreserved','allPeersAdvisoryM_A0','observed==post()','metadataReferencesNormalClose']:
            self.assertTrue(part in s,part)
        for part in ['pidfd_send_signal','systemctl start','systemctl stop','daemon-reload']:
            self.assertFalse(part in s,part)


if __name__=='__main__':unittest.main()
