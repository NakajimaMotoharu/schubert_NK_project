import ast
import json
import unittest
import pg3756_hygiene_unused_sources as c
import pg3758_hygiene_unused_compile as compiler


class Roles(unittest.TestCase):
    def test_simultaneous_roles_no_sha_substring_or_historical_uuid_rewrite(self):
        source=c.previous.SOURCE;current=c.previous.CURRENT
        self.assertEqual(c.SOURCE+' '+c.CURRENT,c.role_text(source+' '+current))
        self.assertEqual('PG3748 PG3420',c.role_text('PG3420 PG2802'))
        sha='a'+source+'b'*23;self.assertEqual(64,len(sha));self.assertEqual(sha,c.role_text(sha))
        example="negative='323bc9ad-1528-449a-8067-19228ee1e046'; wrong='00000000-0000-0000-0000-000000000007'";self.assertEqual(example,c.role_text(example))

    def test_all18_roles_latest_tuple_negative_fixture_and_strict_input(self):
        values=c.sources();self.assertEqual(18,len(values));raw='\n'.join(values.values())
        for value in [c.CURRENT,c.SOURCE,c.CURRENT_BOM,c.BOM,c.BEFORE,c.BOOT,c.TOOLS,'pg3754-current-4856-before-view-v1']:self.assertIn(value,raw)
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG3748',values['pg3756_input_preflight.py']);self.assertIn('/opt/schubert-nk/releases/0.1.0-PG3420',values['Pg3756UnusedStage.java'])
        self.assertEqual(c.current_tuple()[0],c.previous.binding(values['pg3756_parent_receipt.py']))
        expected=c.pinned(c.LATEST,'Pg3600OriginalTupleTest.java').replace('Pg3600NativeStop','Pg3756UnusedStage').replace('Pg3600','Pg3756').replace('PG3600','PG3756');self.assertEqual(expected,values['Pg3756OriginalTupleTest.java'])
        t=ast.parse(values['pg3756_native_refs.py']);bindings={n.targets[0].id:ast.literal_eval(n.value)for n in t.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in {'INV','START','END'}}
        self.assertEqual({'INV':c.current_tuple()[0]['invocation'],'START':c.current_tuple()[0]['start'],'END':c.current_tuple()[1]['endMonotonicUs']},bindings)
        for bad in [None,'','a'*64,c.CURRENT_BOM]:
            with self.assertRaises(ValueError):c.sources(bad)
        with self.assertRaises(ValueError):c.sources(c.BOM,'b'*64)

    def test_emitted_host_abi_is_new_only_and_current_shared_contract(self):
        raw=compiler.compiler();ast.parse(raw)
        for value in ['pg3748-candidate-build-v1','pg3748-release-v1','pg3748-manifest-v1.sig','pg3754-current-before-view-v1',"['result']",'pg3602-frozen-v1','pg3600-current-browser-owned-stop-tools-v1','pg3420-release-v1','Pg3756OriginalTupleTest','pg3758-frozen-v1']:
            self.assertIn(value,raw)
        for value in ['pg3152-frozen','pg2802-release-v1','systemctl','daemon-reload']:self.assertNotIn(value,raw)
        self.assertTrue(c.VIEW_LOCAL.is_file());view=json.loads(c.VIEW_LOCAL.read_bytes());self.assertEqual(0,view['actualExit']);self.assertEqual(c.CURRENT,view['result']['productionSource']);self.assertEqual(c.BEFORE,view['result']['privateBeforeSha256']);self.assertIn('pg3754-current-4856-before-view-v1',view['result']['guestBeforePath'])
        current_line=next(x for x in raw.splitlines()if x.strip().startswith('current = '));self.assertNotIn('current-4856-before-view',current_line)


if __name__=='__main__':unittest.main()
