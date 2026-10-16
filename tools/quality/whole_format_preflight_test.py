"""Independent order/failure/changed-source oracle; no Maven or external mutation."""
import ast
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg4694_ssc299_full as frozen
from whole_format_preflight import compose, format_preflight


class Preflight(unittest.TestCase):
    def test_real_six_module_factory_has_preflight_before_only_pt_site(self):
        original = frozen.server_source(frozen.SOURCE, 'a' * 64)
        raw = compose(original)
        main = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == 'main')
        order = [ast.unparse(n) for n in main.body]
        self.assertLess(next(i for i, n in enumerate(order) if n.startswith('format_preflight(')),
                        next(i for i, n in enumerate(order) if 'maven.private.log' in n))
        self.assertNotIn('format_preflight', original)
        self.assertEqual(0, check(raw, '<future whole preflight actual standalone>'))
        with self.assertRaises(ValueError): compose(raw)

    def test_zero_only_unchanged_six_format_can_return_to_caller(self):
        modules = ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']
        args = ['mvn', '-o', '-pl', ','.join('src/schubert-nk-' + m for m in modules),
                'clean', 'spotless:check', 'test-compile', 'jar:test-jar', 'test',
                'spotbugs:check', 'jacoco:report', 'jar:jar']
        for exit_code, mutate, accepted in [(0, False, True), (1, False, False), (0, True, False), (False, False, False)]:
            with self.subTest(exit_code=exit_code, mutate=mutate), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); source = root / 'source'; source.mkdir()
                (source / 'literal').write_bytes(b'original'); out = root / 'out'; out.mkdir()
                inputs = {'literal': hashlib.sha256(b'original').hexdigest()}
                calls = []
                def run(command, **kwargs):
                    calls.append(command)
                    if mutate: (source / 'literal').write_bytes(b'changed')
                    return SimpleNamespace(returncode=exit_code)
                with patch('subprocess.run', side_effect=run):
                    if accepted: format_preflight(args, source, out, {}, inputs)
                    else:
                        with self.assertRaises(ValueError): format_preflight(args, source, out, {}, inputs)
                self.assertEqual([args[:4] + ['spotless:check']], calls)
                self.assertFalse(json.loads((out / 'format-preflight.safe.json').read_bytes())['testsIssued'])
        with tempfile.TemporaryDirectory() as directory, patch('subprocess.run') as child:
            with self.assertRaises(ValueError): format_preflight(['mvn', '-pl', 'foreign', 'test'], Path(directory), Path(directory), {}, {})
            child.assert_not_called()


if __name__ == '__main__': unittest.main()
