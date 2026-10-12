"""Exact actual caller namespace and immutable input/profile joins."""
import inspect
import unittest
from pg1862_warning_actual_graph_dispatch import source,main,STAGE


class Actual(unittest.TestCase):
    def test_real_main_composes_newsource_target_helpers_and_graph(self):
        raw=source()
        for v in ['pg1861-frozen-v1.safe.json','Pg1860UnusedStage place','pg1862-warning-release-v1.tar','pg1862-stage-v2.exit','completedObservedHead']:
            self.assertIn(v,raw)
        self.assertIn('pg1860-warning-unused-tools-v1',STAGE)
        caller=inspect.getsource(main)
        self.assertIn("'sources':sources",caller);self.assertIn("'source':source",caller)
        for bad in ['pg1856-frozen','Pg1855UnusedStage','pg1857-stage-v2.exit']:
            self.assertNotIn(bad,raw)


if __name__=='__main__':unittest.main()
