import json
import unittest
from pg1446_current_cold_stage import W
from pg2658_operation_candidate_sources import CURRENT,CURRENT_BOM,BEFORE,SOURCE
import pg2675_operation_publication_compile as c
import pg2676_operation_publication_dispatch as d
import pg2680_operation_publication_post as p


class FinitePublicationConnection(unittest.TestCase):
    def test_complete_abi_and_new_only_dispatch(self):
        abi=c.compiler('a'*64);body=d.source('a'*64);stage=d.stage('a'*64)
        for value in ['pg2672-operation-ro-post-v1','pg2659-frozen','pg2658-operation-unused-tools-v1','pg2675-frozen']:
            self.assertIn(value,abi+body)
        for value in ['411abb597f15a221acd4c0da4a407a035fcbdd20','program/characterization','pg2676-']:
            self.assertIn(value,body)
        self.assertIn('pg2674-operation-publication-tools-v1',stage)
        self.assertIn('pg2676-operation-publication-stage-v1',stage)
        self.assertNotIn('NORMAL_DAEMON_RELOAD',body)

    def test_current_reader_and_all_seven_phase_independent_post(self):
        directory=W/'pg2656-current-a79-before-v1';raw=(directory/'payload.private.py').read_text()
        receipt=json.loads((directory/'manifest.safe.json').read_bytes());fixed={'actualExit':0,'fileHashes':{}}
        post=p.compose(raw,receipt,fixed,'a'*64)
        for value in [SOURCE,CURRENT_BOM,BEFORE,'0.1.0-PG2654','pg2654-manifest.sig',
          'pg2674_ordinary_publication_contract','pg2678-operation-publication-v1','pg2680-operation-publication-post-v1',
          'pg2656-current-a79-before-v1/native-before.private.json','tuple(dict.fromkeys(phase',
          'after[\'unitFilesActual\']==old_after[\'unitFilesActual\']']:
            self.assertIn(value,post)
        self.assertNotIn('pg2532_',post)
        for changes in [{'productionSource':'0'*40},{'privateBeforeSha256':'0'*64},{'actualExit':False},{'payloadSha256':'0'*64}]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):p.compose(raw,{**receipt,**changes},fixed,'a'*64)
        self.assertEqual(receipt['productionSource'],CURRENT)
        with self.assertRaises(ValueError):p.compose(raw,receipt,{'actualExit':False,'fileHashes':{}},'a'*64)


if __name__=='__main__':unittest.main()
