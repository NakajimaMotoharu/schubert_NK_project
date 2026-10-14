"""Independent finite golden/all phases/negative retained metadata + source graph."""
import inspect
import unittest
import pg1083_cold_publication_contract_test as old_test
import pg2852_network_cold_publication_sources as p


class ColdPublication(unittest.TestCase):
    def test_current_literal_finite_all_negative_vectors(self):
        raw=p.bind(inspect.getsource(old_test))
        marker='from pg1083_cold_publication_contract import verify,epoch_bytes,verify_retained'
        raw=p.ro.unused.one(raw,marker,'verify=protocol.verify;epoch_bytes=protocol.epoch_bytes;verify_retained=protocol.verify_retained')
        raw=p.ro.unused.one(raw,'0o777,37,target=', '0o777,38,target=')
        env={'__name__':'independent_current_finite','protocol':p.protocol()}
        exec(compile(raw,'<independent newboot finite golden>','exec'),env)
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(env['Finite'])
        result=unittest.TestResult();suite.run(result)
        self.assertEqual([],result.errors);self.assertEqual([],result.failures)
        self.assertGreaterEqual(result.testsRun,8)

    def test_exact_empty_startup_once_finite_and_whole_namespace(self):
        j=p.java();r=p.observer()
        for v in [p.CLASS,p.SAVE,'79a3260a-e16d-42bf-942a-b914ed144c28','04207efc3ad78bca75942153a90c70985064c988',
            'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25']:
            self.assertTrue(v in j,v)
        for v in ['"activate".equals(args[0])','entries.findAny().isEmpty()','StartupPermitRecords.State.INVALID','StandardCopyOption.ATOMIC_MOVE','refs.check("exchange")']:
            self.assertTrue(v in j,v)
        self.assertFalse('freezeCandidate()'in j)
        self.assertTrue('value[\'children\']==expected_runtime[\'children\']'in r)
        self.assertTrue('a==b and a==prepared[\'current\']'in r)
        self.assertTrue('PEER_CLOSED=True'in r)
        self.assertTrue('pub.verify_retained('in r)
        self.assertTrue('pg2852-current.part'in r)
        self.assertFalse('pg1088-current.part'in r)


if __name__=='__main__':unittest.main()
