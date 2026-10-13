import ast
import unittest
import pg2178_newsource_noargs_once as p


class Admission(unittest.TestCase):
    def test_actual_whole_command_and_native_preservation_not_acceptance(self):
        raw=p.payload({'pg2176_watch_parent.py':'a'*64})
        for text in ['PG2126','3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8','62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c','require(len(records)==38)','>=12884901888','pg2178-newsource-noargs-once-v1','replayAllowed']:self.assertIn(text,raw)
        self.assertIn("'--resume'not in declaration[1]",raw)
        self.assertEqual(raw.count("['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']"),1)
        self.assertIn('b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4',raw)
        self.assertIn("require(watch==observer()and native==snapshot())",raw)
        tree=ast.parse(raw)
        scope=next(n for n in tree.body if isinstance(n,ast.Try)and any(isinstance(x,ast.FunctionDef)and x.name=='snapshot'for x in n.body))
        self.assertTrue(any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='run'for n in ast.walk(scope)))
        self.assertNotIn('daemon-reload',raw)


if __name__=='__main__':unittest.main()
