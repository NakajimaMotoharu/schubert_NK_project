"""Actual all-script global assignment separation and explicit retained binding."""
import ast
import unittest
from pg1788_warning_pair_once_handoff_v3 import payload,SLOT


class Globals(unittest.TestCase):
    def test_original_capture_profile_not_rebound_to_retained_proof(self):
        raw=payload();tree=ast.parse(raw)
        old=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='old'for t in n.targets)]
        self.assertEqual(1,len(old))
        retained=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='retained_proof'for t in n.targets)]
        self.assertEqual(1,len(retained))
        capture=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='capture')
        self.assertTrue("old['unitFilesActual']" in ast.get_source_segment(raw,capture))
        original=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='original')
        self.assertEqual("def original():\n    require(capture() == retained_proof['fullCurrent'])",ast.unparse(original))
        save=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SAVE'for t in n.targets)][-1]
        self.assertEqual("SAVE = BASE / '"+SLOT+"'",ast.unparse(save))
        self.assertFalse('pg1786-warning-pair-once-handoff-v2' in raw)


if __name__=='__main__':unittest.main()
