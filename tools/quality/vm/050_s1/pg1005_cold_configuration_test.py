"""Literal declaration/history oracle and narrow-observer no-full-regression contract."""
import ast
import re
import unittest
from pg1005_cold_configuration import source
from pg847_configuration import FIELDS,same

class DeclarationTest(unittest.TestCase):
    def test_literal_warm_to_cold_declaration_and_foreign_null_rejected(self):
        raw=source();node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record')
        env={'re':re};exec(compile(ast.Module(body=[node],type_ignores=[]),'<literal declaration>','exec'),env)
        parse=env['exec_record']
        cold='{ path=/fixed ; argv[]=/fixed arg ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }'
        warm='{ path=/fixed ; argv[]=/fixed arg ; ignore_errors=no ; start_time=[old] ; stop_time=[old] ; pid=41 ; code=exited ; status=143 }'
        self.assertEqual(('/fixed','/fixed arg','no','n/a','n/a','0','(null)','0/0'),parse(cold))
        before={k:''for k in FIELDS};before.update(ExecStart=warm,Id='literal.service')
        after={**before,'ExecStart':cold}
        self.assertTrue(same(before,after,parse))
        self.assertFalse(same(before,{**after,'ExecStart':cold.replace('/fixed arg','/foreign')},parse))
        for value in [None,'',cold+' extra',cold.replace('pid=0','pid=-1')]:self.assertIsNone(parse(value))

    def test_data_proof_reuse_not_full_database_or_success_rerun(self):
        raw=source();self.assertFalse('snapshot()'in raw)
        self.assertFalse('jsonb_agg'in raw)
        self.assertTrue("'v3DataProofReusedNotNewAchievement':True"in raw)
        self.assertTrue("start[3:]==('n/a','n/a','0','(null)','0/0')"in raw)
        self.assertTrue("same(old['configuration'][name],v,exec_record)"in raw)
        self.assertTrue("with_references(manager,bus,list(old['units']),both)"in raw)

if __name__=='__main__':unittest.main()
