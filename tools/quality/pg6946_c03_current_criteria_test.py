import unittest
import pg6946_c03_current_criteria as p


class C03CurrentCriteriaTest(unittest.TestCase):
    def test_literal_parser_no_duplicate_missing_or_unbalanced(self):
        self.assertEqual({'port': '5432', 'shared_buffers': '2GB'}, p.settings("# comment\nport = 5432\nshared_buffers = '2GB'\n"))
        for text in ('port=1\nport=2', 'port', "port='unterminated", 'port=', 'bad key=1'):
            with self.assertRaises(ValueError):
                p.settings(text)

    def test_ordered_hba_independent_boundary_literals(self):
        rows = p.hba_expected()
        self.assertEqual(16, len(rows))
        self.assertEqual('local all postgres peer', rows[0])
        self.assertEqual('host schubert_nk schubert_app 127.0.0.1/32 scram-sha-256', rows[1])
        self.assertEqual(['host all all 0.0.0.0/0 reject', 'host all all ::/0 reject'], rows[-2:])

    def test_actual_public_templates_and_unsafe_missing_extra_policy_changes(self):
        conf, hba = [(p.ROOT / path).read_text() for path in p.OWNED]
        p.validate_templates(conf, hba)
        for a, b in ((conf.replace('max_connections = 40', 'max_connections = 0'), hba),
          (conf + '\nunknown=1\n', hba), (conf.replace('port = 5432', ''), hba),
          (conf, hba.replace('scram-sha-256', 'trust')), (conf, '\n'.join(reversed(p.lines(hba)))),
          (conf, hba.replace('host all all ::/0 reject', ''))):
            with self.assertRaises(ValueError):
                p.validate_templates(a, b)

    def test_role_catalog_no_extra_idle_or_duplicate_timeout(self):
        sql = (p.ROOT / p.ROLE_SQL).read_text()
        p.validate_roles(sql)
        for changed in (sql.replace("statement_timeout = '1500ms'", "statement_timeout = '0'"),
          sql + "\nALTER ROLE schubert_inbox_inspector SET idle_in_transaction_session_timeout = '60s';\n",
          sql + "\nALTER ROLE schubert_app SET lock_timeout = '500ms';\n"):
            with self.assertRaises(ValueError):
                p.validate_roles(changed)


if __name__ == '__main__':
    unittest.main()
