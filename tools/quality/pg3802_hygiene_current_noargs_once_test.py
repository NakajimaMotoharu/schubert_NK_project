import ast
import unittest
import pg3802_hygiene_current_noargs_once as tool


class OrdinaryAdmission(unittest.TestCase):
    def test_single_start_after_full_guard_and_reservation_with_ref_close(self):
        raw=tool.payload({'fixture.py':'0'*64});ast.parse(raw)
        self.assertEqual(1,raw.count("['/usr/bin/systemctl','start','--no-block'"))
        for marker in [tool.SOURCE,tool.BOM,'require(len(records)==34)','ordinaryNoargs=True','originalBudgetSeconds=1800',"'replayAllowed':False",'read_rows()==first','complete_configuration(r.stdout,unit)==oldcfg','finite-','PG3748','pg3798-observer-v1',tool.SLOT]:self.assertTrue(marker in raw,marker)
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index("['/usr/bin/systemctl','start'"))
        self.assertLess(raw.index("['/usr/bin/systemctl','start'"),raw.index('for unit in reversed(refs):'))
        self.assertLess(raw.index('for unit in reversed(refs):'),raw.rindex('print(json.dumps(current))'))
        self.assertNotIn('pg3462',raw)


if __name__=='__main__':unittest.main()
