"""Independent literal pins/date/clock/foreign guards, no VM effects."""
import unittest
import pg968_current_terminal_final as p
import pg969_current_native_counter as n
class Test(unittest.TestCase):
    def test_current_terminal_pins(self):
        raw=p.source()
        for x in ('pg963_current_stop_binding','pg960-completed-readonly-v1','pg932-manifest.sig','complete_configuration('):
            self.assertIn(x,raw,'missing '+x)
        self.assertNotIn('pg875',raw);self.assertNotIn('pg877',raw)
    def test_independent_host_and_actual_tuple_pins(self):
        raw=n.code({'synthetic.exec':'0'*64},'1'*64,'2'*64,202580374989)
        for x in ('40ef6e894573d2ffab1d1732124960f9c98d5f97','pg926-body-six-host-v1','4ae512d3b3a8e85d81fcd8e9ef04279fff58114c42e9b158adc61299d8211fdf',"tests']==3560",'201380374989','202580374989','0bb4d6f3b9e74cdc91c553748a4cd018','213904','historicalNativeNotImported'):
            self.assertIn(x,raw,'missing '+x)
        for old in ('pg857','pg879','pg875','e01612fcd7f2752df5ae0836b78538fd5e87f120'):self.assertNotIn(old,raw)
if __name__=='__main__':unittest.main()
