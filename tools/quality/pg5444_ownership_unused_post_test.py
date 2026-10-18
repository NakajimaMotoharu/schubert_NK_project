import ast
from collections import Counter
import unittest
from pyflakes.api import check,checkPath
from immutable_payload_binding import PROTECTED
import pg5444_ownership_unused_post as post


def capsules(raw):
    return Counter(ast.get_source_segment(raw,n)for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in n.targets))


class Post(unittest.TestCase):
    def test_no_foreign_source_or_boolean_exit_accepted(self):
        good={'actualExit':0,'sourceQualified':True,'currentApprovalEpochChanged':False,
            'action':'place','candidateSource':post.role.SOURCE,'installedSource':post.role.CURRENT,
            'unusedPlacementOnly':True,'startsStopsReloadsSqlWrites0':True,'oldFailedNormalized':False}
        post.qualify_placement(good)
        for key,value in(('actualExit',False),('candidateSource',post.role.CURRENT),('installedSource',post.role.SOURCE),('unusedPlacementOnly',1),('action','stage'),('oldFailedNormalized',True)):
            with self.subTest(key=key),self.assertRaises(ValueError):post.qualify_placement({**good,key:value})

    def test_exact_capsules_and_full_before_native_under_new_reference_scope(self):
        raw=post.payload();self.assertEqual(check(raw,'<independent candidate unused post>'),0)
        self.assertEqual(capsules(raw),capsules(post.current.payload()))
        tree=ast.parse(raw);outer=next(n for n in tree.body if isinstance(n,ast.Try)and 'manager.UnrefUnit(u)'in ast.unparse(n.finalbody))
        held=ast.unparse(outer.body)
        for item in('0.1.0-PG5430','0.1.0-PG4980','pg5430-manifest.sig','json.loads(before) == expected','native88Preserved','candidateUnusedOnly'):
            self.assertIn(item,held)
        self.assertGreater(tree.body[-1].lineno,outer.end_lineno)
        self.assertIn('**candidate_post',ast.unparse(tree.body[-1]))
        self.assertIn('newTenReferencesReturnedNormally',ast.unparse(tree.body[-1]))
        source=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SOURCE'for t in n.targets)]
        self.assertEqual(len(source),1);self.assertEqual(ast.literal_eval(source[0].value),post.role.CURRENT)
        candidate=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='CANDIDATE'for t in n.targets))
        self.assertEqual(ast.literal_eval(candidate.value)['candidateSource'],post.role.SOURCE)
        for path in(post.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
