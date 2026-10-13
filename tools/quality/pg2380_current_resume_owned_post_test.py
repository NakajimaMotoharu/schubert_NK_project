"""Actual whole emitted post closure and immutable namespace; no SSH invocation."""
import ast
import json
import unittest
import pg2380_current_resume_owned_post as p
from pg1446_current_cold_stage import W
import pg1257_fresh_independent_terminal_post as seal_schema


class Stopped(unittest.TestCase):
    def test_exact_current_full_post_namespace_and_no_lifecycle(self):
        old=json.loads((W/'pg2281-current-signed-owned-post-v2/manifest.safe.json').read_bytes())
        seals={n:old['proofHashes'][n]['sha256']for n in seal_schema.previous.SEALS}
        live=json.loads((W/'pg2362-current-resume-live-binding-v1/manifest.safe.json').read_bytes())
        raw=p.emit(seals,p.previous.prior.context(),live)
        for n in ['pg2368-current-resume-full-seal-v1',p.TOOLS,'PG2380-current-resume-owned-post-v1','0.1.0-PG2126']:self.assertIn(n,raw)
        self.assertNotIn('pg2274',raw);self.assertNotIn('Pg2274',raw)
        for n in ast.walk(ast.parse(raw)):
            if isinstance(n,ast.List):self.assertFalse({'start','stop','restart','reload','daemon-reload','reset-failed'}&{getattr(v,'value',None)for v in n.elts if isinstance(v,ast.Constant)})


if __name__=='__main__':unittest.main()
