"""Current actual emitted proof/recovery/post full namespaces and exact signal targets."""
import ast
import unittest
from pg1993_partial_runtime_pair_once_handoff import payload
from pg1995_partial_runtime_recovery_full_post import payload as post


class Current(unittest.TestCase):
    def test_actual_current_once_and_no_reload_file_mutation(self):
        raw=payload();calls=[n for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='terminate']
        self.assertEqual([498758,498727],[n.args[0].value for n in calls])
        self.assertEqual([10276392,10276205],[n.args[1].value for n in calls])
        self.assertIn("expected['partialRuntimeFileVerified'] is True",raw)
        for old in ['291213','291242','490998','491029']:
            self.assertTrue(old not in raw,'no old current target '+old)
        self.assertNotIn("['systemctl', 'daemon-reload']",raw);self.assertNotIn('os.unlink',raw)
        p=post();self.assertIn("lines[-2:] == [b'0', b'0']",p)
        self.assertIn('partialNewRuntimeFileNoReload',p);self.assertIn('old1983CloseUnknownRetained',p)
        self.assertIn('78f1488383951e0fc2716bcf63ab41f75c64e975440e7f5e079fd6129f8612ec',p)


if __name__=='__main__':unittest.main()
