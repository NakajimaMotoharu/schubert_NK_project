import ast
import unittest
from pg1295_completed_unused_stage_dispatch import STAGE,GUEST,REMOTE


class ClosedUnusedTransportTest(unittest.TestCase):
    def test_actual_complete_archive_policy_and_new_only_paths(self):
        ast.parse(STAGE);env={}
        exec(STAGE[:STAGE.index('import pathlib,hashlib,json,os,tarfile,stat')],env)
        env['archive_members']([('a','file')],{'a'})
        for bad in [[('../a','file')],[('a','link')],[('a','file'),('a','file')],[('extra','file')]]:
            with self.assertRaises(ValueError):env['archive_members'](bad,{'a'})
        self.assertIn('/pg1295-fixed-stage-v1/pg1293-native-tools-v1.tar',STAGE)
        self.assertEqual(GUEST,'/var/lib/pgpt-s1-preservation/pg1293-native-tools-v1')
        self.assertEqual(REMOTE,'/home/ubuntu/pg1295-candidate-input-v1')
        self.assertNotIn('StartUnit',STAGE)
        self.assertNotIn('StopUnit',STAGE)


if __name__=='__main__':unittest.main()
