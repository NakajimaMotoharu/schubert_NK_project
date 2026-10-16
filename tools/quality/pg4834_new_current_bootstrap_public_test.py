import ast
import unittest
import pg4834_new_current_bootstrap_public as role


class ExactProjection(unittest.TestCase):
    def test_measured_ten_twelve_not_acceptance(self):
        raw=role.source();ast.parse(raw)
        for value in ("n['currentNativeStreams'] == 10","n['validatedNativePoints'] == 12",'3739','549','1646',"'PMDRaw': 1654","'CheckstyleRaw': 0","'acceptedLeafDelta': 0","'effortPercent': None","'formalAccepted': False","'currentSourceCriteriaRevalidationPending': True"):
            self.assertIn(value,raw)
        self.assertNotIn('PG4782-native',raw)
        self.assertIn('PG4832-native-v1',raw)


if __name__=='__main__':unittest.main()
