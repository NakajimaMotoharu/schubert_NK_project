import unittest
from pg1475_failed_publication_owner_observation import payload,within_root_period,JOURNAL


class OwnerObservationTest(unittest.TestCase):
    def test_type_scoped_actual_pid1_oracle_refuses_wrong_generation_or_missing_receipt(self):
        # Execute just the actual pure predicate segment, with independent
        # systemd record fixtures; no journal/process/DB operation is performed.
        body=JOURNAL[JOURNAL.index('  require(1<=len(records)'):JOURNAL.index('  observations[unit]')]
        body='\n'.join(line[2:]for line in body.splitlines())
        boot='3d69f5af-6bac-46b1-a540-7591c4a79a0d';inv='47be234990bd4aec838648a8f365536f'
        broker='artemis.service';state={'Type':'simple','ExecMainStartTimestampMonotonic':'6366634712'}
        done={'_BOOT_ID':boot.replace('-',''),'_PID':'1','_UID':'0','UNIT':broker,'INVOCATION_ID':inv,
              'MESSAGE_ID':'39f53479d3a045ac8e11786248231fbf','JOB_TYPE':'start','JOB_RESULT':'done','JOB_ID':'13935','__MONOTONIC_TIMESTAMP':'6366636157'}
        def verify(records,current=state):
            def require(value):
                if not value:raise ValueError('independent rejection oracle')
            exec(body,{'records':records,'state':current,'unit':broker,'inv':inv,'BOOT':boot,'require':require,'within_root_period':within_root_period})
        verify([done])
        for record in [dict(done,INVOCATION_ID='a'*32),dict(done,JOB_ID='13936'),dict(done,_UID='1000'),
                       dict(done,JOB_RESULT='failed'),dict(done,__MONOTONIC_TIMESTAMP='7511141318')]:
            with self.assertRaises(ValueError):verify([record])
        for records in [[],[done,done],[dict(done,MESSAGE_ID='7d4958e842da4a758f6c1cdc7b36dcc5')]]:
            with self.assertRaises(ValueError):verify(records)
        for kind in ['exec','oneshot','unknown']:
            with self.assertRaises(ValueError):verify([done],dict(state,Type=kind))

    def test_actual_budget_strict_boundaries_not_extended(self):
        self.assertTrue(within_root_period(6366634712,6366634713))
        for pair in [(5711141318,6366634712),(6366634712,7511141318),
                     (6366634712,6366634712),(6366634712,6366634711),
                     (False,6366634712),(6366634712,None)]:
            self.assertFalse(within_root_period(*pair))

    def test_fixed_publication_only_readonly_and_no_authority(self):
        raw=payload();self.assertNotIn('pg1464-failed-current-capture-v1',raw)
        self.assertIn("'stopRevokeRetirementIssued':False",raw)
        self.assertIn("'brokerStillOwnedProofPending':True",raw)
        self.assertIn("state['ExecMainStatus']=='0'",raw)
        self.assertNotIn("['systemctl','stop'",raw)


if __name__=='__main__':unittest.main()
