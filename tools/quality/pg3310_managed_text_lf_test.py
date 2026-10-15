import unittest
from pg3310_managed_text_lf import inspect_text, selected


class ManagedTextLfTest(unittest.TestCase):
    def test_lf_utf8_empty_and_no_final_newline_are_valid(self):
        for value in [b'', b'one\ntwo\n', '正本\n'.encode(), b'{"one":1}']:
            self.assertEqual('PASS', inspect_text(value))

    def test_crlf_bare_cr_non_utf8_and_binary_are_not_normalized(self):
        for value, expected in [(b'one\r\n', 'CR_NOT_LF_ONLY'), (b'one\r', 'CR_NOT_LF_ONLY'), (b'\xff', 'INVALID_UTF8'), (b'x\x00y', 'BINARY_NUL_NOT_MANAGED_TEXT')]:
            self.assertEqual(expected, inspect_text(value))

    def test_deployment_templates_maven_and_document_types_are_explicit(self):
        for name in ['src/deployment/caddy/Caddyfile.template', 'api.env.template', 'Caddyfile', 'mvnw', '.gitattributes', 'doc.md', 'query.sql']:
            self.assertTrue(selected(name), name)
        for name in ['wire.bin', 'image.png', 'driver.jar', 'original.docx']:
            self.assertFalse(selected(name), name)


if __name__ == '__main__':
    unittest.main()
