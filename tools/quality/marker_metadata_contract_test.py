"""Six independent metadata grammar checks; no target application or existing PT replay."""
import unittest
from marker_metadata_contract import validate_description

TEXT='  flags: (0x0600) ACC_INTERFACE, ACC_ABSTRACT\n  interfaces: 0, fields: 0, methods: 0, attributes: 1\n'
class MarkerMetadataContractTest(unittest.TestCase):
    def test_accept_empty_package_interface(self):
        self.assertIsNone(validate_description(TEXT,'empty capability, retained physical'))
    def test_reject_missing_reason(self):
        with self.assertRaises(ValueError):validate_description(TEXT,'')
    def test_reject_executable_method(self):
        with self.assertRaises(ValueError):validate_description(TEXT.replace('methods: 0','methods: 1'),'reason')
    def test_reject_field(self):
        with self.assertRaises(ValueError):validate_description(TEXT.replace('fields: 0','fields: 1'),'reason')
    def test_reject_noninterface(self):
        with self.assertRaises(ValueError):validate_description(TEXT.replace('ACC_INTERFACE, ACC_ABSTRACT','ACC_FINAL, ACC_SUPER'),'reason')
    def test_reject_parent_interface(self):
        with self.assertRaises(ValueError):validate_description(TEXT.replace('interfaces: 0','interfaces: 1'),'reason')
if __name__=='__main__':unittest.main()
