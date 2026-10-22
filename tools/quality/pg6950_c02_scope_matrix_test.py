import unittest
import pg6950_c02_scope_matrix as p


class C02SourceMatrixTest(unittest.TestCase):
    def test_reset_and_append_order_not_flattened(self):
        rows = p.directives('[Service]\nExecStart=\nExecStart=/fixture/entry\nLoadCredential=a:/fixture/a\nLoadCredential=b:/fixture/b\n')
        self.assertEqual(['', '/fixture/entry'], p.values(rows, 'Service', 'ExecStart'))
        self.assertEqual(['a:/fixture/a', 'b:/fixture/b'], p.values(rows, 'Service', 'LoadCredential'))
        self.assertEqual([('Service', 'Environment', 'JAVA_ARGS=-Xmx512m -Dname=value')],
          p.directives('[Service]\nEnvironment=JAVA_ARGS=-Xmx512m -Dname=value\n'))

    def test_malformed_or_empty_has_no_successful_projection(self):
        for text in ('', '# only comment', 'User=fixture', '[Service]\nbad line', '[Service]\n=empty-key'):
            with self.assertRaises(ValueError):
                p.directives(text)

    def test_declared_profile_not_runtime_identity_and_negative_policy(self):
        text = '[Service]\nUser=schubert-api\nGroup=schubert-api\nProtectSystem=strict\nSendSIGKILL=no\nNoNewPrivileges=true\nExecStart=!/fixture/RootServiceLauncher API\n'
        p.common_profile('schubert-nk-api.service.template', p.directives(text))
        for value in (text.replace('User=schubert-api', 'User=root'), text.replace('ProtectSystem=strict', 'ProtectSystem=full'),
          text.replace('SendSIGKILL=no', 'SendSIGKILL=yes'), text.replace('NoNewPrivileges=true', 'NoNewPrivileges=false'),
          text.replace('ExecStart=!', 'ExecStart=+'), text + '\n[Unit]\nConditionPathExists=/fixture/unknown\n'):
            with self.assertRaises(ValueError):
                p.common_profile('schubert-nk-api.service.template', p.directives(value))


if __name__ == '__main__':
    unittest.main()
