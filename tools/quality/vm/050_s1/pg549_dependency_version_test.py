"""BUG842 exact external-version preservation; no native actions. Management only."""
import ast
from pathlib import Path
import re
import unittest

R=Path(__file__).resolve().parent


def constants(path,name):
    module=ast.parse(path.read_text())
    n=next(n for n in module.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets))
    return ast.literal_eval(n.value)


class Test(unittest.TestCase):
    def test_exact_external_prefixes(self):
        old=R/'pg549_completed_native_v1.py';new=R/'pg549_completed_native_v4.py'
        self.assertEqual(constants(old,'prefixes')[1:],constants(new,'prefixes')[1:])
        self.assertEqual(constants(old,'host_prefixes'),constants(new,'host_prefixes'))
        self.assertEqual(constants(new,'prefixes')[0],'pg549-completed-tools-v4')
        for p in (R/'pg549_completed_compile_v1.sh',R/'pg549_completed_compile_v4.sh'):
            text=p.read_text();match=re.search(r'^task_cp="([^"]+)"',text,re.M)
            self.assertIsNotNone(match)
            if p.name.endswith('v1.sh'):expected=match.group(1)
            else:self.assertEqual(match.group(1),expected)
        newer=R/'pg549_completed_native_v5.py'
        self.assertEqual(constants(old,'prefixes')[1:],constants(newer,'prefixes')[1:])
        self.assertEqual(constants(old,'host_prefixes'),constants(newer,'host_prefixes'))
        self.assertEqual(constants(newer,'prefixes')[0],'pg549-completed-tools-v5')
        self.assertEqual(re.search(r'^task_cp="([^"]+)"',(R/'pg549_completed_compile_v5.sh').read_text(),re.M).group(1),expected)
        text=new.read_text()
        self.assertNotIn('pg464-code-tools-v3',text);self.assertNotIn('pg481-pending-tools-v3',text)
        self.assertIn("W/('pg549-'+mode+'-v4.private.log')",text)
        self.assertIn("W/('pg549-'+mode+'-v4.exit')",text)
        self.assertIn("W/('pg549-'+mode+'-v4.safe.json')",text)


if __name__=='__main__':unittest.main()
