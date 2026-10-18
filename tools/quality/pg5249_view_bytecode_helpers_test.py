import unittest
import pg5138_factory_bytecode as bytecode


class DeclarationNames(unittest.TestCase):
    def test_abstract_and_native_empty_code_have_exact_empty_canonical_form(self):
        for header in ('public abstract T execute();','public native int openRoot();'):
            self.assertEqual(bytecode.canonical({'header':header,'ops':[],'handlers':[]}),
                             {'ops':[],'handlers':[]})

    def test_code_free_method_with_handler_is_rejected_not_silently_equal(self):
        with self.assertRaises(ValueError):
            bytecode.canonical({'header':'public abstract T execute();','ops':[],
                                'handlers':[(0,1,1,'Class java/lang/Error')]})

    def test_package_private_public_and_static_members_share_one_name_rule(self):
        for header in ('int openRoot() throws StorageIoException;',
            'private int openRoot();','public static int openRoot();',
            'public <T> T openRoot(java.lang.String);'):
            self.assertTrue(bytecode.named({'header':header},'openRoot'))

    def test_return_type_suffix_constructor_and_empty_are_not_member_name(self):
        for header in ('int openRootAgain();','int reopenRoot();',
                       'dev.codex.ViewOwner();','static {};',''):
            self.assertFalse(bytecode.named({'header':header},'openRoot'))


if __name__=='__main__':unittest.main()
