"""Independent SSC228 live witness and finite publication source wiring."""
from pathlib import Path
import ast
import unittest

R=Path(__file__).resolve().parent


class Binding(unittest.TestCase):
    def test_v2_output_and_post_current_oldpid(self):
        wrapper=(R/'pg633_pending_native.py').read_text()
        refs=(R/'pg633_pending_refs.py').read_text()
        post=(R/'pg634_pending_post.py').read_text()
        self.assertIn("'run':'PG633-'+mode+'-v2'",wrapper)
        self.assertIn("root=base/('pg633-pending-'+MODE+'-v2')",post)
        self.assertIn("BASE/('pg633-pending-'+mode+'-v2')",refs)
        self.assertIn("base/'pg633-pending-verify-v2/after.private.json'",post)
        for source in (refs,post):
            self.assertIn("not pathlib.Path('/proc/1511808').exists()",source)
            self.assertNotIn("'pg633-pending-'+MODE+'-v1'",source)
            self.assertNotIn("'pg633-pending-'+mode+'-v1'",source)
        self.assertNotIn("'run':'PG633-'+mode+'-v1'",wrapper)

    def test_helper_and_peer_tag_exact_end_to_end(self):
        java=(R/'Pg633PendingDeployment.java').read_text()
        refs=(R/'pg633_pending_refs.py').read_text()
        self.assertIn('TOOLS.resolve("pg633_pending_refs.py").toString(),mode,Integer.toString(pid)',java)
        self.assertIn("set_config('application_name','PG633-pending-codeonly',false)",java)
        self.assertIn("a.application_name='PG633-pending-codeonly'",refs)
        self.assertTrue((R/'pg633_pending_refs.py').is_file())
        for source in (java,refs):
            self.assertNotIn('pg633_completed_refs',source)
            self.assertNotIn('PG633-completed-codeonly',source)

    def test_publication_epoch_invariant_and_source(self):
        java=(R/'Pg633PendingDeployment.java').read_text()
        self.assertIn('configure("PG621","72fb7440697ee1048a5c0145055dc1cc3c577914",OLD);Pg387TrustedDeployment.expectedSqlCount=28;',java)
        self.assertIn('configure("PG631",source,NEXT);Pg387TrustedDeployment.expectedSqlCount=28;',java)
        self.assertIn('epoch.state()==StartupPermitRecords.State.INVALID && epoch.permitDigest().isEmpty()',java)
        self.assertIn('original.completed().isEmpty()',java)
        self.assertIn('require(Arrays.equals(Files.readAllBytes(SAVE.resolve("old-epoch.private")),Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current"))));',java)
        for denied in ('invalidate(', 'UUID.randomUUID(', '.complete(', '.resume(', 'normalDone(', '2026-10-08T15:57:38.735146Z'):
            self.assertNotIn(denied,java)
        wrapper=(R/'pg633_pending_native.py').read_text()
        self.assertIn('/0.1.0-PG621/operations/batch.jar',wrapper)
        self.assertNotIn('/0.1.0-PG631/operations/batch.jar',wrapper)
        self.assertIn("'pg629_failed_receipt.py'",wrapper)
        self.assertIn("oracle.count('\\nOK\\n')==5",wrapper)
        self.assertEqual(wrapper.count("'pg633-'+mode+'-v2.safe.json'"),2)
        self.assertIn("'pg633-'+mode+'-v2.private.log'",wrapper)
        self.assertIn("'pg633-'+mode+'-v2.exit'",wrapper)
        self.assertNotIn("'pg624-'+mode",wrapper)

    def test_fresh_failure_seal_and_complete_nineteen_snapshot(self):
        source=(R/'pg633_pending_refs.py').read_text();tree=ast.parse(source)
        for value in ('pg629-failed-parent-baseline-v1/after.private.json',
                      'e2c2bb7eba013f9e90685c1d619a6c9f2127625af33af424116b7e37c081ada2',
                      '==494','0b36b3310aa261ee80b2f0cf9831f4c99ba666116f2c4473135d5ac3b67db2de',
                      '3a2de24f931544c0a2fd83556a659cd0','97094171993',
                      "receipt_env['failed30'](observed)","verified/'after.private.json'",'same_value(before,json.loads',
                      "changed_only(before,now)", "'PG633-pending-codeonly'",'e49243d5-de84-4714-8612-6912ddc17e9e'):
            self.assertIn(value,source)
        for value in ('pg611_parent_receipt','5a1acaa0c35e484c979401e3b6dfb36a','==492','old_epoch','changed_only(before,now,','epoch_transition('):
            self.assertNotIn(value,source)
        node=next(n for n in ast.walk(tree)if isinstance(n,ast.Compare)and isinstance(n.left,ast.Call)
                  and isinstance(n.left.func,ast.Name)and n.left.func.id=='strict'
                  and any(isinstance(v,ast.Constant)and isinstance(v.value,bytes)and v.value.startswith(b'NKACT1')for v in n.comparators))
        expected=b'NKACT1\ne49243d5-de84-4714-8612-6912ddc17e9e\n2026-10-08T18:32:42.140966Z\n7d381b67-b37b-48c6-99ac-e04a336f887d\n'
        self.assertEqual(ast.literal_eval(node.comparators[0]),expected);self.assertEqual(len(expected),109)
        # Old completed-owned receipts are protected history, not the new failure's normality.
        self.assertIn("value['pid1Stop']={u:file(BASE/'pg611-native-stop-v1'",source)
        self.assertIn("live=False",source);self.assertIn("for u in reversed(refs):manager.UnrefUnit(u)",source)


if __name__=='__main__':unittest.main()
