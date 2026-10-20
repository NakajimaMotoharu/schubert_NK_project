import unittest
from pg5872_terminal_identity8_review import guarded_identity


class DirectThrowableGuardTest(unittest.TestCase):
    def test_inclusive_span_whole_condition_and_no_intervening_callback(self):
        prefix='if (';expr='failure != closing';text=prefix+expr+') { failure.addSuppressed(closing); }'
        fact={'operator':'NOT_EQUAL_TO','leftExpression':'failure','rightExpression':'closing','firstLine':1,'lastLine':1,'firstColumn':len(prefix)+1,'lastColumn':len(prefix)+len(expr)}
        self.assertEqual('DISTINCT_THROWABLE_APPEND',guarded_identity(text,fact,False))
        for bad in(text.replace(') { failure',') { callback(); failure'),text.replace('addSuppressed(closing)','addSuppressed(other)'),text.replace('failure != closing','failure != unknown')):
            with self.assertRaises(ValueError):guarded_identity(bad,fact,False)
        for delta in(-1,1):
            with self.assertRaises(ValueError):guarded_identity(text,{**fact,'lastColumn':fact['lastColumn']+delta},False)


if __name__=='__main__':unittest.main()
