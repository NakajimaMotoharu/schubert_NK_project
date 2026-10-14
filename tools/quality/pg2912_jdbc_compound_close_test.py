"""No Main compilation, exact real DB all Session methods, no coverage claim."""
import unittest
import pg2912_jdbc_compound_close_selected as p


class TestOnlyContract(unittest.TestCase):
    def test_complete_server_and_exact_inputs(self):
        raw=p.server()
        self.assertEqual(2,len(p.FILES))
        self.assertTrue(all('/src/main/'not in n for n in p.FILES))
        for v in ['source-full-PG2798',"'mainRecompiled':False",'require(not mainclasses)', 'mdb2804001CheckedCallbackAndCompoundJdbcClosePreserveRowsAndRedactSecondary','Pg2796JdbcContractLauncher']:
            self.assertIn(v,raw)

    def test_completed_transport_count_uses_named_test_not_ordinal(self):
        raw=p.transport_body()
        self.assertNotIn('ROOT/FILES[1]',raw)
        self.assertIn('(ROOT/TEST).read_text()',raw)
        self.assertIn('pg2912-jdbc-compound-close-selected-v2',raw)
        self.assertEqual(61,(p.prior.ROOT/p.TEST).read_text().count('@Test\n'))
        self.assertEqual(0,(p.prior.ROOT/p.FILES[1]).read_text().count('@Test\n'))


if __name__=='__main__':unittest.main()
