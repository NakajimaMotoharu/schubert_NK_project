import unittest
from pg5878_process_resource28_review import ROOT,PATH,verify_shape,EXPECTED


class QueryPriorityCountercheck(unittest.TestCase):
    def test_fixed_priority_cancellation_and_no_raw_or_normal_return(self):
        text=(ROOT/PATH).read_text();verify_shape(text)
        self.assertEqual(28,sum(EXPECTED.values()))
        for bad in(text.replace('throw cleanup;','throw primary;',1),text.replace('throw primary;','return;',1),text.replace('Thread.currentThread().interrupt();','Thread.interrupted();',1),text.replace('primary instanceof InterruptedException','primary instanceof Error',1),text.replace('primary.addSuppressed(new StopGateException(StopGateFailure.COMMAND_FAILURE));','primary.addSuppressed(cleanup);',1)):
            with self.assertRaises(ValueError):verify_shape(bad)


if __name__=='__main__':unittest.main()
