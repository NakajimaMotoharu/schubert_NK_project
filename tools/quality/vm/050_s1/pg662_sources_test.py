"""BOOT662001 independent current binding, one start and no source/DB changes."""
import ast
import unittest
from pg662_sources import java, refs, receipt, join, native, compile_script


class Test(unittest.TestCase):
    def test_current_generation_and_scopes(self):
        j=java();r=refs();n=native();c=compile_script()
        for raw in(j,r,n):
            self.assertNotIn('0.1.0-PG548',raw)
            self.assertNotIn('969d8ded',raw)
        self.assertIn('36fe7a0b938489d61d17d49c1c30a6fbbef699d5',j)
        self.assertIn('601297d0-a8ba-47da-852b-0ffeae409965',j)
        self.assertIn('2026-10-08T22:03:10.738020Z',j)
        self.assertIn('pg661-completed-baseline-v1/before.private.json',r)
        self.assertIn("len(baseline)==20",r)
        self.assertIn("==514)",r)
        self.assertIn('==109694780700',r)
        self.assertIn("parent_rows==baseline['parentPid1']",r)
        self.assertIn('PREPARE_DATABASE_SCOPE_CLOSE',j)
        self.assertIn('POST_DATABASE_SCOPE_CLOSE',j)
        self.assertEqual(c.count('pg631-release-v1/'),4)
        for raw in(r,n,receipt(),join()):ast.parse(raw)

    def test_single_durable_normal_start_and_preservation(self):
        r=refs();tree=ast.parse(r)
        starts=[n for n in ast.walk(tree)if isinstance(n,ast.List)and len(n.elts)>=3
                and all(isinstance(e,ast.Constant)for e in n.elts[:3])
                and [e.value for e in n.elts[:3]]==['/usr/bin/systemctl','start','--no-block']]
        self.assertEqual(len(starts),1)
        self.assertLess(r.index("save('start-reserved.private.json'"),r.index("command(['/usr/bin/systemctl','start'"))
        for guard in ("require(data==baseline['rows'])","same_terminal_cohort(baseline['units'],current,terminal)",
                      "native_tree(baseline['native'],trees['native'],native_invocation)",
                      "namespace==baseline['namespace']","verify_fixed_fields()",
                      "('bootstrapOldProofs','pg570-bootstrap-existing-v1')",
                      "('bootstrapTools','pg570-bootstrap-tools-v1')","('unitFiles','pid1Stop')"):
            self.assertIn(guard,r)
        self.assertIn("secrets.token_hex(16)",r)
        self.assertIn('secrets.token_urlsafe(32)',r)
        self.assertIn('os.O_EXCL|os.O_NOFOLLOW',r)
        self.assertIn('retire_no_replace(credsfd,name,savefd)',r)
        self.assertIn("prior['actualExit'] == 0 and prior['toolHashes'] == hashes",native())
        for forbidden in('reset-failed','daemon-reload','restart','kill -','update schubert','delete from'):
            self.assertNotIn(forbidden,r.lower())


if __name__=='__main__':unittest.main()
