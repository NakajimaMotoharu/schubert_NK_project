import unittest
from pg1342_published_current_native_gap import source

class CurrentNativeGapSourceTest(unittest.TestCase):
    def test_actual_fourteen_current_exec_and_no_exclusions_or_vm_actions(self):
        code=source();compile(code,'<actual coordinates>','exec')
        for part in ['pg1341-published-eight-native-v1','pg1279-held-channel-six-host-v1','len(data)==14',"'currentNativeExecCount':8",'exclusions0','newVmOperations0','classMismatch0=true']:
            self.assertTrue(part in code,part)
        for old in ['pg1258','pg1018',"'currentNativeExecCount':10"]:self.assertTrue(old not in code,old)

if __name__=='__main__':unittest.main()
