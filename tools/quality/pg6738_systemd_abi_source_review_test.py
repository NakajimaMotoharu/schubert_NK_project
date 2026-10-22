import unittest
import pg6738_systemd_abi_source_review as p


class IndependentAbiSourceReviewTest(unittest.TestCase):
    def test_exact_all21_against_independent_document(self):
        actual=p.verify((p.ROOT/p.MAIN).read_text(),(p.ROOT/p.SPEC).read_text())
        self.assertEqual(21,len(actual));self.assertEqual('V:P',actual['free'])

    def test_swapped_actual_layout_or_resolver_does_not_qualify(self):
        text=(p.ROOT/p.MAIN).read_text();oracle=(p.ROOT/p.SPEC).read_text()
        for altered in (text.replace('var octet = ValueLayout.JAVA_BYTE;','var octet = ValueLayout.JAVA_LONG;'),
                        text.replace('? libc : systemd','? systemd : libc')):
            with self.assertRaises(ValueError):p.verify(altered,oracle)

    def test_oracle_missing_symbol_or_changed_argument_detected(self):
        text=(p.ROOT/p.MAIN).read_text();oracle=(p.ROOT/p.SPEC).read_text()
        for altered in (oracle.replace('|sd_bus_new|I:P|',''),
                        oracle.replace('|sd_bus_call|I:PPLPP|','|sd_bus_call|I:PPIPP|')):
            with self.assertRaises(ValueError):p.verify(text,altered)


if __name__=='__main__':unittest.main()
