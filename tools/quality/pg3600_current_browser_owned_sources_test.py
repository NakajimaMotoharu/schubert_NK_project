"""Actual final owned roles and downstream immutable Browser data, no VM operation."""
import ast
import json
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg3600_current_browser_owned_sources as p
import pg3604_current_browser_owned_dispatch as dispatch


class CurrentOwned(unittest.TestCase):
    def test_all_actual_emitted_current_roles(self):
        values=p.sources();self.assertEqual(15,len(values))
        for name,raw in values.items():
            if name.endswith('.py'):self.assertEqual(0,check(raw,'<current Browser owned '+name+'>'))
        java=values['Pg3600NativeStop.java']
        self.assertIn('LABEL="PG3420";Pg387TrustedDeployment.STEM="pg3420"',java)
        self.assertIn('784b8508-7dcd-415d-9b85-3855f4335a8c',java)
        self.assertIn('2026-10-15T20:35:59.251066Z',java)
        receipt={};exec(compile(values['pg3600_parent_receipt.py'],'<actual new receipt>','exec'),receipt)
        self.assertEqual('3f924cbb70ca4800bf9e8871aa6ccd00',receipt['BINDING']['invocation'])
        self.assertEqual(94137764253,receipt['BINDING']['start'])
        run=dispatch.namespace()['run_source']()
        self.assertIn('Pg3600NativeStop stop',run)
        self.assertEqual('/home/ubuntu/pg3604-current-browser-owned-stage-v1',dispatch.namespace()['REMOTE'])
        self.assertIn('repr(GUEST)',run)

    def test_actual_downstream_post_preserves_real_chain(self):
        raw=dispatch.namespace()['post_payload']()
        oracle=next(ast.literal_eval(n.value)for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ORACLE'for t in n.targets))
        chain=next(ast.literal_eval(n.value)for n in ast.parse(oracle).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='CHAIN'for t in n.targets))
        cases=W/'pg3580-current-browser-business-actual-v1/cases'
        expected={name:json.loads((cases/file).read_bytes())for name,file in [('before','before-rows.private.json'),('after','after-rows.private.json'),('context','context.private.json')]}
        self.assertEqual(expected,chain)


if __name__=='__main__':unittest.main()
