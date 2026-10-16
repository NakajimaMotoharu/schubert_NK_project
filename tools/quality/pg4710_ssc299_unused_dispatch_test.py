"""Pure real-artifact contracts: no stage/place, systemctl or business action issued."""
import ast
from contextlib import nullcontext
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg4710_ssc299_unused_dispatch as dispatch
import pg4712_ssc299_unused_post as post


class UnusedActions(unittest.TestCase):
    def test_actual_main_selects_new_candidate_before_runtime_admission(self):
        seen=[]
        def namespace(candidate,before):
            seen.append((candidate,before));return {}
        with patch.object(dispatch.sys,'argv',['tool','stage']),patch.object(dispatch,'authenticate_host')as auth, \
             patch.object(dispatch,'runtime_namespace',side_effect=namespace), \
             patch.object(dispatch,'source',return_value='def main(): return 0'), \
             patch.object(dispatch,'management_gate',return_value=nullcontext()):
            self.assertEqual(0,dispatch.main());auth.assert_called_once()
        self.assertEqual(1,len(seen))
        self.assertEqual(dispatch.role.SOURCE,seen[0][0]['candidateSource'])
        self.assertEqual(dispatch.role.candidate_bom(),seen[0][0]['manifestSha256'])
        self.assertEqual(dispatch.role.CURRENT,seen[0][1]['productionSource'])

    def test_current_data_only_and_new_candidate_runtime_have_distinct_fixed_roles(self):
        record=dispatch.before_record()
        candidate=json.loads((dispatch.role.W/'pg4702-candidate-build-v1.safe.json').read_bytes())
        ns=dispatch.runtime_namespace(candidate,record)
        self.assertEqual(dispatch.role.SOURCE,ns['SOURCE'])
        self.assertEqual(dispatch.role.BEFORE,ns['BASELINE_SHA'])
        for raw in [dispatch.source(),dispatch.stage_source()]:
            compile(raw,'<new immutable unused action>','exec')
            self.assertNotIn('pg3986',raw)
            self.assertNotIn('PG3986',raw)
        self.assertIn('PG4710_IMMUTABLE_STAGE_V1',dispatch.stage_source())
        for key,value in [('runtimeAlreadyRetired',False),('dataOnlyNotRuntimeAuthority',False),('allClientAdvisoryFlock0',False)]:
            with self.subTest(key=key),self.assertRaises(ValueError):dispatch.runtime_namespace(candidate,{**record,key:value})
        with patch.object(dispatch.sys,'argv',['tool','stop']),patch.object(dispatch,'authenticate_host')as auth:
            with self.assertRaises(ValueError):dispatch.main()
            auth.assert_not_called()

    def test_candidate_checks_inside_owned_refs_and_durable_success_after_close(self):
        raw=post.payload();self.assertEqual(0,check(raw,'<actual independent unused post>'))
        tree=ast.parse(raw)
        outer=next(n for n in tree.body if isinstance(n,ast.Try)and 'manager.UnrefUnit(u)'in ast.unparse(n.finalbody))
        text=ast.unparse(outer.body)
        for literal in ['0.1.0-PG4702','pg4702-manifest.sig','0.1.0-PG4432',
                        'pg4704-current-preservation-readonly-v1/before.private.json',
                        "p.endswith('.exec')",'complete_configuration','187']:
            self.assertIn(literal,text)
        self.assertEqual(1,raw.count('def complete_configuration('))
        update=next(n for n in tree.body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)
                    and ast.unparse(n.value.func)=='result.update'and 'candidateUnusedOnly' in ast.unparse(n))
        self.assertGreater(update.lineno,outer.end_lineno)
        self.assertIn("'guestFilesWritten': 3",ast.unparse(update))
        self.assertIn('result["newTenReferencesReturnedNormally"]=len(refs)==10',raw)
        for original in [dispatch.__file__,post.__file__,__file__]:self.assertEqual(0,checkPath(original))
        before=post.current.payload()
        with patch.object(post.current,'payload',return_value=before.replace('def complete_configuration(', 'def foreign_configuration(')):
            with self.assertRaises(ValueError):post.payload()


if __name__=='__main__':unittest.main()
