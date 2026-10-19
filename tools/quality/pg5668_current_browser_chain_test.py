"""Independent current0ea guest-clock chain/immutable Root fixtures; no VM actions."""
import ast
import copy
import unittest
from pyflakes.api import check,checkPath
from pg5652_current_acceptance_test import independent_observed
from pg5520_guest_clock_contract_test import context
from pg3136_browser_rows_oracle_test import fixture
import pg5660_current_browser_ready as ready
import pg5662_current_same_owner_browser as actual
import pg5664_current_browser_composite as entry
import pg5666_current_parent_projection as projection


class Browser(unittest.TestCase):
    def test_driver_uses_guest_clock_and_no_old_failed_history(self):
        raw=actual.entry_source();compile(raw,'<new0ea Browser driver>','exec')
        self.assertIn('tools/quality/pg5520_guest_clock_contract.py',raw)
        self.assertNotIn('tools/quality/pg3136_browser_rows_oracle.py',raw)
        self.assertIn('legacyFailedPrefixImported=False',raw);self.assertNotIn('previousFailedRunPreserved=',raw)
        self.assertIn('rootReplayed=False',raw);self.assertEqual(3,len(ready.namespace()['ORACLES']))
        self.assertEqual(ready.SOURCE,entry.admission.SOURCE);self.assertIn('tools/quality/pg5668_current_browser_chain_test.py',ready.PINNED)

    def test_root_guard_oracle_and_literal_chain_are_immutable(self):
        raw=entry.root.payload(independent_observed(),'a'*64)
        before,after=fixture();chain={'before':before,'after':after,'context':context()}
        value=entry.compose(raw,chain,'b'*64);oracle=entry.literal(value,'ORACLE')
        self.assertEqual(check(value,'<new0ea complete Browser seal>'),0)
        self.assertEqual(entry.literal(value,'GUARD'),entry.literal(raw,'GUARD'))
        self.assertEqual(entry.literal(oracle,'ROOT_ORACLE'),entry.literal(raw,'ORACLE'))
        self.assertEqual(entry.literal(oracle,'CHAIN'),chain)
        self.assertIn('clock_ns[\'verify_context\'](context)',oracle)
        self.assertNotIn('FAILED_HOST_CLOCK_BROWSER',oracle)
        self.assertIn(entry.root.SLOT+'/before.private.json',oracle)
        self.assertIn(entry.SLOT,value)
        for change in('missing','domain','reversed'):
            bad=copy.deepcopy(chain)
            if change=='missing':bad['context'].pop('lowerClock')
            elif change=='domain':bad['context']['clockDomain']='host-estimate'
            else:bad['context']['upperClock']['hostStartNanos']=-1
            with self.assertRaises(ValueError):entry.compose(raw,bad,'b'*64)

    def test_projection_is_current_source_read_only_and_static(self):
        raw=projection.payload('a'*64);self.assertIn(entry.SLOT,raw);self.assertIn(entry.admission.SOURCE,raw)
        self.assertNotIn('systemctl',raw);self.assertEqual(check(raw,'<current typed18>'),0)
        for p in(ready.__file__,actual.__file__,entry.__file__,projection.__file__,__file__):self.assertEqual(checkPath(p),0)
        tree=ast.parse(raw);self.assertTrue(tree.body)


if __name__=='__main__':unittest.main()
