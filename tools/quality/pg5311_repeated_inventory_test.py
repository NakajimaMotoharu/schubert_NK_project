import unittest
import pg5311_repeated_inventory as role


class ExactRepetitions(unittest.TestCase):
    def test_only_declared_literal_noarg_repetitions_are_expanded(self):
        source='@Test void normal() {}\n@RepeatedTest(3)\nvoid repeated() throws Exception {}'
        self.assertEqual(role.expected(['normal'],{'repeated':3},source),
            ['normal','repeated()[1]','repeated()[2]','repeated()[3]'])
        self.assertEqual(role.detail('repeated()[2]',{'repeated':3}),
            {'declaredMethod':'repeated','observedInvocation':'repeated()[2]','declaredRepetition':{'number':2,'count':3}})
        self.assertEqual(role.detail('normal',{'repeated':3}),{})
        with self.assertRaises(ValueError):role.detail('repeated()[4]',{'repeated':3})

    def test_missing_changed_custom_parameterized_duplicate_or_invalid_contract_refused(self):
        literal='@RepeatedTest(3) void repeated() {}'
        for source,declared in [(literal,{}),(literal,{'repeated':2}),
            ('@RepeatedTest(value=3) void repeated() {}',{'repeated':3}),
            ('@RepeatedTest(3) void repeated(String arg) {}',{'repeated':3}),
            (literal+'\n'+literal,{'repeated':3}),
            (literal+'\n@ParameterizedTest void other() {}',{'repeated':3})]:
            with self.assertRaises(ValueError):role.expected([],declared,source)
        for count in (False,0,-1,101,'3',3.0):
            with self.assertRaises(ValueError):role.expected([],{'repeated':count},literal)
        with self.assertRaises(ValueError):role.expected(['repeated'],{'repeated':3},literal)
        with self.assertRaises(ValueError):role.expected(['repeated()[1]'],{'repeated':3},literal)
        with self.assertRaises(ValueError):role.expected(['normal','normal'],{},'')

    def test_missing_duplicate_unknown_invocation_never_matches_fixed_inventory(self):
        expected=role.expected([],{'repeated':3},'@RepeatedTest(3) void repeated() {}')
        for actual in (expected[:-1],expected+[expected[0]],['repeated()[1]','repeated()[2]','repeated()[4]']):
            self.assertNotEqual(sorted(actual),expected)


if __name__=='__main__':unittest.main()
