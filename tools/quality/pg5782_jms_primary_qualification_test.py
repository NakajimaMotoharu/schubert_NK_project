"""Original/current paths, counts and actual byte deltas; no host/job operation."""
import unittest
import pg5782_jms_primary_qualification as p


class ArtifactBinding(unittest.TestCase):
    def test_original_and_prior_are_distinct_exact_paths(self):
        raw=p.emitted({});self.assertIn("out = base / 'runs/PG5780-six-v1'",raw)
        self.assertIn("old = base / 'runs/PG5754-six-v1'",raw);self.assertIn('source-full-PG5780',raw)
        self.assertNotIn('PG5716',raw);self.assertIn('len(oldcases) == 3932',raw);self.assertIn('len(cases) == 3939',raw);self.assertIn('len(additions) == 7',raw)
        self.assertNotIn('source-full-PG5754',raw);self.assertNotIn('transfer/PG5754-source.tar',raw)
        self.assertNotIn('subprocess.',raw);self.assertEqual(7,len(p.added_cases()))

    def test_extra_physical_difference_or_foreign_candidate_refused(self):
        keys=list(p.PHYSICAL_KINDS)+['same:'+str(i)for i in range(1662)];old={k:'a'*64 for k in keys};new={k:'b'*64 if k in p.PHYSICAL_KINDS else'a'*64 for k in keys}
        delta,same=p.physical_difference(old,new,new);self.assertEqual(2,len(delta));self.assertEqual(1662,same)
        other={**new,'same:0':'c'*64}
        with self.assertRaisesRegex(ValueError,'raw delta'):p.physical_difference(old,other,other)
        with self.assertRaisesRegex(ValueError,'candidate'):p.physical_difference(old,new,old)


if __name__=='__main__':unittest.main()
