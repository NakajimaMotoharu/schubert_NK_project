import ast
import unittest
from pg1197_completed_current_capture import payload


class CurrentCaptureTest(unittest.TestCase):
    def test_actual_full_generation_source_and_same_snapshot_nonmutation(self):
        s=payload();ast.parse(s)
        for part in ['data_oracle.output_bound(p.returncode,len(p.stdout))','row_command([','data_oracle.after(','oldRowsRetained','CAPTURE_UNITS','exec(GUARD_SOURCE,witness.__dict__)','observed==capture()','journal-read-','a[:3]==b[:3]','projected,now','privateBeforeSha256']:
            self.assertTrue(part in s,part)
        self.assertFalse("sql+'commit;'],33554432)" in s)
        self.assertFalse("parent['Result']=='timeout'" in s)
        self.assertFalse('runtime.owned_prepare(' in s)
        self.assertEqual(sum(isinstance(n,ast.FunctionDef)and n.name=='capture'for n in ast.parse(s).body),1)


if __name__=='__main__':unittest.main()
