import ast
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg4870_ssc301_302_unused_post as role


class Post(unittest.TestCase):
    def test_all_candidate_checks_under_owned_refs_and_summary_after_normal_close(self):
        values=role.role.sources()
        with patch.object(role.role,'pinned',side_effect=lambda folder,name:values[name]):raw=role.payload()
        tree=ast.parse(raw);self.assertEqual(0,check(raw,'<full actual post>'))
        outer=next(n for n in tree.body if isinstance(n,ast.Try) and 'manager.UnrefUnit(u)' in ast.unparse(n.finalbody))
        held=ast.unparse(outer.body)
        for text in ['0.1.0-PG4860','0.1.0-PG4702','pg4860-manifest.sig',role.role.view.SLOT+'/before.private.json',"sum((p.endswith('.exec') for p in native)) == 72",'json.loads(before) == expected',"'native72Preserved': True","'guestFilesWritten': 2"]:
            self.assertIn(text,held)
        final=tree.body[-1];self.assertGreater(final.lineno,outer.end_lineno)
        self.assertIn('**candidate_post',ast.unparse(final))
        self.assertEqual(1,raw.count('def complete_configuration('))
        self.assertEqual(0,checkPath(role.__file__));self.assertEqual(0,checkPath(__file__))
        values['pg4864_configuration_capture.py']=values['pg4864_configuration_capture.py'].replace('def complete_configuration(','def foreign_configuration(')
        with patch.object(role.role,'pinned',side_effect=lambda folder,name:values[name]),self.assertRaises(ValueError):role.payload()


if __name__=='__main__':unittest.main()
