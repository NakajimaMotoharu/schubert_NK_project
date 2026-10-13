"""Actual whole source exports/immutable observer/native32/durable noargs admission."""
import ast
import unittest
from pg2070_current_newrun_observer import namespace
from pg2072_current_noargs_newrun_once import payload
from pg2040_fresh_normal_warning_terminal_post import SEALS


class Newrun(unittest.TestCase):
    def test_one_current_unmodified_noargs_entry(self):
        raw=payload({}, {n:'a'*64 for n in SEALS});ast.parse(raw)
        for marker in ['require(len(records)==32)','ordinaryNoargs','oldCompletedRunNotResumed','originalBudgetSeconds','allTenAlreadyTerminal=true','same_except_runtime','os.O_NOFOLLOW','observer()','external-start-guard.private.json','manager.UnrefUnit(u)']:
            self.assertTrue(marker in raw,marker)
        self.assertEqual(1,raw.count("'start','--no-block'"))
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index("'start','--no-block'"))
        self.assertLess(raw.index("'start','--no-block'"),raw.index('finally:',raw.index("'start','--no-block'")))
        files=namespace()['files']();self.assertTrue(files)
        for source in files.values():compile(source,'<actual current observer>','exec')


if __name__=='__main__':unittest.main()
