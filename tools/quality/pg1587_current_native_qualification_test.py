"""Current source input/immutable full-result/native-count/no-action admission."""
import ast
import unittest
from pg1587_current_native_qualification import CODE

class CurrentNativeQualificationTest(unittest.TestCase):
    def test_current_source_and_actual_checks_no_regression_or_vm_actions(self):
        ast.parse(CODE)
        for text in ['4d6bcbddb417b76d27e52d5d9640752c300edccf','len(v[\'selected\'])==8',"full['tests']==3583","full['actualExit']==full['mavenExit']==0","qualified['qualificationInputs'][m]['exec']","qualified['jarHashes'][m]","rows[0]['sessions']==1","result['classByteMismatch']==0","local[m][k]==qualified['coverage'][m][k]",'NativeSessions571Test','NativeCoverageXml471',"'oldNativeImported':False","'remainingInspectorCurrent':True","'remainingBootstrapCurrent':True"]:
            self.assertIn(text,CODE)
        for forbidden in ['StartUnit','StopUnit','systemctl','mvn','javaagent','skipTests','shutdown','-DfailIfNoTests=false']:
            self.assertNotIn(forbidden,CODE)

if __name__=='__main__':unittest.main()
