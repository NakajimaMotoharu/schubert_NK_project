import unittest
from pg2658_operation_candidate_sources import sources, bind, CURRENT, SOURCE, CURRENT_BOM, BEFORE, TOOLS


class OperationRoles(unittest.TestCase):
    def test_current_actual_roles_and_history_not_authority(self):
        values=sources('a'*64);raw='\n'.join(values.values())
        for marker in [CURRENT,SOURCE,CURRENT_BOM,BEFORE,TOOLS,'pg2656-current-a79-before-v1','b29fb3e5-2c46-4eac-b8f3-d03b986338e3','d0219581-24e4-4136-ac90-39d54e704378']:
            self.assertIn(marker,raw)
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG2654',values['pg2658_input_preflight.py'])
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG2512',values['Pg2658UnusedStage.java'])
        self.assertIn('START=41101204300;END=42816406603',values['pg2658_native_refs.py'])
        self.assertIn('/proc/287080',values['pg2658_native_refs.py'])
        self.assertNotIn('pg2514-current-cdbc-before-v2',raw)

    def test_invalid_candidate_or_before_refused(self):
        for v in [None,'a'*63,'x'*64]:
            with self.assertRaises(ValueError):sources(v)
        with self.assertRaises(ValueError):sources('a'*64,'b'*64)

    def test_overlapping_source_and_release_roles(self):
        import pg2516_current_strict_candidate_sources as old
        self.assertEqual(SOURCE+' '+CURRENT+' PG2654 PG2512',bind(old.SOURCE+' '+old.CURRENT+' PG2512 PG2428'))


if __name__=='__main__':unittest.main()
