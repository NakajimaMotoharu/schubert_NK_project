import re
import subprocess
import unittest
import pg5314_readiness_stream_selected as role
import pg5311_repeated_inventory as repeated

PATH='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MorningCaddyReadinessTest.java'
NAMES=('caddyStream001SameInputIsClosedOnceWithoutReading','caddyStream002AbsentBodyKeepsOldNoResourceContract',
       'caddyStream003GetterFailuresKeepOriginalIdentity','caddyStream004CloseFailureKeepsFixedIoAndUnknownPriority',
       'caddyStream005NullSourceIsRejectedBeforeAcquisition','caddyStream006ParallelStreamsKeepSeparateOwnership')


class ReadinessScope(unittest.TestCase):
    def test_three_new_suites30_cases_old14_unchanged(self):
        root=role.selected.ROOT;actual={}
        for name in role.RELATED:
            path=root/('src/schubert-nk-batch/src/test/java/'+name.replace('.','/')+'.java')
            raw=path.read_text();methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(methods),raw.count('@Test'))
            self.assertEqual(repeated.expected(methods,{},raw),sorted(methods))
            actual[name.rpartition('.')[2]]=len(methods)
        self.assertEqual(actual,{'MorningCaddyReadinessTest':20,'MorningServiceReadinessTest':7,'MorningServiceReadinessNativeTest':3})
        self.assertFalse(set(role.RELATED)&set(role.previous.extra_suites()))
        current=(root/PATH).read_text()
        old=subprocess.check_output(['git','show','c29752dbe4de7b24ee92bfa4fb71f2e164c16515:'+PATH],cwd=root,text=True)
        marker='  static final String INV'
        self.assertEqual(old[old.index(marker):],current[current.index(marker):])
        self.assertEqual(tuple(re.findall(r'@Test\s+void\s+(caddyStream[A-Za-z0-9_]+)\(',current)),NAMES)

    def test_scope_and_repeated_provenance_are_explicit(self):
        role.configure()
        self.assertEqual(len(role.selected.EXTRA_CHANGED),53)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),165)
        self.assertEqual(len(role.extra_suites()),98)
        self.assertEqual(role.repetitions(),{'dev.codex.schubert.nk.batch.file.BackupStartIntentFilesTest':
            {'concurrentDistinctOwnersCannotPublishTwoIntents':10}})


if __name__=='__main__':unittest.main()
