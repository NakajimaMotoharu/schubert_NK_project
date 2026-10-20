import unittest
import pg5830_isolation_static as target


class ExactIsolationDeltaTest(unittest.TestCase):
    def test_no_byte_or_rule_scope_widening(self):
        original={str(i):'old'for i in range(1665)}
        modified={target.class_key(p)for p in target.MODIFIED}
        for i,name in enumerate(sorted(modified)):
            original[name]=original.pop(str(i))
        current={**original,**{k:'new'for k in modified},target.class_key(target.ADDED):'new'}
        self.assertEqual(7,len(target.class_contract(original,current)))
        for key in(set(original)-modified):
            bad={**current,key:'unexpected'}
            with self.assertRaises(ValueError):target.class_contract(original,bad)
            break
        raw=target.runner_source()
        for s in('actualAuxClasses\':1666','inputSourceFiles\':851','unchangedPhysicalClasses\':1659','pmdProcessingErrors','checkstyleFindings'):
            self.assertIn(s,raw)
        self.assertNotIn('failIfNoTests=false',raw)


if __name__=='__main__':unittest.main()
