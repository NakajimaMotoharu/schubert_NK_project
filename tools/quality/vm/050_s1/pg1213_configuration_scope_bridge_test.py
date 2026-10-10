import unittest
from pg1213_configuration_scope_bridge import extend


class ScopeTest(unittest.TestCase):
    def fixture(self):
        legacy='ExecStart,DropInPaths,ReadWritePaths,User,Group,SupplementaryGroups,NoNewPrivileges,ProtectSystem,ProtectHome,PrivateTmp,PrivateDevices,RestrictSUIDSGID,CapabilityBoundingSet,AmbientCapabilities,UMask,LimitCORE,TimeoutStartUSec,TimeoutStopUSec,MemoryMax,TasksMax'.split(',')
        state='Id,Type,Restart,RemainAfterExit,KillMode,SendSIGKILL'.split(',')
        added='After,ExecStop,FragmentPath,ReadOnlyPaths,Requires,RestrictAddressFamilies'.split(',')
        old={k:'literal-'+k for k in legacy};s={k:'literal-'+k for k in state};return old,dict(old,**s,**{k:'literal-'+k for k in added}),s

    def test_exact_full_scope_historical_and_state_preserved(self):
        old,current,state=self.fixture();value,summary=extend(old,current,state)
        self.assertEqual(value,current);self.assertEqual(summary['newlyObservedFields'],['After','ExecStop','FragmentPath','ReadOnlyPaths','Requires','RestrictAddressFamilies'])
        self.assertFalse(summary['historicalFull32Accepted'])
        for k in current:
            bad=dict(current);del bad[k]
            with self.assertRaises(ValueError):extend(old,bad,state)
            bad=dict(current);bad[k]=None
            with self.assertRaises(ValueError):extend(old,bad,state)
        for k in [*old,*state]:
            bad=dict(current);bad[k]='foreign'
            with self.assertRaises(ValueError):extend(old,bad,state)
        with self.assertRaises(ValueError):extend(old,dict(current,unknown='x'),state)


if __name__=='__main__':unittest.main()
