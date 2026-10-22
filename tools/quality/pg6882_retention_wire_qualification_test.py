import unittest
import xml.etree.ElementTree as ET
import pg6882_retention_wire_qualification as p


class RetentionWireQualificationTest(unittest.TestCase):
    def fixture(self):
        root = ET.Element('report')
        c = ET.SubElement(ET.SubElement(root, 'package'), 'class', name=p.CLASS)
        for name, desc in p.METHODS.items():
            m = ET.SubElement(c, 'method', name=name, desc=desc)
            for t in ('LINE', 'METHOD', 'BRANCH'):
                ET.SubElement(m, 'counter', type=t, covered='1', missed='0')
        return root

    def test_real_positive_counters_and_exact_member_required(self):
        self.assertEqual(set(p.METHODS), set(p.methods(self.fixture())))
        for attribute, value in (('missed', '1'), ('covered', '0')):
            tree = self.fixture()
            tree.find('package/class/method/counter').set(attribute, value)
            with self.assertRaises(ValueError):
                p.methods(tree)
        tree = self.fixture()
        tree.find('package/class/method').set('desc', 'wrong')
        with self.assertRaises(ValueError):
            p.methods(tree)
        with self.assertRaises(ValueError):
            p.methods(ET.Element('report'))


if __name__ == '__main__':
    unittest.main()
