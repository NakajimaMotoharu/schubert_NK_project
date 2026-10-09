"""Explicit static-byte oracle, current after baseline, immutable noargs declaration."""
import ast,unittest
from pg954_current_ordinary_before import payload
class Test(unittest.TestCase):
    def test_current_source_and_old_unitdata_not_old_success(self):
        raw=payload();ast.parse(raw)
        for s in ('40ef6e894573d2ffab1d1732124960f9c98d5f97','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524','8b44b0db4a95049cc9d2085964d6538df428e3ada13877f8d07c47f711fa39f0','a8c6c5d4dca5c02b1ae6b3ee797ba87d129b0dc4851ae31f6e7609ebfd31d980',"static_units=json.loads(static_raw)['unitFiles'];assert len(static_units)==18","assert unit_files==baseline['unitFiles']",'standard_snapshot(limited)','ordinary_argv','assert limited==json.loads(original)',"assert '--resume'not in command",'os.statvfs(candidate).f_flag&os.ST_RDONLY'):
            self.assertIn(s,raw)
        self.assertNotIn("'test'",raw);self.assertNotIn("['systemctl','start",raw)
if __name__=='__main__':unittest.main()
