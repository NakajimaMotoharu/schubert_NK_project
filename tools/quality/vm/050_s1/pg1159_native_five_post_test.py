import ast
import unittest
from pg1159_native_five_post import payload


class PostTest(unittest.TestCase):
    def test_independent_full_closed_delta_and_negative_no_bootstrap(self):
        s=payload();ast.parse(s)
        for p in ['pg1148-native-five-recovery-v2','2fee063c194b5ae4ef9e526ba3566d4f567a9526bbfec5cead3c8370a07e7d57','native_policy.coverage_delta','fiveNativeDirectoriesPrepared','nativeDumpAccepted','require(set(now)==set(old_native)|','manager.UnrefUnit(u)','resource_zero()']:
            self.assertTrue(p in s,p)
        self.assertFalse('ordinary-bootstrap196'in s);self.assertFalse('systemctl start'in s)
        self.assertFalse('pidfd_send_signal'in s)


if __name__=='__main__':unittest.main()
