import unittest
from pyflakes.api import check
import pg4132_signed_phase_invariant as subject


class SignedPhaseTest(unittest.TestCase):
    def test_exact_qualified_closure_and_no_service_or_db_authority(self):
        raw=subject.source()
        self.assertEqual(0,check(raw,'<signed inventory>'))
        for token in ['os.O_NOFOLLOW','os.pread(','metadata(fd)','attributes(fd)','held.capture()','finally:held.close()']:
            self.assertTrue(token in raw)
        for token in ['subprocess','systemctl','kill(','psql','database','terminate_once']:
            self.assertFalse(token in raw)

    def test_full_187_manifest_and_both_materials_each_call_closed_no_skips(self):
        calls=[]
        class Inventory:
            def __init__(self,root,records,owner):
                calls.append(('construct',root,len(records),owner));self.held=[(1,None,'fixed',(),())]
            def open(self):calls.append('open-closed-release')
            def open_file(self):calls.append('open-material')
            def capture(self):calls.append('capture')
            def close(self):calls.append('close')
        ns={};exec(subject.source(),ns);ns['HeldInventory']=Inventory
        records=[{'path':'file'+str(i),'size':1,'sha256':'a'*64}for i in range(187)]
        materials=[{'path':'/fixed/pin.der','size':44,'sha256':'b'*64},{'path':'/private/signature','size':64,'sha256':'c'*64}]
        for i in range(2):self.assertTrue(ns['verify']('/release',records,b'independent manifest',materials))
        self.assertEqual(2,calls.count('open-closed-release'));self.assertEqual(4,calls.count('open-material'))
        self.assertEqual(6,calls.count('capture'));self.assertEqual(6,calls.count('close'))
        self.assertEqual([189,1,1,189,1,1],[c[2]for c in calls if type(c)is tuple])

    def test_inventory_failure_acl_or_close_failure_never_returns_success(self):
        for failure in ['capture','ACL','close']:
            closed=[]
            class Inventory:
                def __init__(self,*unused):self.held=[(1,None,'fixed',(),('ACL',)if failure=='ACL'else())]
                def open(self):pass
                def capture(self):
                    if failure=='capture':raise OSError('independent digest drift')
                def close(self):
                    closed.append(True)
                    if failure=='close':raise OSError('independent close failure')
            ns={};exec(subject.source(),ns);ns['HeldInventory']=Inventory
            records=[{'path':'file'+str(i),'size':1,'sha256':'a'*64}for i in range(187)]
            with self.assertRaises((OSError,ValueError)):ns['verify']('/release',records,b'manifest',[{'path':'/p/a','size':1,'sha256':'b'*64}]*2)
            self.assertEqual([True],closed)


if __name__=='__main__':unittest.main()
