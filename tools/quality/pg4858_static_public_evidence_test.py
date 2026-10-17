import json
import unittest
import pg4858_static_public_evidence as role


class Projection(unittest.TestCase):
    def test_allowlist_preserves_all_rows_and_unknown_without_raw_values(self):
        row = {'id':'fixture-1', 'path':'src/fixture.java','sourceSha256':'a'*64,'rule':'CloseResource','priority':'3','coordinates':{'beginline':1},'disposition':'UNCLASSIFIED','qualityGatePass':False,'rawWarningRemoved':False,'message':'PRIVATE_SYNTHETIC_MARKER','session':'PRIVATE_SYNTHETIC_MARKER'}
        result = {'rawFindings':1,'technicalDispositions':0,'unclassified':1}
        value = role.project([row],result)
        self.assertNotIn('PRIVATE_SYNTHETIC_MARKER',json.dumps(value))
        self.assertEqual('UNCLASSIFIED',value[0]['disposition']); self.assertFalse(value[0]['qualityGatePass'])
        with self.assertRaises(ValueError): role.project([],result)
        with self.assertRaises(ValueError): role.project([{**row,'qualityGatePass':True}],result)


if __name__ == '__main__': unittest.main()
