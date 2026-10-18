import inspect
import unittest
from pyflakes.api import check,checkPath
import pg5560_snapshot_static_projection as entry


class CurrentRows(unittest.TestCase):
    def test_unknown_or_old_whole_does_not_reuse_context(self):
        with self.assertRaises(ValueError):entry.project({}, {}, [], {}, {'productionSource':'old'}, {})

    def test_every_individual_current_row_must_match_source_and_span(self):
        raw=inspect.getsource(entry.project)
        for fact in("row[k]!=ref[k]","sourceSpanSha256","matched!=set(context)","ziprows!=2",'fingerprints!=1',"len(refs)!=11"):
            self.assertIn(fact,raw)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)
        raw=entry.collect_source()
        self.assertEqual(check(raw,'<fresh metadata only>'),0)
        self.assertNotIn('PG5424',raw)
        self.assertNotIn('PG5556-ownership',raw)
        self.assertIn('runs/PG5556-snapshot-static-v1/pmd.xml',raw)
        self.assertIn('runs/PG5556-snapshot-static-input-v1/candidate/',raw)
        producer=inspect.getsource(__import__('pg5556_snapshot_static').main)
        self.assertIn("'staticJob':'PG5556-snapshot-static-v1'",producer)
        self.assertIn("'candidateJob':'PG5556-snapshot-static-input-v1'",producer)


if __name__=='__main__':unittest.main()
