"""Metadata guards only; mutations do not start Java/Maven or access any VM/log/service."""
import copy
import json
import unittest
from web_classpath_receipt_contract import META,validate_receipt,verify_metadata

class WebClasspathReceiptTest(unittest.TestCase):
    def test_actual_completed_receipt_and_retained_exact_tool_version(self):
        value=verify_metadata()
        self.assertTrue(value['exactExecutedSourcesVerified'])
        self.assertFalse(value['metadataGoalReplayed'])

    def test_each_terminal_source_command_and_output_mutation_rejected(self):
        original=json.loads(META.read_bytes())
        for kind in ('unknown-terminal','wrong-source','wrong-compile','not-metadata','compile-replayed','classes-changed','wrong-output','extra-test-command'):
            with self.subTest(kind=kind):
                value=copy.deepcopy(original)
                if kind=='unknown-terminal':value['terminal']['actualExit']=None
                elif kind=='wrong-source':value['source']='0'*40
                elif kind=='wrong-compile':value['originalCompileSha256']='0'*64
                elif kind=='not-metadata':value['metadataOnly']=False
                elif kind=='compile-replayed':value['compileRepeated']=True
                elif kind=='classes-changed':value['originalClassBytesAndMtimesUnchanged']=False
                elif kind=='wrong-output':value['classpath']['sha256']='0'*64
                else:value['command'].append('test')
                with self.assertRaises(ValueError):validate_receipt(value,original['source'],original['originalCompileSha256'],original['classpath']['sha256'])

if __name__=='__main__':unittest.main()
