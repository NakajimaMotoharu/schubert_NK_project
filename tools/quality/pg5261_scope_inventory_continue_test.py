import unittest
import pg5261_scope_inventory_continue as role


class PriorWhitelist(unittest.TestCase):
    def test_fixed_reason_never_claims_a_hardcoded_test_count(self):
        names=role.inventory.ROOT_FIXED|role.inventory.CALLER_FIXED|{'LinuxExecDescriptors.java'}
        rows=[{'path':'p/'+name,'sites':[{}],'sourceSha256':'unused'} for name in names]
        counts=role.inventory.classify(rows,lambda path:b'ResourceScope.use(' if path.endswith('LinuxExecDescriptors.java') else b'',evidence_ref='current-source-qualified/manifest.json')
        self.assertEqual(counts,{'FIXED_LIMITED':7,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':0})
        for row in rows:
            site=row['sites'][0]
            self.assertEqual(site['retestEvidence'],'current-source-qualified/manifest.json')
            self.assertNotIn('222',site['reviewReason'])
            self.assertFalse(site['fixed'])

    def row(self,path,*classes):
        return {'path':path,'sites':[{'classification':value} for value in classes]}

    def test_only_uniform_fixed_rows_supply_candidate_names(self):
        self.assertEqual(role.fixed_names([self.row('p/A.java','FIXED_LIMITED','FIXED_LIMITED'),
            self.row('p/B.java','UNKNOWN'),self.row('p/C.java','NON_APPLICABLE_BORROWED')]),{'A.java'})

    def test_duplicate_basename_partial_unknown_empty_or_unrecognized_are_rejected(self):
        for rows in ([self.row('a/A.java','FIXED_LIMITED'),self.row('b/A.java','UNKNOWN')],
            [self.row('p/A.java','FIXED_LIMITED','UNKNOWN')],[self.row('p/A.java')],
            [self.row('p/A.java','UNREVIEWED')]):
            with self.assertRaises(ValueError):role.fixed_names(rows)


if __name__=='__main__':unittest.main()
