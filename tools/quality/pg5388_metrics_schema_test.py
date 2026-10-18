import copy
import unittest
import json
import tempfile
from pathlib import Path
import pg5388_metrics_schema_correction as correction


class CanonicalFields(unittest.TestCase):
    def test_result_source_and_hash_chain_mismatch_cannot_become_new_measurements(self):
        original={'eventId':'PGPT-20261008-1231','groupId':'fixture','eventType':'GROUP_END',
            'timeJST':'original-time','source':'a'*40,'primaryWbs':'WBS-P018-04.03',
            'costRevision':'frozen','estimateRevisionSha256':'b'*64,
            'groupStartEstimatePp':{'low':0.8,'base':2.5,'high':6}}
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            paths=[root/(correction.BASE+name+'/manifest.json') for name in correction.RESULTS[1231]]
            for path in paths:path.parent.mkdir(parents=True)
            proof={'source':'a'*40,'actualExit':0,'targetClassCounters':{}}
            paths[1].write_text(json.dumps(proof))
            public={'productionCandidateSource':'a'*40,'actualExit':0,'tests':1,'suites':1,
                'fixtureBytecodeProofSha256':correction.sha(paths[1].read_bytes())}
            paths[0].write_text(json.dumps(public))
            classified={'source':'a'*40,'qualificationSha256':correction.sha(paths[0].read_bytes()),
                'classificationCounts':{'FIXED_LIMITED':1}}
            paths[2].write_text(json.dumps(classified))
            values=correction.correction(original,b'original\n',{'fixture':original},root)
            self.assertTrue(values['technicalMeasurementDelta']['coverageBySource'][0]['measurementReferenceOnly'])
            self.assertEqual(values['acceptedDelta']['closedIds'],[])
            classified['qualificationSha256']='0'*64;paths[2].write_text(json.dumps(classified))
            with self.assertRaises(ValueError):correction.correction(original,b'original\n',{'fixture':original},root)
            public['productionCandidateSource']='foreign';paths[0].write_text(json.dumps(public))
            with self.assertRaises(ValueError):correction.correction(original,b'original\n',{'fixture':original},root)

    def test_original_extensions_unchanged_and_group_end_uses_registered_checkpoint(self):
        values={'primaryWbs':'WBS-P018-01','componentWbs':['WBS-P018-05','WBS-P018-06'],
            'groupStartEstimatePp':{'low':0.5,'base':1.5,'high':4},'actualAllocatedPp':None}
        before=copy.deepcopy(values)
        actual,event=correction.metrics.canonical_fields(values,'GROUP_END')
        self.assertEqual(values,before)
        self.assertEqual(event,'CHECKPOINT')
        self.assertEqual(actual['wbsLeafIds'],['WBS-P018-01','WBS-P018-05','WBS-P018-06'])
        self.assertEqual(actual['estimateAtGroupStartPp'],before['groupStartEstimatePp'])
        self.assertIsNone(actual['actualAllocatedPp'])
        self.assertEqual(actual['componentAdditionalBudgetPp'],0)

    def test_conflicting_or_invalid_frozen_columns_are_refused(self):
        for estimate in ({'low':2,'base':1,'high':3},{'low':False,'base':1,'high':3},
            {'low':-1,'base':1,'high':3},{'low':1,'base':2}):
            with self.assertRaises(ValueError):correction.metrics.canonical_fields({'groupStartEstimatePp':estimate},'CHECKPOINT')
        with self.assertRaises(ValueError):
            correction.metrics.canonical_fields({'primaryWbs':'WBS-P018-01','wbsLeafIds':['WBS-P018-05']},'CHECKPOINT')
        with self.assertRaises(ValueError):
            correction.metrics.canonical_fields({'groupStartEstimatePp':{'low':1,'base':2,'high':3},
                'estimateAtGroupStartPp':{'low':1,'base':2,'high':4}},'CHECKPOINT')

    def test_original_start_value_and_time_not_reestimated_or_backdated(self):
        original={'eventId':'PGPT-20261008-1232','groupId':'fixture','eventType':'GROUP_START',
            'timeJST':'original-time','source':'a'*40,'primaryWbs':'WBS-P018-01',
            'componentWbs':['WBS-P018-05'],'costRevision':'frozen','estimateRevisionSha256':'b'*64,
            'groupStartEstimatePp':{'low':0.5,'base':1.5,'high':4},'quotaUsedPercent':19,'quotaRemainingPercent':81}
        actual=correction.correction(original,b'original\n',{'fixture':original})
        self.assertEqual(actual['originalTimeJST'],'original-time')
        self.assertEqual(actual['frozenEstimateFromEventId'],original['eventId'])
        self.assertIsNone(actual['attempt']);self.assertIsNone(actual['actualAllocatedPp'])
        self.assertIsNone(actual['quotaBefore']['fetchedAtJST'])
        self.assertEqual(actual['acceptedDelta']['closedIds'],[])
        self.assertEqual(actual['technicalMeasurementDelta']['newClosedIds'],[])
        wrong=copy.deepcopy(original);wrong['groupStartEstimatePp']['base']=3
        with self.assertRaises(ValueError):correction.correction(original,b'original\n',{'fixture':wrong})


if __name__=='__main__':unittest.main()
