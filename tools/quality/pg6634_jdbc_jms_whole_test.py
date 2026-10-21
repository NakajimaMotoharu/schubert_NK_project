import ast
import unittest
from unittest.mock import patch
import pg6634_jdbc_jms_whole as whole
import pg6636_original4158_artifacts as original


class IntegratedGraphDefinitionTest(unittest.TestCase):
    def test_declared_source_only_and_safe_standalone(self):
        self.assertEqual((4158,635),whole.declared_inventory())
        raw=whole.server_source('0'*40,'0'*64)
        ast.parse(raw)
        for forbidden in ('systemctl','qemu-system','virsh','sudo ','/opt/schubert-nk/current','--recover','--resume'):
            self.assertNotIn(forbidden,raw)

    def test_original_reader_retains_exact_campaign_and_no_execution(self):
        raw=original.emitted('0'*64,'/public-test-only')
        self.assertIn("('PG6634', (4158, 635, 1667), 45)",raw)
        self.assertIn('expectedCurrentMain',raw)
        self.assertNotIn('subprocess',raw)
        self.assertNotIn('Popen',raw)
        self.assertIn('currentOriginalXmlQualified',raw)

    def test_all85_new_declarations_not_old_success_addition(self):
        source=whole.selected.OLD
        # The current HEAD has exactly the two new JMS suites as well as all prior new suites.
        import subprocess
        source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=whole.ROOT,text=True).strip()
        self.assertEqual(85,len(original.new_case_identities(source)))

    def test_no_whole_before_qualified_original(self):
        with patch.object(whole.subprocess,'check_output',return_value=b''):
            with self.assertRaisesRegex(ValueError,'freeze genuine'):whole.prerequisites('fixture')


if __name__=='__main__':unittest.main()
