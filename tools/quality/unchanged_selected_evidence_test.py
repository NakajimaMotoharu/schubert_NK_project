import unittest
import xml.etree.ElementTree as ET
import unchanged_selected_evidence as p


class UnchangedSelectionEvidenceTest(unittest.TestCase):
    def test_branchless_requires_actual_absence_and_explicit_reason(self):
        tree = self.tree()
        c = tree.find('package/class')
        c.remove(c.findall('counter')[-1])
        values = p.target_counter(tree, 'batch:public/Receipt.class', 'Data record ctor/toString have no actual branch')
        self.assertNotIn('BRANCH', values)
        for bad, reason in ((self.tree(), 'cannot hide present branch'), (tree, ''), (tree, ' ')):
            with self.assertRaises(ValueError):
                p.target_counter(bad, 'batch:public/Receipt.class', reason)
        c.find('counter').set('missed', '1')
        with self.assertRaises(ValueError):
            p.target_counter(tree, 'batch:public/Receipt.class', 'no branches but missed line')

    def tree(self):
        root = ET.Element('report')
        c = ET.SubElement(ET.SubElement(root, 'package'), 'class', name='public/Receipt')
        for t in ('LINE', 'METHOD', 'CLASS', 'BRANCH'):
            ET.SubElement(c, 'counter', type=t, covered='1', missed='0')
        return root

    def test_positive_all_four_and_no_absent_counter_filling(self):
        self.assertEqual(4, len(p.target_counter(self.tree(), 'batch:public/Receipt.class')))
        with self.assertRaises(ValueError):
            p.target_counter(self.tree(), 'batch:missing/Receipt.class')
        for key, value in (('missed', '1'), ('covered', '0')):
            tree = self.tree()
            tree.find('package/class/counter').set(key, value)
            with self.assertRaises(ValueError):
                p.target_counter(tree, 'batch:public/Receipt.class')
        tree = self.tree()
        c = tree.find('package/class')
        c.remove(c.findall('counter')[-1])
        with self.assertRaises(ValueError):
            p.target_counter(tree, 'batch:public/Receipt.class')

    def test_original_current_case_cannot_be_missing_duplicate_failed_or_other_source(self):
        row = dict(className='PublicTest', method='case1', source='current', result='PASS_ORIGINAL_XML')
        self.assertEqual(row, p.case_join([row], 'PublicTest', 'case1', 'current'))
        for rows in ([], [row, row], [dict(row, source='old')], [dict(row, result='FAIL')]):
            with self.assertRaises(ValueError):
                p.case_join(rows, 'PublicTest', 'case1', 'current')


if __name__ == '__main__':
    unittest.main()
