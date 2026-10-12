"""Independent current bounds/generation/archive assertions on emitted script."""
import ast
import unittest
from pg1839_warning_current_native_catalog import catalog_source


class Catalog(unittest.TestCase):
    def test_actual_script_current_bounds_archive_and_failed_pid1_only(self):
        raw=catalog_source('def completed(rows,original): return {}\n')
        compile(raw,'<fixture>','exec')
        self.assertIn('ROOT_START=81404764713',raw)
        self.assertIn('ROOT_END=83018953880',raw)
        self.assertIn("JOB_RESULT')=='failed'",raw)
        self.assertIn("completion['genuinePid1StartDone']is False",raw)
        self.assertIn('len(old)==20',raw)
        self.assertIn('pg1759-next-day-ordinary-once-v1',raw)
        self.assertIn('pg1833-native-stop-v1',raw)
        self.assertIn('set(excluded)==set(old)-',raw)
        self.assertIn("inv=before['units'][unit]['InvocationID']",raw)
        self.assertFalse('fe43e94b1fbf4886bb4ab3922fd16f9c'in raw)
        tree=ast.parse(raw)
        self.assertFalse(any(isinstance(n,ast.Constant)and n.value in [66941284515,68542820690]for n in ast.walk(tree)))


if __name__=='__main__':unittest.main()
