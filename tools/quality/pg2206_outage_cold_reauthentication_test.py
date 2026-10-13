import unittest
import pg2206_outage_cold_reauthentication_v2 as p


class ExistingMaintenance(unittest.TestCase):
    def test_exact_preserved_empty_directory_and_negative_contract(self):
        m=[1,1987,0,0,0o40700,2,40,1,1]
        self.assertTrue(p.maintenance_shape(m,[],[],'tmpfs'))
        for index,value in [(2,999),(3,999),(4,0o40755),(4,0o120700),(5,3),(6,60)]:
            v=m.copy();v[index]=value;self.assertFalse(p.maintenance_shape(v,[],[],'tmpfs'))
        for v,n,a,f in [(None,[],[],'tmpfs'),(m,['foreign'],[],'tmpfs'),(m,[],['system.posix_acl_access'],'tmpfs'),(m,[],[],'ext2/ext3')]:
            self.assertFalse(p.maintenance_shape(v,n,a,f))

    def test_full_payload_keeps_all_previous_checks_and_new_only_output(self):
        s=p.payload()
        self.assertIn("for name in ['startup','pt-coverage','backup-request','cleanup-request','expiry-request']:",s)
        for value in ["rows==old['rows'] and len(rows)==24","durable==old['durable']","'oldOwnedStopAccepted':False","'maintenance':m","pg2206-outage-cold-reauthentication-v2"]:self.assertIn(value,s)
        self.assertNotIn('chmod(',s);self.assertNotIn('chown(',s)


if __name__=='__main__':unittest.main()
