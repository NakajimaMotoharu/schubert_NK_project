import unittest
from pg5842_identity13_review import guarded_identity,reader_source


class IsolationConstructorGuardTest(unittest.TestCase):
    def test_actual_inclusive_span_and_no_intervening_effect(self):
        prefix='Objects.requireNonNull(primary, "primary failure"); Objects.requireNonNull(protocolFailure, "protocol failure"); if ('
        expr='protocolFailure != primary';text=prefix+expr+') { addSuppressed(protocolFailure); }'
        fact={'method':'<init>','operator':'NOT_EQUAL_TO','leftExpression':'protocolFailure','rightExpression':'primary','firstLine':1,'lastLine':1,'firstColumn':len(prefix)+1,'lastColumn':len(prefix)+len(expr)}
        self.assertEqual('FRESH_ISOLATION_WRAPPER_CAUSE_NODE_DEDUPLICATION',guarded_identity(text,fact,True))
        for bad in(text.replace(') { addSuppressed',') { mutate(); addSuppressed'),text.replace('addSuppressed(protocolFailure)','addSuppressed(primary)'),text.replace('Objects.requireNonNull(primary','Objects.requireNonNull(other')):
            with self.assertRaises(ValueError):guarded_identity(bad,fact,True)
        for delta in(-1,1):
            with self.assertRaises(ValueError):guarded_identity(text,{**fact,'lastColumn':fact['lastColumn']+delta},True)
        self.assertIn('len(used)!=12',reader_source());self.assertIn("'rawFindings':1594",reader_source())


if __name__=='__main__':unittest.main()
