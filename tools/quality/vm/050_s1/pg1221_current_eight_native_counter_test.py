import unittest
from pg1221_current_eight_native_counter import code,catalog


class NativeBindingTest(unittest.TestCase):
    def test_whole_actual_host_namespace_and_strict_new_provenance(self):
        s=code({});env={'__name__':'qualified_d5_native_test','__file__':__file__,'CAPACITY':{}}
        exec(compile(s,'<actual isolated native namespace>','exec'),env)
        self.assertEqual(env['SOURCE'],'d5b00104280028d9ea81b44c1d1c805f3c2861ed')
        compile(env['PAYLOAD'],'<actual native readback>','exec')
        compile(catalog(),'<actual native catalog>','exec')
        for part in ['pg1018-stream-six-host-v2',"tests']==3563",'pg1218-stop-v1.exit','pg1220-full32-terminal-post-v1',"'requiredPlannedStreams':9", "'wholeNativeAccepted':False"]:
            self.assertTrue(part in s,part)
        for old in ['40ef6e894573d2ffab1d1732124960f9c98d5f97','pg926-body','cc9ed874','0bb4d6f3']:
            self.assertFalse(old in s,old)


if __name__=='__main__':unittest.main()
