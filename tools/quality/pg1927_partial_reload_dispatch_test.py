"""Actual entry namespace closure, closed arguments and independent full post flags."""
import builtins
import symtable
import unittest
from unittest.mock import patch
import pg1927_partial_reload_dispatch as entry
from pg1930_partial_reload_full_post import payload
from pyflakes.api import check


class Entry(unittest.TestCase):
    def test_actual_main_globals_all_present_and_closed_arguments(self):
        raw=entry.source();table=symtable.symtable(raw,'<actual main>','exec').get_children()[0]
        names={s.get_name()for s in table.get_symbols()if s.is_global()and s.is_referenced()}
        namespace={**entry.prior.__dict__,'sources':entry.sources,'TOOLS':entry.TOOLS,'CLASS':entry.CLASS,'TARGET':entry.TARGET,'GUEST':entry.GUEST,'REMOTE':entry.REMOTE,'STAGE':entry.STAGE}
        self.assertEqual(set(),names-set(namespace)-set(dir(builtins)))
        exec(compile(raw,'<actual entry no missing globals>','exec'),namespace)
        with patch.object(entry.prior.subprocess,'check_output')as git,patch.object(entry.prior.sys,'argv',['driver','activate']):
            with self.assertRaises(ValueError):namespace['main']()
            git.assert_not_called()
        self.assertIn("b'PG1925_INPUT_CLOSURE_READY\\n'",raw)
        self.assertIn("'pg1926-frozen-v1.safe.json'",raw)
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG1846/operations/batch.jar',raw)
        self.assertNotIn('TransitionTest',raw)

    def test_actual_post_statically_complete_and_old_partial_slot_immutable(self):
        raw=payload();self.assertEqual(0,check(raw,'<whole actual full post>'))
        self.assertIn("[b'SuccessExitStatus=10',b'Type=oneshot']",raw)
        self.assertIn('pg1929-partial-reload-v1',raw)
        self.assertIn("'allNewReloadScopesReturnedNormally':True",raw)
        self.assertIn("not(publication/'daemon-reload-reserved.private').exists()",raw)
        self.assertIn("reload_private('daemon-reload-reserved.private')",raw)


if __name__=='__main__':unittest.main()
