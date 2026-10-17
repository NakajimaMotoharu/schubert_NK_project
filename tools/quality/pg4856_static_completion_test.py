import contextlib
import hashlib
import inspect
import io
import json
from pathlib import PosixPath
import tempfile
import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg4856_static_completion as role


class MissingPhase(unittest.TestCase):
    def test_frozen_original_identity_and_no_reissued_pmd(self):
        text = (role.W / 'pg4850-ssc301-302-static-v1/static.private.py').read_text()
        self.assertEqual(role.SOURCE, role.original_input(text)['source'])
        for bad in (text.replace(role.SOURCE, 'f' * 40), text + '\nserver({})\n', text.replace("'includeCheckstyle': True", "'includeCheckstyle': False")):
            with self.assertRaises(ValueError): role.original_input(bad)
        raw = '\n'.join(inspect.getsource(f) for f in (role.require, role.server))
        self.assertEqual(0, check(raw, '<full missing-phase payload>'))
        self.assertEqual(1, raw.count('subprocess.run('))
        self.assertIn("fixed['checkstyle']['argv']", raw)
        self.assertNotIn("fixed['pmd']['argv']", raw)

    def fixture(self, base):
        def write(path, value):
            p = base / path; p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(value) if isinstance(value, dict) else value); return p
        sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        source = base / 'source-full-PG4844'; candidate = base / 'runs/PG4850-ssc301-302-static-input-v1/candidate'
        hashes = {}
        for i in range(849):
            name = f'src/schubert-nk-api/src/main/java/p/C{i:03d}.java'
            data = f'final class C{i:03d} {{}}'
            a = write('source-full-PG4844/' + name, data)
            write('runs/PG4850-ssc301-302-static-input-v1/candidate/' + name, data); hashes[name] = sha(a)
        frozen = write('transfer/PG4850-ssc301-302-static-v1/static.private.py', 'exact frozen fixture')
        prefix = 'runs/PG4850-ssc301-302-static-v1/'
        write(prefix+'begin.safe.json', {'productionCandidateSource': role.SOURCE})
        paths = sorted(candidate.glob('src/*/src/main/java/**/*.java'))
        write(prefix+'all-java.txt', ''.join(str(p)+'\n' for p in paths))
        write(prefix+'pmd.xml', '<pmd><file name="'+str(paths[0])+'"><violation rule="ExplicitRule"/></file></pmd>')
        write(prefix+'pmd.private.log', 'original log')
        aux = write('qualified.jar', 'current six-Jar fixture binding')
        write(prefix+'aux-classpath.txt', str(aux)+'\n')
        rule = write('runs/PG3382-static-gate-v1/result/source/tools/quality/static/checkstyle.xml', 'pinned rule')
        jar = write('runs/PG3382-static-gate-v1/checkstyle-14.3.0-all.jar', 'pinned analyzer')
        old = write('runs/PG3422-candidate-static-v1/manifest.safe.json', {'ruleSha256': {'checkstyle.xml': sha(rule)}, 'pinnedToolSha256': {'checkstyle-14.3.0-all.jar': sha(jar)}})
        write('runs/PG3382-static-gate-v1/result/manifest.safe.json', {'checkstyle': {'argv': ['java', '-jar', str(jar), '-c', 'old', '-o', 'old', '@old']}})
        write('runs/PG4700-ssc299-static-v1/manifest.safe.json', {'pmd': {'ruleCounts': {'ExplicitRule': 1}}})
        return {'source': role.SOURCE, 'originalPayloadSha256': sha(frozen), 'originalStaticManifestSha256': sha(old), 'candidateJob': 'PG4850-ssc301-302-static-input-v1', 'sourceSha256': hashes, 'auxJson': json.dumps({str(aux): sha(aux)}), 'originalFailure': {'actualExit': 1}}, source

    def test_actual_recovery_only_executes_checkstyle_preserves_failure_and_unknown_exit(self):
        with tempfile.TemporaryDirectory() as folder:
            base = PosixPath(folder); data, source = self.fixture(base); calls = []
            def mapped(value):
                return base if str(value) == '/home/mini/schubert-nk-pgpt' else PosixPath(value)
            def checked(argv, **kwargs):
                calls.append(argv); self.assertIn('checkstyle-14.3.0-all.jar', ' '.join(argv))
                PosixPath(argv[argv.index('-o')+1]).write_text('<checkstyle/>')
                import subprocess
                return subprocess.CompletedProcess(argv, 0, b'', b'')
            with patch('pathlib.Path', mapped), patch('subprocess.run', checked), contextlib.redirect_stdout(io.StringIO()):
                role.server(data)
            result = json.loads((base/'runs/PG4856-static-completion-v1/manifest.safe.json').read_text())
            self.assertEqual(1, len(calls)); self.assertEqual(1, result['recoveredOriginalFailure']['actualExit'])
            self.assertIsNone(result['pmd']['actualExit']); self.assertEqual(0, result['checkstyle']['actualExit'])
            self.assertFalse(result['pmdReissued']); self.assertFalse(result['F03Accepted'])
            self.assertEqual({}, result['actualRuleCountDeltaFromOld825e'])
            # Source mutation is rejected before any second tool execution.
            next(source.glob('src/*/src/main/java/**/*.java')).write_text('changed')
            with patch('pathlib.Path', mapped), patch('subprocess.run', checked), self.assertRaises(ValueError): role.server(data)
            self.assertEqual(1, len(calls))


if __name__ == '__main__': unittest.main()
