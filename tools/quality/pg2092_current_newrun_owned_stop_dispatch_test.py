"""Actual complete current stage literals, fresh full oracle and normal parent18/config2."""
import unittest
from pg2092_current_newrun_owned_stop_dispatch import STAGE,ARCHIVE,GUEST,REMOTE,PARENT_PREQUAL,run_source,post_payload,run_action


class Entry(unittest.TestCase):
    def test_actual_stage_profile_and_new_only_transport(self):
        for marker in [ARCHIVE,GUEST,REMOTE,'PG1846','ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7','0fd734195b4d5338f6b7e860e087cce561d49562']:
            self.assertTrue(marker in STAGE,marker)
        self.assertFalse('PG1638'in STAGE)
        raw=run_source();compile(raw,'<actual current entry>','exec')
        for marker in ['pg2091','pg2092','pg2093','pg2094','Pg2090','archive = P / ARCHIVE']:self.assertTrue(marker in raw,marker)
        self.assertTrue('actualStateFieldCount' in PARENT_PREQUAL)
        whole=post_payload();self.assertTrue('require(before_shape(before))'in whole)
        with self.assertRaises(ValueError):run_action('retry')


if __name__=='__main__':unittest.main()
