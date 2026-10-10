"""Independent Linux-lock literals and actual cold profile assembly, no VM side effects."""
import ast
import copy
import os
import stat
import unittest
from pg1023_cold_contract import owned_flocks,owned_peer_sql
from pg1023_cold_readback_sources import guest,files

class ColdContract(unittest.TestCase):
    def setUp(self):
        self.meta={'maintenance.lock':[os.makedev(8,1),7,0,0,stat.S_IFREG|0o600,1,0,11,12],
          'startup-admission.lock':[os.makedev(8,1),8,0,0,stat.S_IFREG|0o600,1,0,13,14]}
        self.lines=['1: FLOCK ADVISORY WRITE 121 08:01:7 0 EOF','2: FLOCK ADVISORY WRITE 121 08:01:8 0 EOF']
    def test_both_locks_same_parent_and_unrelated_ignored(self):
        self.assertEqual({'maintenance.lock':1,'startup-admission.lock':1},owned_flocks(self.lines,self.meta,121))
        self.assertEqual({'maintenance.lock':1,'startup-admission.lock':1},owned_flocks(self.lines+['3: FLOCK ADVISORY READ 9 08:01:10 0 EOF'],self.meta,121))
    def test_each_lock_missing_duplicate_foreign_read_or_waiter_refused(self):
        for index in (0,1):
            for changed in (self.lines[:index]+self.lines[index+1:],self.lines+[self.lines[index]],
              [v.replace('121','122')if i==index else v for i,v in enumerate(self.lines)],
              [v.replace('WRITE','READ')if i==index else v for i,v in enumerate(self.lines)],
              [v.replace(': FLOCK',': -> FLOCK')if i==index else v for i,v in enumerate(self.lines)]):
                with self.subTest(index=index,changed=changed):
                    with self.assertRaises(ValueError):owned_flocks(changed,self.meta,121)
    def test_null_unknown_and_inode_alias_refused(self):
        for lines,meta,pid in ((None,self.meta,121),(self.lines,None,121),(self.lines,self.meta,None),(self.lines,self.meta,True),(self.lines+[None],self.meta,121)):
            with self.assertRaises(ValueError):owned_flocks(lines,meta,pid)
        for field,value in ((2,1),(4,stat.S_IFREG|0o644),(5,2),(6,1),(1,7)):
            m=copy.deepcopy(self.meta);m['startup-admission.lock'][field]=value
            with self.assertRaises(ValueError):owned_flocks(self.lines,m,121)
    def test_malformed_target_kernel_record_refused(self):
        for line in ('1: FLOCK ADVISORY WRITE 121 wrong 0 EOF','1: FLOCK ADVISORY WRITE 121 08:01:7 0','1: FLOCK ADVISORY WRITE 121 08:01:7 1 EOF'):
            with self.assertRaises(ValueError):owned_flocks([line,self.lines[1]],self.meta,121)
    def test_db_pid_boundary_and_actual_pulse_states(self):
        for v in (None,True,-1,1,'121',2147483647):
            with self.assertRaises(ValueError):owned_peer_sql(v)
        for v in (0,121,2147483646):
            sql=owned_peer_sql(v)
            self.assertEqual(3,sql.count(';'))
            self.assertIn('pid<>'+str(v)+';',sql)
            self.assertIn("application_name='PG243-cold-empty'",sql)
            self.assertIn("state in('idle in transaction','active')",sql)
            self.assertIn("mode='ExclusiveLock'and granted",sql)
            self.assertNotIn('insert ',sql.lower())
    def test_profile_has_no_old_invocation_or_mutation_entry(self):
        raw=guest();tree=ast.parse(raw)
        snap=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
        names={n.func.id for n in ast.walk(snap)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)}
        self.assertIn('owned_flocks',names);self.assertIn('owned_peer_sql',names)
        self.assertIn("OWNER_BACKEND=0;post=read_pair()",raw)
        self.assertIn("start[3:]==('n/a','n/a','0','(null)','0/0')",raw)
        java=files()['Pg1023ColdOwnedReadback.java']
        for forbidden in ('.invalidate(','.revoke(','.runFixture(','.readMaintenanceOwner(','.startUnit('):self.assertNotIn(forbidden,java)
        self.assertLess(java.index('database.rollback()'),java.index('database.close()'))
        self.assertLess(java.index('lease.confirmClosed()'),java.index('refs.check("run")'))
        self.assertLess(java.index('refs.check("run")'),java.index('refs.release()'))
        self.assertIn('session.observeStartup(ORIGINAL)',java)
        self.assertNotIn('new StartupPermitFiles',java)

if __name__=='__main__':unittest.main()
