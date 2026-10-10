import ast
import unittest
from pg1177_canonical_runtime_owner_proof import payload


class CanonicalOwnerTest(unittest.TestCase):
    def test_exact_generation_effective_resume_and_all_pins(self):
        s=payload();ast.parse(s)
        for p in ['JAVA=420139;CHILD=420168','5003981','5004100','canonical_configuration(','zz-pg1160-once-resume.conf','pg1172-runtime-tools-v2','a936fd3e8f851255acc66156a99db967b52195033dea4b75cf2515e3bce7b36c']:
            self.assertTrue(p in s,p)
        self.assertFalse('pidfd_send_signal'in s);self.assertFalse('daemon-reload'in s)


if __name__=='__main__':unittest.main()
