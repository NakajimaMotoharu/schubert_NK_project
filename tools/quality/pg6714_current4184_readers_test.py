import inspect
import unittest
from unittest.mock import patch
import pg6714_current115_receivers as sql
import pg6718_sql58_original_jvm as jvm
import pg6720_current4184_trace as trace


class OriginalReaderDefinitionTest(unittest.TestCase):
    def test_exact_catch_literals_retained(self):
        before='class A {void m(){try {} catch(SQLException caught){ throw map("fixed",caught); }}}'
        self.assertEqual(sql.prior.exact_catches(before),sql.prior.exact_catches('\n'+before))
        self.assertNotEqual(sql.prior.exact_catches(before),sql.prior.exact_catches(before.replace('"fixed"','"changed"')))

    def test_explicit_ordinary_reader_bindings_compile_without_execution(self):
        self.assertTrue(callable(sql.definition()))
        self.assertTrue(callable(jvm.definition()))
        with patch.object(jvm,'SQLSHA',None):
            self.assertIsNone(jvm.definition().__globals__['SQLSHA'])
        self.assertIn('read_whole',inspect.getsource(trace.read_qualified))
        self.assertIn('f16f717d4e5338e7f5b44faef179ada0cf19aae0',inspect.getsource(trace.candidates))


if __name__=='__main__':unittest.main()
