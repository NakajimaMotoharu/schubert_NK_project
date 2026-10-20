import unittest
import pg6048_current_jdbc24_review as t


class CurrentCaseJoinTest(unittest.TestCase):
    def test_identity_alias_position_not_allocation_or_guessed_line(self):
        helper = 'private static <T> T present(@Nullable T value) throws SQLDataException { if (value == null) throw new SQLDataException("fixed"); return value; }'
        body = '{\n var query = present(statement);\n use(query);\n}'
        text = '// 日本語 😀\n'+helper+'\nvoid f(){\n var statement = acquire();\n try '+body+' finally { close(); }\n}'
        scope = dict(body=body, variable='statement')
        alias = t.alias_binding(text, scope)
        self.assertEqual(('query', 6, 6), (alias['alias'], alias['firstLine'], alias['lastLine']))
        for bad in (text+'\n'+body, text.replace('return value;', 'return other;'), text.replace('present(statement)', 'present(other)')):
            with self.assertRaises(ValueError):
                t.alias_binding(bad, dict(scope) | {'body': body.replace('present(statement)', 'present(other)') if 'present(other)' in bad else body})

    def test_no_old_pass_or_absent_case_join(self):
        ref = dict(**{'class': 'Example'}, caseNameSha256='a'*64)
        row = dict(ref, testId='new', xmlSha256='b'*64, source=t.SOURCE, result='PASS_ORIGINAL_XML')
        self.assertEqual('new', t.current_refs([ref], {('Example', 'a'*64): row})[0]['testId'])
        with self.assertRaises(ValueError):
            t.current_refs([ref], {})
        with self.assertRaises(ValueError):
            t.current_refs([ref], {('Example', 'a'*64): dict(row) | {'source': t.OLD}})
        self.assertEqual([], t.current_refs([], {}, True))
        with self.assertRaises(ValueError):
            t.current_refs([], {}, False)


if __name__ == '__main__':
    unittest.main()
