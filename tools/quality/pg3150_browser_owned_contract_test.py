"""Complete owned-stop source/consumer closure; fixtures are never current acceptance."""
import ast
import json
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg3006_current_resume_owned_sources as historical
import pg3150_browser_business_owned_sources as owned
import pg3154_browser_business_owned_dispatch as dispatch
import pg3156_browser_business_owned_post as post


class OwnedBrowserClosure(unittest.TestCase):
    def test_complete_fifteen_sources_and_actual_new_receipt_role(self):
        # Explicit generation-only fixture: no claim that current Root is done.
        ctx = list(historical.context())
        live = json.loads((W / 'pg3124-browser-resume-live-binding-v1/manifest.safe.json').read_bytes())
        term = json.loads((W / 'pg2992-current-resume-terminal-v1/manifest.safe.json').read_bytes())
        fields = json.loads((W / 'pg3004-current-resume-parent-projection-v1.safe.json').read_bytes())['parentState18']
        ctx[2] = {**ctx[2], 'endMonotonicUs': live['binding']['start'] + 1000}
        values = owned.emit(tuple(ctx), live, term['parentState'], fields)
        expected = {'Pg3150NativeArgumentTest.java', 'Pg3150NativeStop.java', 'Pg3150OriginalTupleTest.java', 'Pg3150StopLabelTest.java', 'pg3150_configuration.py', 'pg3150_configuration_capture.py', 'pg3150_durable.py', 'pg3150_native_owned_stop.py', 'pg3150_native_refs.py', 'pg3150_parent_receipt.py', 'pg3150_row_bound.py', 'pg3150_stable_journal.py', 'pg3150_warning_parent_projection.py', 'pg526_native_term_witness.py', 'pg526_term_witness.py'}
        self.assertEqual(expected, set(values))
        for name, raw in values.items():
            if name.endswith('.py'):
                self.assertEqual(0, check(raw, '<whole Browser owned ' + name + '>'))
                compile(raw, '<whole owned export>', 'exec')
        receipt = ast.parse(values['pg3150_parent_receipt.py'])
        binding = next(ast.literal_eval(node.value) for node in receipt.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'BINDING' for target in node.targets))
        self.assertEqual(live['binding'], binding)
        self.assertNotEqual('0ac69fb7-3cb7-4d33-b2d9-4733fba5a4cf', binding['activation'])
        for raw in values.values():
            for old in ['pg3006', 'Pg3006', 'pg3000-current-resume-full-seal-v1']:
                self.assertFalse(old in raw, old)

    def test_complete_consumer_namespaces_and_no_old_output_slot(self):
        for ns, required in [(dispatch.namespace(), ['stage', 'post_payload', 'run_source', 'run_action', 'main']), (post.namespace(), ['emit', 'payload', 'entry'])]:
            for name in required:
                self.assertTrue(callable(ns[name]))
        self.assertEqual('/var/lib/pgpt-s1-preservation/pg3150-browser-business-owned-stop-tools-v1', dispatch.GUEST)
        self.assertEqual('pg3146-browser-business-full-seal-v1', dispatch.POST_SLOT)
        self.assertEqual('pg3156-browser-business-owned-post-v1', post.SLOT)


if __name__ == '__main__':
    unittest.main()
