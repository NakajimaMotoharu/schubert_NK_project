"""Actual entry globals and stage/current/archive/action/pinned source must agree."""
import builtins
import symtable
import unittest
from unittest.mock import patch
import pg2003_existing_runtime_finish_dispatch as entry


class Entry(unittest.TestCase):
    def test_whole_entry_and_closed_action(self):
        raw=entry.source();base=entry.prior.prior.prior.prior
        ns={**base.prior.__dict__,'sources':entry.sources,'TOOLS':entry.TOOLS,'CLASS':entry.CLASS,'TARGET':entry.TARGET,'GUEST':entry.GUEST,'REMOTE':entry.REMOTE,'STAGE':entry.STAGE}
        table=symtable.symtable(raw,'<actual remaining entry>','exec').get_children()[0]
        self.assertEqual(set(),{x.get_name()for x in table.get_symbols()if x.is_global()and x.is_referenced()}-set(ns)-set(dir(builtins)))
        exec(compile(raw,'<actual namespace>','exec'),ns)
        with patch.object(base.prior.sys,'argv',['driver','prepare-resume']),patch.object(base.prior.subprocess,'check_output')as git:
            with self.assertRaises(ValueError):ns['main']()
            git.assert_not_called()
        self.assertEqual('Pg2001ExistingRuntimeFinish',ns['CLASS'])
        for value in ['pg2002-frozen-v1.safe.json','pg2003-qualified-tools-v1.tar','PG2001_INPUT_CLOSURE_READY','finish-runtime']:
            self.assertTrue(value in raw,'actual entry binding '+value)
        for value in ['pg2003-qualified-tools-v1.tar','pg2001-existing-runtime-tools-v1','0.1.0-PG1846']:
            self.assertTrue(value in entry.STAGE,'actual stage binding '+value)


if __name__=='__main__':unittest.main()
