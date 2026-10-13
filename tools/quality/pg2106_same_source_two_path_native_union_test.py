"""Independent two campaigns/latest closing selector and actual server full namespace."""
import copy
import inspect
import unittest
from pyflakes.api import check
from pg1271_current_native_gap import coordinates
from pg2106_same_source_two_path_native_union import select,server,SOURCE


class Union(unittest.TestCase):
    def fixture(self):
        return [{'productionSource':SOURCE,'qualifiedFull':{'independent':'same'},'libraries':{'one':'same'},'selected':[{'relative':str(i)+'.exec','unit':'literal'}for i in range(8)]+[{'relative':str(n)+'.closing.exec','unit':'schubert-nk-inbox-inspector.service'},{'relative':str(n)+'.terminal.exec','unit':'schubert-nk-inbox-inspector.service'}]}for n in range(2)]

    def test_latest_only_and_no_different_source_or_helpers(self):
        inputs=self.fixture();points=select(inputs);self.assertEqual(18,len(points));self.assertFalse(any(v['relative'].endswith('.terminal.exec')for _,_,v in points))
        for key,value in [('productionSource','foreign'),('qualifiedFull',{}),('libraries',{})]:
            bad=copy.deepcopy(inputs);bad[1][key]=value
            with self.assertRaises(ValueError):select(bad)
        bad=copy.deepcopy(inputs);bad[1]['selected'].pop()
        with self.assertRaises(ValueError):select(bad)

    def test_actual_server_class_byte_session_and_output_contract(self):
        raw='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="fixed"\n'+inspect.getsource(coordinates)+'\n'+server()
        self.assertEqual(0,check(raw,'<actual two-path full server>'))
        for marker in ["len(v['selected'])==18","len({session['sessionIdSha256']for session in sessions})==18",'PG2106-native-v1','PG2106-native-input.tar','inspectorLatestClosingOnlyPerProcess','formalCollectorAccepted']:
            self.assertTrue(marker in raw,marker)


if __name__=='__main__':unittest.main()
