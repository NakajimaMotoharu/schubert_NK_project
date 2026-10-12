"""Null/unknown/present/missing reference and DDL boundary counterexamples."""
import unittest
from pg1766_next_day_independent_candidates import classify_inbox,older,instant,payload


class Candidates(unittest.TestCase):
    def test_absent_immutable_reference_not_blanket_delete(self):
        row={'message_id':'candidate','request_layout_id':'LGNREQ01','response_layout_id':'LGNRSP01','processing_state':'COMPLETED','result_ref_type':'AUTH_SESSION','owner_user_id':None,'result_ref_uuid':'missing'}
        rows={'schubert.request_inbox':[row],'schubert.auth_sessions':[]}
        self.assertEqual(['candidate'],classify_inbox(rows,['candidate'])['protected'])
        self.assertEqual([],classify_inbox(rows,['candidate'])['deleted'])
        for key,value in [('response_layout_id','UPWRSP01'),('result_ref_type','NONE'),('result_ref_uuid',None),('owner_user_id',7),('processing_state','ERROR')]:
            with self.assertRaises(ValueError):classify_inbox({**rows,'schubert.request_inbox':[{**row,key:value}]},['candidate'])
        with self.assertRaises(ValueError):classify_inbox({**rows,'schubert.auth_sessions':[{'id':'missing'}]},['candidate'])
        with self.assertRaises(ValueError):classify_inbox(rows,['absent'])

    def test_exact_inclusive_session_and_exclusive_inbox_cutoff(self):
        cutoff=instant('2026-10-12T18:20:32.598894Z')
        self.assertTrue(older('2026-10-12T18:20:32.598894Z',cutoff,True))
        self.assertFalse(older('2026-10-12T18:20:32.598894Z',cutoff))
        self.assertFalse(older(None,cutoff,True))
        self.assertIn('actualDbRowsRead',payload())


if __name__=='__main__':unittest.main()
