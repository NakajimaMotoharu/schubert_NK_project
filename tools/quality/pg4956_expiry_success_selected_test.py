"""Check exact SSC304 scope and generated complete namespace, not Production PT."""
import inspect
import re
import unittest
import zipfile
import xml.etree.ElementTree as ET
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg4956_expiry_success_selected as role


class ExpirySelection(unittest.TestCase):
    def test_actual_scope_does_not_use_ownership_suppression_and_semantic_target(self):
        jar=role.ROOT.parent/'toolchain/m2/repository/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'
        with zipfile.ZipFile(jar)as z:self.assertIn('javax/annotation/WillClose.class',z.namelist())
        text=(role.ROOT/role.MAIN_PATH).read_text()
        self.assertIn('T resource = required(acquire.open());',text)
        self.assertNotIn('@javax.annotation.WillClose',text)
        self.assertNotIn('@edu.umd.cs.findbugs.annotations.WillClose',text)
        self.assertIn("'RESULTSET_READ_BODY'",role.source())
        good=ET.Element('method',name='lambda$successful$3',desc='(Ljava/time/Instant;Ljava/sql/ResultSet;)Ljava/util/Optional;')
        self.assertTrue(role.target_match(good,'RESULTSET_READ_BODY'))
        for desc in ('(Ljava/sql/PreparedStatement;)Ljava/util/Optional;','(Ljava/sql/ResultSet;)V'):
            self.assertFalse(role.target_match(ET.Element('method',name='lambda$successful$3',desc=desc),'RESULTSET_READ_BODY'))

    def test_real_git_main_scope_and_foreign_or_absent_diff_rejection(self):
        role.validate_selection()
        for changed in ('',role.MAIN_PATH+'\nsrc/schubert-nk-batch/src/main/java/Foreign.java\n'):
            with patch.object(role.subprocess,'check_output',return_value=changed):
                with self.assertRaisesRegex(ValueError,'only SSC304 Main'):role.validate_selection()

    def test_actual_scope_and_new_literal_oracles(self):
        self.assertEqual({'storage','bootstrap','batch'},set(role.MODULES.values()))
        self.assertEqual(7,len(role.MODULES))
        count=0
        for name,module in role.MODULES.items():
            path=role.ROOT/('src/schubert-nk-'+module+'/src/test/java/'+name.replace('.','/')+'.java')
            text=path.read_text();methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',text)
            self.assertEqual(text.count('@Test'),len(methods));self.assertEqual(len(methods),len(set(methods)))
            count+=len(methods)
            if name.endswith('ExpirySuccessfulScopeTest'):
                self.assertEqual(24,len(methods));self.assertTrue(all(m.startswith('exp4956')for m in methods))
                self.assertIn('try (JdbcClose owned = release::close)',text)
        self.assertGreater(count,30)

    def test_strict_complete_namespace_and_results(self):
        raw=role.source();header=inspect.getsource(role.previous.base).split('\ndef main():',1)[0]
        header+='\nMODULES={}\nMAIN_SOURCE="candidate"\nMETHODS={}\ndef verify_main_bytes(snapshot):raise ValueError("not a receipt")\n'
        header+=inspect.getsource(role.target_match)
        self.assertEqual(0,check(header+'\n'+raw,'<complete SSC304 selection namespace>'))
        self.assertLess(raw.index('format_command='),raw.index('child = subprocess.Popen'))
        for literal in ('actual != expected','flakyFailure','ptNotRun','freshStaticModules',
                        'verify_main_bytes(snapshot)',"needed={'LINE','METHOD'}|({'BRANCH'}if name!='usingJdbc'or 'BRANCH'in count else set())"):
            self.assertIn(literal,raw)
        self.assertNotIn('-DfailIfNoTests=false',raw)
        self.assertIn("'mainDelta':main_bytes",raw)
        for path in(role.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
