"""Literal canonical manifest vectors, immutable handles and approved skip negative matrix."""
import copy
import unittest
from pg1259_fresh_backup_manifest_oracle_test import IndependentFreshBackupManifestTest
from pg2066_retained_backup_handle_oracle import source


class Retained(unittest.TestCase):
    def setUp(self):
        self.f=IndependentFreshBackupManifestTest();self.f.setUp()
        self.oracle={};exec(source(),self.oracle)

    def rows(self):
        rows=copy.deepcopy(self.f.rows)
        for original in self.f.rows:
            skip=dict(original,id=original['id']+10,attempt=2,status='SKIPPED',error_code='ALREADY_SUCCESSFUL',error_summary='step already successful for business date',started_at='2026-10-11T01:00:00.000000+00:00',ended_at='2026-10-11T01:00:00.000000+00:00')
            for k in ['target_count','success_count','failure_count','byte_count']:skip[k]=0
            rows.append(skip)
        return rows

    def verify(self,rows):return self.oracle['verify'](self.f.raw(self.f.manifest),self.f.files,self.f.profile,rows,self.f.run,self.f.cut,self.f.recipient)

    def test_retained_exact_handle_and_later_skip(self):
        self.assertEqual('20261011-050327-'+self.f.run,self.verify(self.rows())['directoryName'])
        self.assertTrue(self.verify(self.f.rows)['twoCompleteDbHandlesAndCountBytesMatched'])
        for key,value in [('id',625),('attempt',1),('status','FAILED'),('business_date','2026-10-12'),('error_code',None),('error_summary','other'),('target_count',1),('success_count',1),('failure_count',1),('byte_count',1),('started_at','2026-10-10T19:00:00.000000+00:00'),('ended_at','2026-10-11T01:00:01.000000+00:00')]:
            rows=self.rows();rows[2][key]=value
            with self.assertRaises(ValueError):self.verify(rows)
        with self.assertRaises(ValueError):self.verify(self.rows()+[self.rows()[0]])


if __name__=='__main__':unittest.main()
