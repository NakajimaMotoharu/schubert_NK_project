"""Generated all-role source/duration/outcome qualification; no stop authority."""
import ast
import unittest
from pg1772_warning_owned_stop_sources import sources,context


class Stop(unittest.TestCase):
    def test_all_current_helpers_keep_warning_and_failure_separate(self):
        digest,owned,result,utc=context();self.assertTrue(result['managerFailureRetained'])
        raw=sources();self.assertEqual(14,len(raw))
        combined='\n'.join(raw.values())
        for text in ['4148e3e8-f107-431a-ab27-d6e6d1f1772e','b5a12ee25dc44ec49b08f5d084b4052f','81404764713','83204764713',digest,utc,'pg1770-next-day-full-warning-seal-v1']:
            self.assertIn(text,combined)
        self.assertIn('done.outcome()==MaintenanceCompletion.Outcome.WARNING',raw['Pg1772NativeStop.java'])
        self.assertIn('managerFailureRetained=true',raw['Pg1772NativeStop.java'])
        self.assertNotIn('genuineParentDone=true',raw['Pg1772NativeStop.java'])
        for name,body in raw.items():
            if name.endswith('.py'):ast.parse(body)
        for identity in owned.values():self.assertIn(identity[1],combined)


if __name__=='__main__':unittest.main()
