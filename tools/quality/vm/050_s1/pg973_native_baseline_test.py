"""Independent four-counter local-vs-union oracle; no actual native/session fabrication."""
import ast,copy,unittest
import pg972_current_native_v2 as p
KEYS=('LINE','METHOD','CLASS','BRANCH')
def generated():return p.code({'fixture.exec':'0'*64},'1'*64,'2'*64,202927375873)
def oracle(local,host,expected):
    raw=generated();node=next(n for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Assert)and ast.get_source_segment(raw,n).startswith('assert all(moduleLocal'))
    env={'moduleLocal':{'bootstrap':local},'hostOnly':{'bootstrap':host},'m':'bootstrap','host_record':{'moduleResults':{'bootstrap':{'hostCounters':expected}}}}
    statement=ast.Module(body=[node],type_ignores=[]);exec(compile(statement,'<literal local baseline oracle>','exec'),env)
class Test(unittest.TestCase):
    def test_actual_cross_module_shape_is_distinct_not_changed_expected(self):
        local={k:{'covered':10,'missed':2}for k in KEYS};host=copy.deepcopy(local);host['LINE']={'covered':11,'missed':1};host['METHOD']={'covered':11,'missed':1}
        oracle(local,host,copy.deepcopy(local))
        with self.assertRaises(AssertionError):oracle(host,host,local)
    def test_every_local_counter_mismatch_is_refused(self):
        expected={k:{'covered':10,'missed':2}for k in KEYS}
        for key in KEYS:
            wrong=copy.deepcopy(expected);wrong[key]={'covered':11,'missed':1}
            with self.assertRaises(AssertionError):oracle(wrong,expected,expected)
    def test_same_source_frozen_xml_and_new_slot(self):
        raw=generated()
        for x in ('pg972-current-eight-native-v2','40ef6e894573d2ffab1d1732124960f9c98d5f97','classByteMismatch','moduleLocalCounters',"[executions[modules.index(m)]]",'executions+streams','pg926-body-six-host-v1','4ae512d3b3a8e85d81fcd8e9ef04279fff58114c42e9b158adc61299d8211fdf'):
            self.assertIn(x,raw,'missing '+x)
        self.assertNotIn('pg969-current-eight-native-v1',raw)
if __name__=='__main__':unittest.main()
