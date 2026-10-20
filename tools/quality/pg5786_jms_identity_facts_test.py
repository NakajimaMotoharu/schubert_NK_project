"""Existing correct tool paths inherited, no compilation, network or job action."""
import unittest
from unittest.mock import patch
import pg5786_jms_identity_facts as p


class ScopeContract(unittest.TestCase):
    def test_correct_bin_and_only_declared_namespace_overrides(self):
        scope=p.namespace();self.assertEqual(p.previous.JDK,scope['JDK']);self.assertEqual(p.TC/'jdk-25.0.4/bin',scope['JDK']);self.assertEqual(p.SOURCE,scope['SOURCE']);self.assertIs(p.inputs,scope['inputs']);self.assertTrue(scope['SLOT'].endswith('-v2'))
        with patch.object(p.previous,'JDK',p.TC/'jdk-25.0.4'):
            with self.assertRaisesRegex(ValueError,'before output'):p.namespace()


if __name__=='__main__':unittest.main()
