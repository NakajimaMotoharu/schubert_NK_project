import re
import unittest
import pg6820_web_prebind_original_jvm as p


class PreBindOriginalJvmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,_,_,cls.raw=p.read_original()

    def test_original_order_and_late_empty_variant(self):
        value=p.inspect_order(self.raw)
        self.assertLess(value['optionalEmptyBci'],value['bindBci'])
        old=p.block(self.raw,p.OPEN)
        self.assertIn(' open(',old.splitlines()[0])
        with self.assertRaises(ValueError):p.block(self.raw.replace(' open(',' renamedOpen('),p.OPEN)
        changed=re.sub(r'(^\s+)\d+(: invokestatic[^\n]*java/util/Optional.empty:)',r'\g<1>9999\2',old,flags=re.M)
        self.assertNotEqual(old,changed)
        with self.assertRaises(ValueError):p.inspect_order(self.raw.replace(old,changed,1))

    def test_post_factory_allocation_variant_rejected(self):
        ctor=p.block(self.raw,p.CTOR)
        changed=ctor.replace('    Code:\n','    Code:\n      9999: new #1 // class java/lang/Object\n',1)
        self.assertNotEqual(ctor,changed)
        with self.assertRaises(ValueError):p.inspect_order(self.raw.replace(ctor,changed,1))


if __name__=='__main__':unittest.main()
