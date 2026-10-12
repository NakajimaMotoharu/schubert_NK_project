"""Actual candidate remains separately labelled and strict full-byte post is retained."""
import unittest
from unittest.mock import patch
import json
from pg1853_warning_unused_independent_post import payload,engine,CANDIDATE


class Post(unittest.TestCase):
    def test_actual_emitted_candidate_all187_signature_oldwarning_and_inode(self):
        post=json.loads((engine.W/'pg1838-warning-terminal-independent-post-v1/manifest.safe.json').read_bytes())
        real=engine.Path.read_bytes
        def read(path):
            if path.name=='pg1846-candidate-build-v1.safe.json':return json.dumps({'actualExit':0,'manifestSha256':'b'*64,'signatureSha256':'c'*64}).encode()
            return real(path)
        with patch.object(engine.Path,'read_bytes',read):raw=payload(post)
        for s in ['pg1852-warning-unused-placement-v1','0.1.0-PG1846',CANDIDATE,'unusedCandidate187Verified','managerFailureRetained=true','len(sums)==187','openssl','s.st_nlink==1']:
            self.assertIn(s,raw)
        self.assertNotIn('genuineParentDone=true',raw)
        self.assertNotIn('StartUnit',raw)


if __name__=='__main__':unittest.main()
