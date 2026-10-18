import unittest
from pyflakes.api import checkPath
import pg5428_cost_owner_correction as entry


class CostOwner(unittest.TestCase):
    def test_one_start_budget_and_original_source_time_remain_not_exclusive_cost(self):
        start={'eventId':entry.TARGETS[0],'groupId':'V4_FACTORY_WHOLE_READONLY','eventType':'GROUP_START',
            'timeJST':'original-time','primaryWbs':'WBS-P018-04.03','source':'a'*40,'run':None,
            'costRevision':'frozen','estimateRevisionSha256':'b'*64,'groupStartEstimatePp':{'low':1,'base':3,'high':8},'sourceEvidenceRefs':['fixture']}
        for identifier in entry.TARGETS:
            original=dict(start,eventId=identifier)
            result=entry.values(original,b'original\n',start)
            self.assertEqual(result['primaryWbs'],'WBS-K01.01');self.assertEqual(result['componentWbs'],['WBS-P018-04.03'])
            self.assertEqual(result['originalTimeJST'],'original-time');self.assertEqual(result['source'],'a'*40)
            self.assertEqual(result['groupStartEstimatePp'],start['groupStartEstimatePp'])
            self.assertEqual(result['groupBudgetCount'],1);self.assertEqual(result['newBudgetAddedPp'],0)
            self.assertIsNone(result['actualSpentPp']);self.assertIsNone(result['actualAllocatedPp'])
            self.assertEqual(original['primaryWbs'],'WBS-P018-04.03')
        for key,value in [('eventId','foreign'),('groupId','foreign'),('source','foreign'),('groupStartEstimatePp',{'low':1,'base':2,'high':8})]:
            invalid=dict(start);invalid[key]=value
            with self.assertRaises(ValueError):entry.values(invalid,b'original\n',start)
        for path in (entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
