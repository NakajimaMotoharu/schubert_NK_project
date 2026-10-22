import unittest
import xml.etree.ElementTree as ET
import pg6848_observation_boundary_qualification as p


class OriginalObservationMethodTest(unittest.TestCase):
    def tree(self,desc=None):
        root=ET.Element('report');pkg=ET.SubElement(root,'package');cls=ET.SubElement(pkg,'class',name=p.PGCLASS)
        method=ET.SubElement(cls,'method',name='postgres',desc=desc or p.PGDESC)
        for kind in('LINE','METHOD','BRANCH'):ET.SubElement(method,'counter',type=kind,covered='1',missed='0')
        return root,method

    def test_actual_positive_method_counters_and_no_class_synthesis(self):
        tree,method=self.tree();self.assertEqual({'LINE','METHOD','BRANCH'},set(p.postgres_method(tree)))
        method.find('counter').set('missed','1')
        with self.assertRaises(ValueError):p.postgres_method(tree)

    def test_missing_counter_or_wrong_descriptor_rejected(self):
        tree,method=self.tree();method.remove(method.find('counter'))
        with self.assertRaises(ValueError):p.postgres_method(tree)
        tree,_=self.tree('()V')
        with self.assertRaises(ValueError):p.postgres_method(tree)


if __name__=='__main__':unittest.main()
