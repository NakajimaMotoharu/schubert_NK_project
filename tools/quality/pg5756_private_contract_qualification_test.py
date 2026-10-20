"""Negative checks of independent artifact reader, not Production PT."""
import unittest
import pg5756_private_contract_qualification as p


class WholeReaderTest(unittest.TestCase):
    def test_all_raw_bytes_must_match_declared_types(self):
        p.PHYSICAL_KINDS=p.changed_types();keys=sorted(p.PHYSICAL_KINDS)+['same:'+str(i)for i in range(1610)]
        old={k:'a'*64 for k in keys};current={k:('b'*64 if k in p.PHYSICAL_KINDS else'a'*64)for k in keys}
        rows,same=p.physical_difference(old,current,current)
        self.assertEqual(54,len(rows));self.assertEqual(1610,same)
        extra=dict(current);extra['same:0']='c'*64
        with self.assertRaisesRegex(ValueError,'ignored raw'):p.physical_difference(old,extra,extra)
        with self.assertRaisesRegex(ValueError,'same source'):p.physical_difference(old,current,old)

    def test_exact_original_run_and_source_case_additions(self):
        raw=p.emitted({});self.assertIn("runs/PG5754-six-v1",raw);self.assertIn("old = base / 'runs/PG5716-six-v1'",raw)
        self.assertIn('len(oldcases) == 3908',raw);self.assertIn('len(additions) == 24',raw);self.assertIn('len(cases) == 3932',raw)
        self.assertEqual(24,len(p.added_cases()));self.assertNotIn('subprocess.',raw)


if __name__=='__main__':unittest.main()
