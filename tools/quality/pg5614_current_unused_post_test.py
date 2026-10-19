import ast
import unittest
from pyflakes.api import check,checkPath
import pg5614_current_unused_post as post


class IndependentUnusedPost(unittest.TestCase):
    def test_full94_and_current_candidate_types_are_not_shadowed(self):
        raw=post.payload();self.assertEqual(check(raw,'<all post dependencies pre-stage>'),0)
        tree=ast.parse(raw);assign={n.targets[0].id:ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in('EXPECTED_CURRENT_SOURCE','EXPECTED_CANDIDATE_SOURCE','CANDIDATE_RECORD','EXPECTED_BEFORE_SHA')}
        self.assertEqual(assign['EXPECTED_CURRENT_SOURCE'],post.role.CURRENT);self.assertEqual(assign['EXPECTED_CANDIDATE_SOURCE'],post.role.SOURCE)
        self.assertIsInstance(assign['CANDIDATE_RECORD'],dict);self.assertNotEqual(assign['EXPECTED_CURRENT_SOURCE'],assign['EXPECTED_CANDIDATE_SOURCE'])
        self.assertIn('json.loads(before_raw)==captured',raw);self.assertIn("'nativePhysicalFiles':94",raw)
        self.assertIn("'full11BeforeSha256':EXPECTED_BEFORE_SHA",raw);self.assertIn("'candidateUnusedOnly':True",raw)
        self.assertIn("with(destination/'after.private.json').open('xb')",raw)
        self.assertNotIn("with(destination/'before.private.json').open('xb')",raw)
        self.assertIn('pg5496-current-owned-tools-v1',raw)

    def test_no_partial_or_wrong_placement_receipt_promoted(self):
        good={'actualExit':0,'action':'place','candidateSource':post.role.SOURCE,'installedSource':post.role.CURRENT,'unusedPlacementOnly':True,'startsStopsReloadsSqlWrites0':True,'oldFailedNormalized':False}
        post.qualify_placement(good)
        for key,value in(('actualExit',1),('actualExit',False),('action','stage'),('candidateSource',post.role.CURRENT),('installedSource',post.role.SOURCE),('oldFailedNormalized',True)):
            with self.assertRaises(ValueError):post.qualify_placement({**good,key:value})
        for path in(post.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
