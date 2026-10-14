"""Use actual complete helper exports, independent literal declaration and bad inputs."""
import ast
import hashlib
import importlib.util
import re
import unittest
from pathlib import Path
from pg1446_current_cold_stage import W
import pg2978_current_resume_post_exports as post


class Exports(unittest.TestCase):
    def test_actual_configuration_export_not_assumed_names(self):
        path = W / 'pg2970-current-cold-resume-tools-v1/pg2970_configuration.py'
        spec = importlib.util.spec_from_file_location('current_configuration_fixture', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(callable(module.same))
        self.assertFalse(hasattr(module, 'exec_record'))
        self.assertFalse(hasattr(module, 'config_same'))
        self.assertTrue('import same as config_same' in post.EXPORTS)

    def test_sealed_parser_literal_and_rejected_unknown(self):
        raw = (Path(__file__).parent / 'vm/050_s1/pg477_unit_references.py').read_bytes()
        self.assertEqual('b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4', hashlib.sha256(raw).hexdigest())
        node = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == 'exec_record')
        scope = {'re': re}
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<independent actual parser>', 'exec'), scope)
        parse = scope['exec_record']
        self.assertIsNone(parse('unknown'))
        self.assertIsNone(parse(''))
        value = '{ path=/opt/jdk-25.0.4/bin/java ; argv[]=/opt/jdk-25.0.4/bin/java main --resume fixed ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }'
        result = parse(value)
        self.assertIsNotNone(result)
        self.assertEqual(('/opt/jdk-25.0.4/bin/java', '/opt/jdk-25.0.4/bin/java main --resume fixed', 'no'), result[:3])


if __name__ == '__main__':
    unittest.main()
