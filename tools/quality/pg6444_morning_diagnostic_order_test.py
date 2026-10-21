import unittest
from pyflakes.api import checkPath
import pg6444_morning_diagnostic_order as subject

FAILURE = '''
  0: aload_1
  1: invokestatic #1 // Method java/util/Objects.requireNonNull:(Ljava/lang/Object;)Ljava/lang/Object;
  4: pop
  5: aload_0
  6: invokevirtual #2 // Method emit:(Ljava/lang/String;)V
  9: goto 13
  12: astore_2
  13: return
 Exception table:
  5 9 12 Class java/lang/RuntimeException
  5 9 12 Class java/lang/Error
'''
PHASE = '  0: invokevirtual #2 // Method emit:(Ljava/lang/String;)V\n  3: return\n'
OUTER = {'  private void completion();': '  0: invokevirtual #3 // Method MorningStartupLaunchOwner$CompletionProgress.failure:(Ljava/lang/Throwable;)V\n  3: invokestatic #4 // Method retain:()V\n  6: return\n'}


class Definition(unittest.TestCase):
    def test_explicit_protected_span_and_direct_retention_edge(self):
        value = subject.analyze({' void failure(java.lang.Throwable);': FAILURE, ' void phase(Phase);': PHASE}, OUTER)
        self.assertEqual((1, 5, 9, 12, 3), tuple(value[k] for k in ('nullCheckOffset', 'protectedStart', 'protectedEnd', 'diagnosticHandler', 'nextRetainOffset')))
        self.assertFalse(value['actualNativeRetentionProven'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_error_unprotected_emit_or_unwind_cannot_pass(self):
        for bad in (FAILURE.replace('  5 9 12 Class java/lang/Error\n', ''),
                    FAILURE.replace('5 9 12', '7 9 12'), FAILURE.replace('13: return', '13: athrow')):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                subject.analyze({' void failure(java.lang.Throwable);': bad, ' void phase(Phase);': PHASE}, OUTER)
        wrong = {k: v.replace('Method retain:', 'Method ordinaryReturn:') for k, v in OUTER.items()}
        with self.assertRaisesRegex(ValueError, 'directly'):
            subject.analyze({' void failure(java.lang.Throwable);': FAILURE, ' void phase(Phase);': PHASE}, wrong)


if __name__ == '__main__':
    unittest.main()
