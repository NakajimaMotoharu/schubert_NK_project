import struct
import unittest
from classfile_field_flags import fields,only_clear_private_volatile


class ClassFileFlagTest(unittest.TestCase):
    def fixture(self,flags=66,name=b'closed',descriptor=b'Z'):
        # Independent minimal valid field table,empty methods/attributes;not a loaded class.
        def utf8(value):return b'\x01'+struct.pack('>H',len(value))+value
        return (b'\xca\xfe\xba\xbe'+struct.pack('>HHH',0,69,3)+utf8(name)+utf8(descriptor)
                +struct.pack('>HHHHH',0x21,0,0,0,1)+struct.pack('>HHHH',flags,1,2,0)+b'\x00\x00\x00\x00')

    def test_one_exact_bit_only_without_production_invocation(self):
        before=self.fixture();after=self.fixture(2)
        fact=only_clear_private_volatile(before,after)
        self.assertTrue(fact['allOtherClassBytesIdentical']);self.assertEqual((66,2),(fact['oldFlags'],fact['newFlags']))
        self.assertEqual(b'Z',fields(after)[b'closed']['descriptor'])

    def test_missing_field_bad_flag_other_byte_or_wrong_type_fails(self):
        for before,after in ((self.fixture(),self.fixture(0)),(self.fixture(name=b'other'),self.fixture(2,name=b'other')),
                             (self.fixture(),self.fixture(2)+b'\x00'),(self.fixture(descriptor=b'I'),self.fixture(2,descriptor=b'I'))):
            with self.assertRaises(ValueError):only_clear_private_volatile(before,after)
        with self.assertRaises(ValueError):fields(b'not-a-ClassFile')


if __name__=='__main__':unittest.main()
