import unittest
import pg5844_protocol_expression_green as target


class ProtocolExpressionProfileTest(unittest.TestCase):
    def test_exact_complete_protocol_and_unchanged_other_guards(self):
        from pg5540_snapshot_scratch_selected import ROOT
        actual={p.relative_to(ROOT/'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk').as_posix()[:-5].replace('/','.')for p in(ROOT/'src/schubert-nk-protocol/src/test/java').rglob('*Test.java')}
        self.assertEqual(actual,target.CASES['protocol']);self.assertEqual(20,len(actual))
        total=0
        for m,classes in target.CASES.items():
            for c in classes:
                path=ROOT/('src/schubert-nk-'+m+'/src/test/java/dev/codex/schubert/nk')/(c.replace('.','/')+'.java');count=len(target.source_test_names(path))
                self.assertEqual(target.COUNTS[c.rsplit('.',1)[1]],count);total+=count
        self.assertEqual(105,total);self.assertEqual(6,sum(map(len,target.TARGETS.values())))
        raw=target.runner_source();self.assertNotIn('failIfNoTests=false',raw);self.assertNotIn('lan_server',raw)
        self.assertIn('done=done and target100',raw)


if __name__=='__main__':unittest.main()
