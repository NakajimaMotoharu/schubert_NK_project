"""Handwritten class attribute fixture; no Java Production expected generation."""
import struct
import unittest
from pg1540_debug_line_delta import positions, verify

def u2(v):return struct.pack('>H',v)
def u4(v):return struct.pack('>I',v)
def fixture(line):
    utf=lambda b:b'\x01'+u2(len(b))+b
    pool=b''.join(utf(b)for b in [b'Code',b'LineNumberTable',b'method',b'()V',b'Record'])
    line_table=u2(2)+u2(0)+u2(line)+u2(1)+u2(line+2)
    code=u2(1)+u2(1)+u4(2)+b'\x00\xb1'+u2(0)+u2(1)+u2(2)+u4(len(line_table))+line_table
    method=u2(1)+u2(3)+u2(4)+u2(1)+u2(1)+u4(len(code))+code
    return b'\xca\xfe\xba\xbe'+u2(0)+u2(69)+u2(6)+pool+u2(1)+u2(0)+u2(0)+u2(0)+u2(0)+u2(1)+method+u2(1)+u2(5)+u4(2)+u2(0)

class LineDeltaTest(unittest.TestCase):
    def test_literal_delta_and_retained_code_attribute(self):
        self.assertEqual(verify(fixture(100),fixture(101)),{'lineEntries':2,'lineOffset':1,'nonLineBytesIdentical':True})

    def test_every_other_byte_mutation_refused(self):
        old=fixture(100);new=fixture(101);allowed={i for p in positions(old)for i in [p,p+1]}
        for i in range(len(new)):
            if i in allowed:continue
            raw=bytearray(new);raw[i]^=1
            with self.subTest(byte=i),self.assertRaises((ValueError,UnicodeDecodeError)):verify(old,bytes(raw))

    def test_foreign_line_null_type_truncation_or_addition_refused(self):
        for value in [None,bytearray(fixture(101)),b'',fixture(100),fixture(102),fixture(101)[:-1],fixture(101)+b'\0']:
            with self.assertRaises(ValueError):verify(fixture(100),value)
        for offset in [0,2,None,True]:
            with self.assertRaises(ValueError):verify(fixture(100),fixture(101),offset)

if __name__=='__main__':unittest.main()
