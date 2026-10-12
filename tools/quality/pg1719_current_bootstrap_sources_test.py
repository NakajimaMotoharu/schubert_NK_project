"""Independent exact role tuple, genuine original, complete input graph and limits."""
import ast
import unittest
from pg1719_current_bootstrap_sources import files


class CurrentBootstrapSourcesTest(unittest.TestCase):
    def test_actual_tuple_closed_input_and_old_authority_absent(self):
        source=files('6b29aa3fbeee305335bba17f2fe40f51041a3197cc17c9795a9ddd949930c838')
        joined='\n'.join(source.values())
        for v in ['2741c4546afad6c1e8b6efbd53dfb58144edf7bb','195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',
                  '02e941b9-1c52-4018-a193-63dd00b269af','40da389f-23fc-4ad4-a71b-cf72a6bd5a62',
                  '68542820690','2026-10-12T14:45:34.509749Z','pg1718-current-bootstrap-before-v1','==674']:
            self.assertIn(v,joined)
        for old in ['40ef6e894573d2ffab1d1732124960f9c98d5f97','PG932','pg983','Pg983','cc9ed874',
                    'eeae04ea-713c-4f2d-888d-358fb4bed274','213904','201380374989']:
            self.assertNotIn(old,joined)
        java=source['Pg1719BootstrapExisting.java']
        self.assertLess(java.index('beforeOwnership(Pg1719BootstrapExisting::verifyInputClosure)'),java.index('require(MaintenanceFileLock.create().tryExclusive('))
        self.assertIn('lease.confirmClosed()',java)
        self.assertIn('Pg387TrustedDeployment.STEM="pg1638"',java)
        helper=source['pg1719_bootstrap_existing.py']
        self.assertIn('strict(baseline_path,0o600,67108864)',helper)
        self.assertIn("query+'commit;'],67108864)",helper)
        for name,raw in source.items():
            if name.endswith('.py'):
                for n in ast.walk(ast.parse(raw)):
                    roots=[v.name.split('.')[0]for v in n.names]if isinstance(n,ast.Import)else[n.module.split('.')[0]]if isinstance(n,ast.ImportFrom)and n.module else[]
                    for module in roots:
                        if module.startswith('pg'):self.assertIn(module+'.py',source)


if __name__=='__main__':unittest.main()
