import ast
import unittest
from pg2311_current_resume_pair_handoff import payload,PROOF_SHA


class Handoff(unittest.TestCase):
    def test_all_current_identity_fresh_before_reserve_and_single_term_contract(self):
        raw=payload()
        for value in [PROOF_SHA,"fresh_parent(expected['pair']['parent']","terminate(96671,1550259","terminate(96640,1550071","['31']","['90']",'0.1.0-PG2126','same_peer()==fresh[\'peer\']']:
            self.assertTrue(value in raw,'missing fixed handoff boundary: '+value)
        self.assertLess(raw.index('terminate(96671,1550259'),raw.index('terminate(96640,1550071'))
        for value in ['291213','291242','daemon-reload','pg1638-manifest.sig']:
            self.assertFalse(value in raw,'foreign authority survived: '+value)
        self.assertFalse(any(isinstance(n,ast.Attribute)and n.attr=='SIGKILL'for n in ast.walk(ast.parse(raw))))
        self.assertIn('oldCloseUnknown=true',raw)


if __name__=='__main__':unittest.main()
