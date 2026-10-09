"""Current literal captures plus actual isolated import graph/eachdependencyabsence."""
import ast
import copy
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from pg768_sources import assemble,SOURCE


def fixture():
    proof={'actualExit':0,'productionSource':SOURCE,'batchRun':'9de2d03c-28c7-4647-97d9-c66ace06048c','cutoff':'2026-10-09T05:42:22.532331Z',
        'activation':'021111b4-6de5-4733-917d-5ac176240ffc','parentEndedUTC':'2026-10-09T06:10:00.000000Z',
        'genuineCompletion':{'genuineRootDone':True,'genuinePid1StartDone':True,'endMonotonicUs':138900000000}}
    base={'actualExit':0,'source':SOURCE,'batchRows':544,'full21Fields':True,'all24UnchangedTwice':True,'all10KernelAndResources0':True,'beforeSha256':'1'*64}
    return proof,base


class Test(unittest.TestCase):
    def test_fixed_current_closing_and_preserve_nine(self):
        values=assemble(*fixture());self.assertEqual(10,len(values['python_files']))
        for raw in values['python_files'].values():ast.parse(raw)
        refs=values['refs'];self.assertIn('completion_messages(messages)',refs)
        for cohort in ('664','702','737'):
            for kind in ('tools','verify','existing'):self.assertIn('pg'+cohort+'-bootstrap-'+kind+'-v1',refs)
        for v in ('==544)','==138900000000','pg767-completed-baseline-v1','1'*64):self.assertIn(v,refs)
        for v in ('8d4b68b4f1449932ebe506aaf08e584bbfea8dd2','2026-10-09T06:10:00.000000Z','021111b4-6de5-4733-917d-5ac176240ffc'):self.assertIn(v,values['java'])
        self.assertIn('pg750-release-v1/api/api.jar',values['compile_script']);self.assertIn("'pg535_bootstrap_contract.py') else R / name",values['native'])
        self.assertIn("('terminal','closing')",values['python_files']['pg535_bootstrap_contract.py'])

    def test_actual_isolated_graph_and_each_missing(self):
        values=assemble(*fixture())['python_files']
        for missing in (None,*values):
            if missing=='pg768_bootstrap_existing.py':continue
            with self.subTest(missing=missing),tempfile.TemporaryDirectory(prefix='pg768-import-')as directory:
                root=Path(directory)
                for name,raw in {**values,'dbus.py':'# host only inert stub; never stage\n'}.items():
                    if name==missing:continue
                    fd=os.open(root/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o400)
                    with os.fdopen(fd,'w')as f:f.write(raw)
                result=subprocess.run([sys.executable,'-I','-B','-c','import sys;sys.path.insert(0,'+repr(directory)+');import pg768_bootstrap_existing'],capture_output=True)
                if missing is None:self.assertEqual(0,result.returncode,result.stderr.decode());self.assertEqual(b'',result.stdout+result.stderr)
                else:self.assertNotEqual(0,result.returncode);self.assertIn(('No module named '+repr(missing[:-3])).encode(),result.stderr)

    def test_compiler_fixed_new_contract_and_preflight(self):
        from pg768_compile import source
        raw=source(*fixture());ast.parse(raw)
        self.assertIn('from pg768_sources import java, refs, receipt, join, argument_test, compile_script,python_files',raw)
        self.assertIn("for name in ('pg535_bootstrap_contract.py',):",raw)
        self.assertIn("'pg768_pair_contract_test.py')",raw)
        self.assertIn('pg767-completed-baseline-v1.exit',raw)
        self.assertIn("root=W/'pg768-bootstrap-tools-v1'",raw)

    def test_false_foreign_or_incomplete_never_current(self):
        for which,key,value in ((0,'actualExit',False),(0,'productionSource','1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'),(0,'batchRun','55ac70e7-0180-4c32-8c91-5a379ebedf24'),(0,'activation','ab8895ca-4fb1-440d-b174-bc9f1f27505a'),(1,'actualExit',True),(1,'batchRows',534),(1,'full21Fields',1),(1,'beforeSha256',None)):
            pair=copy.deepcopy(fixture());pair[which][key]=value
            with self.assertRaises(AssertionError):assemble(*pair)


if __name__=='__main__':unittest.main()
