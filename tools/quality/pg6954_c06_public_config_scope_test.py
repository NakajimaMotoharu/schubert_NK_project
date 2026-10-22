import unittest
import pg6954_c06_public_config_scope as p


class C06PublicConfigScopeTest(unittest.TestCase):
    def test_literal_lf_environment_has_no_extra_source(self):
        p.fixed_environment(b'SCHUBERT_NK_CONFIG_DIR=/etc/schubert-nk\n')
        for bad in (b'', p.ENV + b'EXTRA=value\n', p.ENV.replace(b'\n', b'\r\n'),
          p.ENV.replace(b'/etc/schubert-nk', b'/fixture/other'), b'JAVA_TOOL_OPTIONS=-Dfixture=x\n'):
            with self.assertRaises(ValueError):
                p.fixed_environment(bad)

    def test_inspector_symbolic_nonsecret_source_exact_not_real_values(self):
        p.fixed_environment(p.INSPECTOR, inspector=True)
        with self.assertRaises(ValueError):
            p.fixed_environment(p.INSPECTOR.replace(b'@PG_PORT@', b'5432'), inspector=True)

    def test_scalar_inventory_is_strict_not_a_permissive_yaml_loader(self):
        self.assertEqual({'nk.protocol.version': 'str', 'nk.fixture.count': 'int'},
          p.flat_scalar_keys('"nk.protocol.version": "001"\n"nk.fixture.count": 7\n'))
        for text in ('', 'unknown: "x"', '"nk.x": []', '"nk.x": null', '"nk.x": !!tag x',
          '"nk.x": ""', '"nk.x": true', '"nk.x": 1\n"nk.x": 2', '"nk.x": 1\r\n'):
            with self.assertRaises(ValueError):
                p.flat_scalar_keys(text)


if __name__ == '__main__':
    unittest.main()
