import ast
import copy
import json
from pathlib import Path
import unittest
from pg876_public_artifact_check import check
from pg2470_question_current_a01 import code


class ActualA01(unittest.TestCase):
    def test_whole_actual_root_source_budget_current_driver(self):
        raw=code();ast.parse(raw)
        for literal in ['cdbc07cdf77370d521e64de8b327da7f6752139b',
            '6e069bc89f53b513c719c27fbe71167afbd07b48caa0a31c61bda3e2222f11cf',
            'b2d6f605-61cf-425f-8fbd-12d606f6ee66','PG2428',
            "issued['MainPID']=='194154'","m['InvocationID']=='9024d0364d07478d9237b6941d725208'",
            'pg2446-parent-watch-v1.private.jsonl','pg2448-question-current-noargs-once-v1',
            'pg2444-question-normal-publication-post-v1/manifest.safe.json','1800000000',
            'NativeNkA01Capture','122dcc4c1be482ac3239325de6fb3d4bec12747d05adce3929c319ab5bdfd71d']:
            self.assertTrue(literal in raw,literal)
        self.assertNotIn('systemctl start',raw)
        self.assertNotIn('daemon-reload',raw)

    def test_independent_fixed_current_dif_only_and_secret_negatives(self):
        root=Path(__file__).resolve().parents[2]
        before=json.loads((root/'program/characterization/baseline/current/artifacts/CHR-A01.json').read_bytes())
        expected=copy.deepcopy(before);expected['title']='schubert NK - ログイン';check(expected,before)
        for key,value in [('title','foreign'),('csrf','raw'),('passwordValue','raw'),('unknown','raw')]:
            bad=copy.deepcopy(expected);bad[key]=value
            with self.assertRaises(AssertionError):check(bad,before)
        bad=copy.deepcopy(expected);bad['securityHeaders']['set-cookie']='raw'
        with self.assertRaises(AssertionError):check(bad,before)


if __name__=='__main__':unittest.main()
