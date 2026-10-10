import ast
import copy
import json
from pathlib import Path
import unittest
from pg1189_current_resume_a01 import code
from pg876_public_artifact_check import check


class ResumeA01Test(unittest.TestCase):
    def test_actual_current_guard_untouched_shared_driver_and_oracle(self):
        s = code();ast.parse(s)
        for part in ['d5b00104280028d9ea81b44c1d1c805f3c2861ed','pg1183-parent-watch-v1.private.jsonl','pg1182-canonical-runtime-post-v1.safe.json','pg1184-canonical-resume-once-v1.safe.json','canonical-resume-once-v1','cbca8738-3b24-4090-b77c-bf029677cdd6','0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',"issued['MainPID']=='430851'",'a14cc600a4fd4f2e9d8c4731ad9d754b','1800000000','NativeNkA01Capture','122dcc4c1be482ac3239325de6fb3d4bec12747d05adce3929c319ab5bdfd71d',"'fullGate':False"]:
            self.assertTrue(part in s, part)
        for old in ['pg957-ordinary-once-v1','pg954-ordinary-before-v1','pg956-parent-watch','40ef6e894573d2ffab1d1732124960f9c98d5f97']:
            self.assertFalse(old in s, old)

    def test_independent_current_schema_dif001_and_secret_negatives(self):
        root = Path(__file__).resolve().parents[4]
        baseline = json.loads((root/'program/characterization/baseline/current/artifacts/CHR-A01.json').read_bytes())
        literal = copy.deepcopy(baseline);literal['title'] = 'schubert NK - ログイン'
        check(literal, baseline)
        for key, value in [('title','wrong'),('csrf','raw'),('passwordValue','raw'),('passwordAutocomplete','foreign'),('unknown','raw')]:
            bad = copy.deepcopy(literal);bad[key] = value
            with self.assertRaises(AssertionError):check(bad, baseline)
        bad = copy.deepcopy(literal);bad['securityHeaders']['set-cookie'] = 'raw'
        with self.assertRaises(AssertionError):check(bad, baseline)


if __name__ == '__main__':unittest.main()
