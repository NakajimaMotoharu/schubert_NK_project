import struct
import unittest
from classfile_line_numbers import compare,normalized


def example(line=77,opcode=0xb1,name=b'm'):
    u2=lambda x:struct.pack('>H',x)
    u4=lambda x:struct.pack('>I',x)
    text=lambda x:b'\1'+u2(len(x))+x
    cp=text(b'C')+b'\7'+u2(1)+text(b'java/lang/Object')+b'\7'+u2(3)+text(name)+text(b'()V')+text(b'Code')+text(b'LineNumberTable')
    table=u2(1)+u2(0)+u2(line)
    code=u2(0)+u2(0)+u4(1)+bytes([opcode])+u2(0)+u2(1)+u2(8)+u4(len(table))+table
    method=u2(9)+u2(5)+u2(6)+u2(1)+u2(7)+u4(len(code))+code
    return b'\xca\xfe\xba\xbe'+u2(0)+u2(69)+u2(9)+cp+u2(0x21)+u2(2)+u2(4)+u2(0)+u2(0)+u2(1)+method+u2(0)


class ExactLineMask(unittest.TestCase):
    def test_only_line_u2_is_masked(self):
        raw=example();after=example(88);masked,lines=normalized(raw)
        self.assertEqual(1,len(lines));self.assertEqual(('m()V',0,77),(lines[0]['method'],lines[0]['startPc'],lines[0]['lineNumber']))
        self.assertEqual(len(raw)-4,lines[0]['offset'])
        expected=bytearray(raw);expected[-4:-2]=b'\0\0'
        self.assertEqual(bytes(expected),masked)
        result=compare(raw,after)
        self.assertFalse(result['rawEqual']);self.assertTrue(result['lineNumberNormalizedEqual'])
        self.assertEqual(raw,example())

    def test_code_and_constant_pool_changes_are_not_debug(self):
        for changed in (example(opcode=0),example(name=b'n')):
            result=compare(example(),changed)
            self.assertFalse(result['rawEqual']);self.assertFalse(result['lineNumberNormalizedEqual'])

    def test_equal_bytes_and_invalid_structures(self):
        self.assertTrue(compare(example(),example())['rawEqual'])
        invalid_cp=bytearray(example());invalid_cp[10]=255
        invalid_length=bytearray(example());invalid_length[-12:-8]=struct.pack('>I',7)
        invalid_pc=bytearray(example());invalid_pc[-6:-4]=struct.pack('>H',1)
        for bad in (b'',b'notaclass',example()[:-1],example()+b'\0',bytes(invalid_cp),bytes(invalid_length),bytes(invalid_pc)):
            with self.subTest(length=len(bad)),self.assertRaises(ValueError):normalized(bad)


if __name__=='__main__':unittest.main()
