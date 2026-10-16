"""Execute the actual original inline full32 contract, before any VM access."""
import unittest
import pg4482_bound_configuration_pair_read as tool


class InlineCompleteContract(unittest.TestCase):
    def test_actual_configuration_dictionary_is_initialized_and_only_missing_binding_is_added(self):
        namespace={'CONFIG_CONTRACT':{}};exec(tool.inline_configuration(),namespace)
        contract=namespace['CONFIG_CONTRACT']
        self.assertTrue(callable(contract['same']))
        self.assertEqual(32,len(contract['FIELDS']))
        for key in ['ExecStart','ExecStop','ReadWritePaths','User','Group','Type']:
            self.assertIn(key,contract['FIELDS'])
        before=(tool.W/'pg4480-complete-inspect-pair-read-v1/payload.private.py').read_text()
        after=tool.payload().replace('pg4482-bound-configuration-pair-read-v1','pg4480-complete-inspect-pair-read-v1')
        self.assertEqual(before,after.replace('CONFIG_CONTRACT={}\n'+tool.inline_configuration(),'CONFIG_CONTRACT={}',1))


if __name__=='__main__':
    unittest.main()
