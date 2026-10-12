"""Independent actual positive and foreign role vectors never collide."""
import unittest
from pg1925_disjoint_role_partial_reload_sources import sources


class Roles(unittest.TestCase):
    def test_current_reset_new_and_each_negative_old_or_null(self):
        s=sources();j=s['Pg1925CurrentIdentityTest.java'];real=s['Pg1925PartialReload.java']
        self.assertIn('LABEL="PG1846"',j);self.assertIn('SOURCE="0fd734195b4d5338f6b7e860e087cce561d49562"',j)
        for value in ['new String[]{"PG1292","PG1638",null}','new String[]{"pg1292","pg1638",null}','"2741c4546afad6c1e8b6efbd53dfb58144edf7bb",null}','Path.of("/opt/schubert-nk/releases/0.1.0-PG1638"),null}']:self.assertIn(value,j)
        self.assertNotIn('new String[]{"PG1292","PG1846",null}',j)
        self.assertIn('SOURCE="0fd734195b4d5338f6b7e860e087cce561d49562"',real)
        self.assertIn('if(checks!=13)',j)
        self.assertIn('state==StartupPermitRecords.State.ISSUED?Optional.of',s['Pg1925OriginalTupleTest.java'])


if __name__=='__main__':unittest.main()
