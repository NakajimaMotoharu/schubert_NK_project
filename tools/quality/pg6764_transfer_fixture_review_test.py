import re
import subprocess
import unittest
import pg6764_transfer_fixture_review as p


class ConfirmedCloseSourceTest(unittest.TestCase):
    def test_current_fixture_confirms_close_and_fault_site(self):p.verify((p.ROOT/p.TEST).read_text())

    def test_old_finally_attempt_counter_and_missing_provenance_cannot_qualify(self):
        text=(p.ROOT/p.TEST).read_text()
        bad,n=re.subn(r'delegate\.close\(\);\s*closedStreams\+\+;', 'try { delegate.close(); } finally { closedStreams++; }',text)
        self.assertEqual(1,n)
        for altered in (bad,text.replace('f.faultsInjected','0')):
            with self.assertRaises(ValueError):p.verify(altered)

    def test_original_compile_failed_source_is_preserved_and_not_qualified(self):
        old=subprocess.check_output(['git','show','7b6b3304d0b899f9f9fae71117abc4caf0559093:'+p.TEST],cwd=p.ROOT,text=True)
        with self.assertRaises(ValueError):p.verify(old)


if __name__=='__main__':unittest.main()
