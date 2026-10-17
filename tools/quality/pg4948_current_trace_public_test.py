"""Independent four-counter owner/inner-family literal vectors; no blind dropped scope."""
import copy
import unittest
from pyflakes.api import checkPath
import pg4948_current_trace_public as target


class OwnerCounters(unittest.TestCase):
    def fixture(self):
        counts=lambda n:{k:[n,5]for k in target.COUNTERS}
        return [{'kind':'JAVA','module':'m','class':'a/A','owner':'ownerA'},
                {'kind':'JAVA','module':'m','class':'a/B','owner':'ownerB'},
                {'kind':'JAVA','module':'m','class':'a/C','owner':'ownerB'}],{
                  'm':{'a/A':counts(0),'a/B':counts(1),'a/C':{k:[0,0]for k in target.COUNTERS}}}

    def test_literal_owner_counts_declared_zero_not_accepted(self):
        artifacts,data=self.fixture();result=target.owner_measurement(artifacts,data)
        self.assertEqual({'TECHNICAL_COUNTERS_CLOSED':1,'TECHNICAL_GAPS':1},result['counts'])
        self.assertEqual({k:1 for k in target.COUNTERS},result['remaining'])
        self.assertEqual((2,3,1),(result['javaOwners'],result['javaFamilies'],result['zeroCounterFamilies']))
        self.assertFalse(result['rows']['ownerA']['accepted']);self.assertIsNone(result['effortPercent'])

    def test_missing_duplicate_negative_bool_and_unmapped_gap_refused(self):
        artifacts,data=self.fixture()
        for change in (lambda a,d:a.append(a[0]),lambda a,d:d['m'].pop('a/A'),
                       lambda a,d:d['m']['a/B'].update(LINE=[-1,5]),
                       lambda a,d:d['m']['a/B'].update(LINE=[False,5]),
                       lambda a,d:d['m'].update(unowned={k:[1,1]for k in target.COUNTERS})):
            a,d=copy.deepcopy(artifacts),copy.deepcopy(data);change(a,d)
            with self.assertRaises(ValueError):target.owner_measurement(a,d)
        self.assertEqual(0,checkPath(target.__file__));self.assertEqual(0,checkPath(__file__))

    def test_retained_characterization_is_unmeasured_not_zero_or_accepted(self):
        artifacts,data=self.fixture()
        artifacts.append({'kind':'JAVA','module':'characterization','class':'dev/codex/schubert/characterization/ArtifactComparator',
            'path':'program/characterization/src/main/java/dev/codex/schubert/characterization/ArtifactComparator.java','owner':'WBS-P020-01'})
        result=target.owner_measurement(artifacts,data);row=result['rows']['WBS-P020-01']
        self.assertEqual('SEPARATE_CHARACTERIZATION_EVIDENCE_REQUIRED',row['status'])
        self.assertIsNone(row['missed']);self.assertIsNone(row['covered']);self.assertFalse(row['accepted'])
        self.assertEqual(1,len(row['unmeasuredFamilies']));self.assertEqual({k:1 for k in target.COUNTERS},result['remaining'])
        self.assertEqual('SIX_PRODUCTION_MODULES_ONLY',result['remainingScope'])


if __name__=='__main__':unittest.main()
