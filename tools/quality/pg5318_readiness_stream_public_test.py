import unittest
import pg5318_readiness_stream_public as role


class ReadinessIds(unittest.TestCase):
    def test_all_prior31_ids_and_repeated_ten_remain_unchanged(self):
        old=role.ids.revalidated_case_ids();current=role.revalidated_case_ids(stream_new=True)
        self.assertEqual(len(old),31)
        self.assertEqual({k:current[k] for k in old},old)
        self.assertEqual(len(current),37)
        self.assertEqual(len({v['testId'] for v in current.values()}),37)
        self.assertEqual(sum(v['newInThisChange'] for v in current.values()),6)
        repeated=[v for v in current.values() if v['testId'].startswith('PT-OPS-ISS006-R')]
        self.assertEqual(len(repeated),10)
        self.assertFalse(any(v['newIndependentCase'] or v['newInThisChange'] for v in repeated))

    def test_future_revalidation_never_reissues_new_credit(self):
        self.assertFalse(any(v['newInThisChange'] for v in role.revalidated_case_ids().values()))


if __name__=='__main__':unittest.main()
