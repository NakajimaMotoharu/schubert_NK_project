"""Independent fixed current terminal binding; no Root operations."""
import ast
from pathlib import Path
import unittest
R=Path(__file__).resolve().parent
class Test(unittest.TestCase):
    def test_full_terminal_scope_unchanged_except_actual_source_and_cohort(self):
        expected=(R/'pg580_terminal_final.py').read_text()
        for a,b in [["Pg579","Pg611"],["pg579","pg611"],["PG579","PG611"],["pg580-terminal-final-v1","pg613-terminal-final-v1"],["PG580-terminal-final-v1","PG613-terminal-final-v1"],["3a302026f6fa536e745c627da360dc0fb9c3898941aff24a610319d80df1c232","19b7e618ef04f79aff6cde2c2dbf45269c1f9651efaa44f04d81d84d02b85912"],["cb5951e30fda2ef63f2691a24f302e46b8cffcff6c8345e69644672b9135eaf6","a7e90f2973f966def39d473f09274383bc866ad37d98b73c96658ece0a09c849"],["f6a785436f14339073e98df92464afff240b087df3e93c316ccce47e351c3f58","fbc7033f0d6fd6b6ccd6de656882e2405dc42623b959a69ee86a6074d38e465e"],["57f0e73d-d334-4882-9284-04246011da54","970bbce1-6bba-4db0-ace1-680ee7dfde92"],["59234299969","87761979588"],["PG548","PG600"],["pg548-manifest.sig","pg600-manifest.sig"],["a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b","a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f"],["969d8ded10c0bf5841d9e3a5c531e922caf4a24a","23b14a44b10504172e030bbd6625926bf049fb5c"],["909808,1138681,1141157,1147348,950235","1207482,1451527,1454010,1460173,1304653"]]:expected=expected.replace(a,b)
        actual=(R/'pg613_terminal_final.py').read_text()
        self.assertEqual(actual,expected)
        tree=ast.parse(actual)
        body=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
        ast.parse(body)
        self.assertIn('all24UnchangedTwice',body);self.assertIn('whole187SignedArtifactBytesVerified',body)
        self.assertIn('allClientAdvisoryFlock0',body);self.assertIn('native==snapshot()',body)
        self.assertNotIn('systemctl stop',body)
        self.assertIn("for u in reversed(refs):manager.UnrefUnit(u)",body)
        self.assertIn('pg600-manifest.sig',body)
if __name__=='__main__':unittest.main()
