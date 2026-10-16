"""Independent tool-only oracles; never counted as Production PT or Root authority."""
import ast
import importlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from pyflakes.api import check
from pyflakes.reporter import Reporter
import pg4408_canonical_shared_manager_cost as canonical
import pg4420_shared_manager_full as full

ROOT = Path(__file__).resolve().parents[2]
NAMES = ['pg4392_proc_metadata_cost', 'pg4394_root_read_cost', 'pg4396_binding_regex_cost',
         'pg4400_exact_native_adapter_cost', 'pg4402_child_unit_read_cost',
         'pg4404_shared_manager_candidate_cost', 'pg4406_verified_shared_manager_cost',
         'pg4408_canonical_shared_manager_cost']


class ToolContracts(unittest.TestCase):
    def test_all_host_and_all_emitted_static_are_independently_zero(self):
        for name in NAMES + ['pg4412_shared_manager_selected', 'pg4420_shared_manager_full']:
            with self.subTest(host=name):
                module = importlib.import_module(name); text = Path(module.__file__).read_text()
                compile(text, name, 'exec')
                self.assertEqual(0, check(text, name, Reporter(io.StringIO(), io.StringIO())))
                if name in NAMES:
                    raw = module.payload(); compile(raw, name + '-emitted', 'exec')
                    self.assertEqual(0, check(raw, name + '-emitted', Reporter(io.StringIO(), io.StringIO())))

    def test_measurements_never_start_root_or_change_business_state(self):
        for name in NAMES:
            with self.subTest(name=name):
                raw = importlib.import_module(name).payload()
                self.assertIn("'operationsIssued':0", raw)
                self.assertNotIn("['systemctl','start'", raw)
                self.assertNotIn("['systemctl','stop'", raw)
                self.assertNotIn('RootStartupContext.create()', raw)
                self.assertIn('assert manifest.read_bytes()==before', raw)
                self.assertIn("'MainPID':'0','ControlPID':'0','Job':''", raw)

    def test_full_preserves_quality_and_expected_literal_count_without_tests_gate_override(self):
        raw = full.server_source(full.SOURCE, 'ab' * 32)
        self.assertEqual(0, check(raw, '<full>', Reporter(io.StringIO(), io.StringIO())))
        literals = [n.value for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Constant)]
        for required in ['spotless:check', 'test-compile', 'jar:test-jar', 'test', 'spotbugs:check', 'jacoco:report', 'jar:jar', 3721, 545, 1644]:
            self.assertIn(required, literals)
        for forbidden in ['-DfailIfNoTests=false', '-DskipTests', '-Dmaven.test.skip=true', '-Djacoco.skip=true']:
            self.assertNotIn(forbidden, literals)
        self.assertIn(full.SOURCE, literals)
        self.assertIn('ab' * 32, literals)

    def test_canonical_oracle_has_literal_independent_values_and_rejects_every_missing_or_changed_field(self):
        # Execute exactly the candidate TOOL method. Expected data is a separately written literal,
        # not a value manufactured by the method under test or by Production code.
        main = r'''
  public static void main(String[] args) {
    String phase="productionChildUnitRead";
    String raw="Id=literal.service\nLoadState=loaded\nActiveState=failed\nSubState=failed\nMainPID=0\nInvocationID=11111111111111111111111111111111\nControlGroup=\n";
    String expected="ActiveState=failed\nControlGroup=\nId=literal.service\nInvocationID=11111111111111111111111111111111\nLoadState=loaded\nMainPID=0\nSubState=failed\n";
    var cs=java.nio.charset.StandardCharsets.US_ASCII;
    byte[] golden=expected.getBytes(cs);
    if(!java.util.Arrays.equals(golden,canonical(phase,raw.getBytes(cs))))throw new AssertionError("literal golden");
    var lines=raw.split("\n");
    var reversed=new java.util.ArrayList<>(java.util.List.of(lines));java.util.Collections.reverse(reversed);
    if(!java.util.Arrays.equals(golden,canonical(phase,(String.join("\n",reversed)+"\n").getBytes(cs))))throw new AssertionError("order only");
    int rejected=0;
    for(String line:lines){
      if(java.util.Arrays.equals(golden,canonical(phase,raw.replace(line,line+"changed").getBytes(cs))))throw new AssertionError("one changed value");
      try{canonical(phase,raw.replace(line+"\n","").getBytes(cs));throw new AssertionError("missing value");}
      catch(IllegalStateException wanted){rejected++;}
    }
    for(String bad:new String[]{"",raw+"Unknown=1\n",raw+"MainPID=0\n",raw.replace("Id=","Id"),raw.replace("loaded","bad\rvalue"),raw.substring(0,raw.length()-1),raw.replace("Id=literal.service","Unknown=literal.service")}){
      try{canonical(phase,bad.getBytes(cs));throw new AssertionError("malformed value");}
      catch(IllegalStateException wanted){rejected++;}
    }
    byte[] proc="proc".getBytes(cs);
    if(canonical("productionProcFilesystemRead",proc)!=proc||rejected!=14)throw new AssertionError("control/rejection count");
    System.out.println("literal2 changed7 rejected14 control1; authority=false");
  }
'''
        java = 'public final class ToolCanonicalOracle {' + canonical.CANONICAL + main + '}\n'
        with tempfile.TemporaryDirectory(prefix='pg4414-tool-oracle-') as folder:
            path = Path(folder) / 'ToolCanonicalOracle.java'; path.write_text(java)
            result = subprocess.run([str(ROOT.parent / 'toolchain/jdk-25.0.4/bin/java'), '--source', '25', str(path)],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual('literal2 changed7 rejected14 control1; authority=false\n', result.stdout)


if __name__ == '__main__':
    unittest.main()
