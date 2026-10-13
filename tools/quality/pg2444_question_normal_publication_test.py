"""Literal full entry, seven-phase independent oracle and retained schema tests."""
import ast
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from pyflakes.api import check
import pg2441_question_normal_publication_compile as compiler
import pg2442_question_normal_publication_dispatch as dispatcher
import pg2444_question_normal_publication_post as post
from pg2440_question_normal_publication_sources import BOOT,BEFORE,BOM,production


class WholePublication(unittest.TestCase):
    def test_actual_complete_compiler_and_dispatch_namespace(self):
        for raw,module in [(compiler.compiler(),compiler.prior.prior),(dispatcher.source(),dispatcher.prior.prior)]:
            namespace={**module.__dict__}
            exec(compile(raw,'<actual complete entry fixture>','exec'),namespace)
            self.assertTrue(callable(namespace['main']))
            for old in ['pg2170','pg2144','pg2168','0.1.0-PG1846','3d69f5af']:
                self.assertNotIn(old,raw)
        stage=dispatcher.STAGE
        self.assertIn(BOOT,stage)
        self.assertIn('/home/ubuntu/pg2442-question-publication-stage-v1/pg2440-question-normal-publication-tools-v1.tar',stage)
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG2126',stage)
        self.assertNotIn('3d69f5af',stage)
        self.assertIn("'unitExchangeAndReload':False",dispatcher.source())

    def test_whole_post_actual_reader_retains_original_and_native(self):
        reader=post.W/'pg2410-retired-current-before-v1/payload.private.py'
        original=reader.read_text();read_bytes=Path.read_bytes
        def fixture(path):
            if str(path).endswith('pg2441-frozen-v1.safe.json'):
                return json.dumps({'actualExit':0,'fileHashes':{}}).encode()
            return read_bytes(path)
        with patch.object(Path,'read_bytes',fixture):raw=post.payload()
        self.assertEqual(0,check(raw,'<independent whole post fixture>'))
        for required in [production(),BOM,BEFORE,'len(phases)>=7','len({stamp for stamp,phase,observed in phases})==len(phases)',
            "tuple(dict.fromkeys(phase for stamp,phase,observed in phases))==oracle['PHASES']",
            "for stamp,phase,observed in phases:oracle['verify']", "'native' not in after", "set(after)==set(old_after)-{'native'}",
            "after={**after,'native':old_after['native']}", "native==json.loads",'all24And32Unchanged',
            'unitBytesInodesConfigurationUnchanged','oldNativeNotAppliedToNewSource']:
            self.assertIn(required,raw)
        self.assertIn("original['source']=='3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8'",raw)
        self.assertNotIn('pg2174',raw)
        self.assertNotIn("save=base/'pg2410-retired-current-before-v1'",raw)
        self.assertEqual(hashlib.sha256(original.encode()).hexdigest(),
            json.loads((reader.parent/'manifest.safe.json').read_bytes())['payloadSha256'])

    def test_source_static_no_normalizing_or_replaying_operations(self):
        for p in Path('tools/quality').glob('pg244*.py'):
            self.assertEqual(0,check(p.read_text(),str(p)))
        tree=ast.parse(dispatcher.source())
        self.assertTrue(any(isinstance(n,ast.FunctionDef)and n.name=='main'for n in tree.body))


if __name__=='__main__':unittest.main()
