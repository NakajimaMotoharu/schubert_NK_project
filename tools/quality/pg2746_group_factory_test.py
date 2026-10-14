"""Full/native factory literal guards only; no run/deploy/start authority."""
import inspect
import types
import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg2744_backup_admission_group_full_six as full
import pg2746_backup_admission_native_qualification as native
import pg2642_wire_oracle_native_qualified as bridge


class Factories(unittest.TestCase):
    def test_reason_is_current_group_before_any_dispatch(self):
        captured=[]
        def constants(code):
            for value in code.co_consts:
                if isinstance(value,types.CodeType):constants(value)
                else:captured.append(value)
        def capture(code,namespace):
            constants(code)
            namespace['main']=lambda:0
        with patch.object(full,'exec',capture,create=True):
            self.assertEqual(0,full.main())
        self.assertIn('3666 retained plus three independently qualified Backup admission methods; unchanged Main/resources;541suite1643Main',captured)
        self.assertIn('Three independent Backup publication/retention/pending methods require one grouped full3669 integration; actual ownsource PG2722 native retained without recapture',captured)
        self.assertNotIn('3664 retained plus two mandatory OperationPostScript tests; new JS/fourtemplate resources;541suite1643Main',captured)

    def test_complete_retained_native_namespace_no_excluded_members(self):
        raw=native.server()
        for literal in ['transfer/PG2722-native-input.tar','runs/PG2746-native-v1','source-full-PG2694','source-full-PG2744',
                        'require(images[0]==images[1])','require(identical_main==1643)',"v['qualifiedFull']=QUALIFIED"]:
            self.assertIn(literal,raw)
        self.assertNotIn('SSH+',raw)
        self.assertNotIn('a79b45b5858a186fa82bec1ff36882271ab996a4',raw)
        code='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA=""\nOLD_JARS={}\nOLD_FULL={}\nOLD_NATIVE_SHA=""\nQUALIFIED={}\nSOURCE=""\n'+inspect.getsource(bridge.entry().__globals__['coordinates'])+'\n'+raw
        self.assertEqual(0,check(code,'<whole ownsource native>'))
        compile(code,'<whole retained native>','exec')


if __name__=='__main__':unittest.main()
