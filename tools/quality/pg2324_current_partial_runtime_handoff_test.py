import ast
import unittest
from pg2324_current_partial_runtime_handoff import payload,PROOF_SHA


class CurrentPartial(unittest.TestCase):
    def test_complete_partial_binding_and_owned_child_parent_order(self):
        raw=payload()
        for value in [PROOF_SHA,'terminate(98516,1656547','terminate(98485,1656317',"expected['partialRuntimeFileVerified']is True and expected['reloadNotReserved']is True",'888ee8561e9c25da302470c2561cdbf65cbf10cdebf668f7196f27b485bc5035']:
            self.assertTrue(value in raw,'missing actual partial boundary '+value)
        self.assertLess(raw.index('terminate(98516,1656547'),raw.index('terminate(98485,1656317'))
        self.assertFalse(any(isinstance(n,ast.Attribute)and n.attr=='SIGKILL'for n in ast.walk(ast.parse(raw))))
        for value in ['96640','96671','96669','daemon-reload']:
            self.assertFalse(value in raw,'foreign/mutation survived '+value)


if __name__=='__main__':unittest.main()
