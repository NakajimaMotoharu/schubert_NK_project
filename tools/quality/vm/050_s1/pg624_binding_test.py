"""Independent fixed cohort, current/candidate ABI and complete witness binding."""
import ast
from pathlib import Path
import unittest

R=Path(__file__).resolve().parent


class BindingTest(unittest.TestCase):
    def test_current_candidate_and_schema_after_each_configure(self):
        java=(R/'Pg624CompletedDeployment.java').read_text()
        self.assertIn('configure("PG600","23b14a44b10504172e030bbd6625926bf049fb5c",OLD);Pg387TrustedDeployment.expectedSqlCount=28;',java)
        self.assertIn('configure("PG621",source,NEXT);Pg387TrustedDeployment.expectedSqlCount=28;',java)
        wrapper=(R/'pg624_completed_native.py').read_text()
        self.assertIn('/0.1.0-PG600/operations/batch.jar',wrapper)
        self.assertNotIn('/0.1.0-PG621/operations/batch.jar',wrapper)
        self.assertIn("'pg611_parent_receipt.py'",wrapper)
        self.assertIn("oracle.count('\\nOK\\n')==5",wrapper)

    def test_witness_pins_and_complete_stops_and_activation_reauthentication(self):
        source=(R/'pg624_completed_refs.py').read_text()
        nodes=ast.parse(source)
        stopped=next(n.value for n in ast.walk(nodes)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='stopped'for t in n.targets))
        self.assertEqual(ast.literal_eval(stopped),{'caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service'})
        for literal in ['a7e90f2973f966def39d473f09274383bc866ad37d98b73c96658ece0a09c849','==492','29ea92cd6befc7fd26e1ed23b8785bc7ce616d0cc36247cdb0b2f30c83564676','5a1acaa0c35e484c979401e3b6dfb36a','87761979588',"verified/'after.private.json'","verified/'complete.private'",'same_value(before,json.loads']:
            self.assertIn(literal,source)
        for obsolete in ['pg579','PG604','482','267003d6','59234299969']:
            self.assertNotIn(obsolete,source)


if __name__=='__main__':unittest.main()
