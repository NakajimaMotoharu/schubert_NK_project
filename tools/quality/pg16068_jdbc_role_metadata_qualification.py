"""Pure metadata tool qualification; original Product/failed tools are never executed."""
import ast
import datetime
import io
import json
import platform
import subprocess
import sys
import unittest
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import jdbc_role_metadata_v1 as reader

OUT = data.BASE / 'PG16068-jdbc-role-metadata-qualification-v1'
CORE = data.ROOT / 'tools/quality/jdbc_role_metadata_v1.py'
INPUTS = [
    ('PG16004-batch-run-current-static-review-v1', '2e6c4240a6749477bf58ade99bb44701c382f0d4adb3c8cb0a5b0ad66348976d', 'failure', {
        ('finish', 'statement'): 'query', ('history', 'rows'): 'row', ('history', 'statement'): 'query', ('abandon', 'statement'): 'query', ('insert', 'rows'): 'row', ('insert', 'statement'): 'query', ('replayed', 'rows'): 'row', ('replayed', 'statement'): 'query'}),
    ('PG16058-cleanup-terminal-current-static-review-v1', 'ca58d40993d3e8c9cf3cd008c64de040be242f306adf474e7274da5eb4946864', 'secondary', {
        ('read', 'rows'): 'row', ('read', 'statement'): 'query', ('references', 'rows'): 'row', ('references', 'statement'): 'query', ('progressSeal', 'rows'): 'row', ('progressSeal', 'statement'): 'checked', ('readRejected', 'rows'): 'row', ('readRejected', 'statement'): 'query'}),
]


class MetadataTest(unittest.TestCase):
    def test_Q_JDBCROLE001_three_primary_names_and_two_cleanup_names(self):
        for primary in ('statementFailure', 'rowFailure', 'rowsFailure'):
            for cleanup in ('failure', 'secondary'):
                text = f'if (JdbcResourceFailures.replace({primary}, {cleanup})) throw {cleanup};'
                self.assertEqual(((primary, cleanup, 0, len(text)),), reader.close_conditions(text))

    def test_Q_JDBCROLE002_wrong_conditional_roles_are_not_candidates(self):
        bad = [
            'if (JdbcResourceFailures.replace(rowsFailure, secondary)) throw failure;',
            'if (JdbcResourceFailures.replace(statementFailure, failure)) throw secondary;',
            'if (Other.replace(rowsFailure, secondary)) throw secondary;',
            'if (JdbcResourceFailures.replace(secondary, rowsFailure)) throw rowsFailure;',
            'JdbcResourceFailures.replace(rowsFailure, secondary); throw secondary;',
            'if (JdbcResourceFailures.replace(rowsFailure, secondary)) return secondary;',
            'if (JdbcResourceFailures.replace(rowsFailure, secondary)) throw;',
            'if (JdbcResourceFailures.replace(other, secondary)) throw secondary;',
        ]
        self.assertTrue(all(reader.close_conditions(text) == () for text in bad))

    def test_Q_JDBCROLE003_source_boundary_contract(self):
        for value in (None, False, 0, b'source', {}, [], 'x\r', 'x\0', r'\u0069f', 'x' * (reader.MAXIMUM_SOURCE_CHARACTERS + 1)):
            with self.assertRaises(ValueError):
                reader.close_conditions(value)
        self.assertEqual((), reader.close_conditions(''))
        self.assertEqual((), reader.close_conditions(' ' * reader.MAXIMUM_SOURCE_CHARACTERS))

    def test_Q_JDBCROLE004_positions_immutable_and_lexical_not_authority(self):
        clause = 'if (JdbcResourceFailures.replace(rowsFailure, secondary)) throw secondary;'
        found = reader.close_conditions('x\n' + clause + '\n')
        self.assertEqual((('rowsFailure', 'secondary', 2, len(clause) + 2),), found)
        with self.assertRaises(TypeError):
            found[0] = ()
        # A textual occurrence in a comment is only a candidate. The library is not an AST
        # or permission checker: callers must bind reviewed source/hash/PMD spans separately.
        self.assertEqual(1, len(reader.close_conditions('// ' + clause)))
        tree = ast.parse(CORE.read_text())
        self.assertEqual(['re'], [name.name for node in tree.body if isinstance(node, ast.Import) for name in node.names])
        self.assertFalse(any(isinstance(node, ast.ImportFrom) for node in tree.body))

    def test_Q_JDBCROLE005_alias_positive_roles(self):
        for text, resource, expected in [('var query = present(statement);', 'statement', 'query'), ('var row = present(rows);', 'rows', 'row'), ('var checked = present(statement);', 'statement', 'checked'), ('  var checked = present(statement);\n', 'statement', 'checked')]:
            self.assertEqual(expected, reader.alias_variable(text, resource))

    def test_Q_JDBCROLE006_alias_negative_structure_and_argument(self):
        for text in ('var checked = present(rows);', 'var checked = other(statement);', 'checked = present(statement);', 'var checked = present(null);', 'var checked = present(statement); extra', '', 'var query = present(statement);\nvar row = present(rows);'):
            with self.assertRaises(ValueError):
                reader.alias_variable(text, 'statement')
        for resource in (None, False, 0, b'rows', 'connection', ''):
            with self.assertRaises(ValueError):
                reader.alias_variable('var query = present(statement);', resource)

    def test_Q_JDBCROLE007_alias_null_line_and_length_contract(self):
        for value in (None, False, 0, b'line', {}, [], 'var x = present(statement);\r\n', 'var x = present(statement);\0', r'var \u0078 = present(statement);', 'var x = present(statement);\n\n'):
            with self.assertRaises(ValueError):
                reader.alias_variable(value, 'statement')
        line = 'var query = present(statement);'
        self.assertEqual('query', reader.alias_variable(' ' * (reader.MAXIMUM_ALIAS_CHARACTERS - len(line)) + line, 'statement'))
        with self.assertRaises(ValueError):
            reader.alias_variable(' ' * (reader.MAXIMUM_ALIAS_CHARACTERS + 1), 'statement')

    def test_Q_JDBCROLE008_sixteen_existing_static_sites_not_runtime(self):
        total = 0
        for folder, pin, cleanup, aliases in INPUTS:
            m = data.read_checked(data.BASE / folder / 'manifest.json', pin)
            self.assertEqual(0, m['actualExit'])
            self.assertEqual(0, m['productTestsExecuted'])
            v = data.read_checked(data.BASE / folder / 'review.json', m['reviewSha256'])
            rows = v['rows']
            self.assertEqual(48, len(rows))
            path = rows[0]['path']
            source = (data.ROOT / path).read_text()
            self.assertEqual(rows[0]['sourceSha256'], data.sha(source.encode()))
            expected = {}
            groups = {}
            for row in rows:
                key = row['method'], row['resource']
                groups.setdefault(key, row)
                expected[row['closeCatchLine'] + 1] = row['primaryVariable'], cleanup
            self.assertEqual(set(aliases), set(groups))
            self.assertEqual(8, len(expected))
            actual = {source[:start].count('\n') + 1: (primary, secondary) for primary, secondary, start, end in reader.close_conditions(source)}
            self.assertEqual(expected, actual)
            lines = source.splitlines()
            for key, row in groups.items():
                self.assertEqual(aliases[key], reader.alias_variable(lines[row['aliasLine'] - 1], row['resource']))
            total += len(actual)
        self.assertEqual(16, total)


def main():
    invocation = capture(__file__)
    if OUT.exists():
        raise ValueError('new-only tool evidence')
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    core_pin = data.sha(CORE.read_bytes())
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MetadataTest))
    actual = 0 if result.wasSuccessful() and result.testsRun == 8 and not result.skipped else 1
    if data.sha(CORE.read_bytes()) != core_pin:
        raise ValueError('fixed tool source during qualification')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=actual, invocation=invocation,
        source='6b53efeec87f3ec36a840dd8e7759656cb4aee5c',
        qualificationHead=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=data.ROOT, text=True).strip(),
        startUTC=start, endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        environment=dict(os=platform.platform(), python=sys.version), toolSource=str(CORE.relative_to(data.ROOT)),
        toolSourceSha256=core_pin, toolMetadataTests=result.testsRun, failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
        toolMetadataTestIds=['Q-JDBCROLE' + str(i).zfill(3) for i in range(1, 9)], log=log.getvalue(),
        staticExistingSites=16, existingProductTestsReexecuted=0, productTestsExecuted=0,
        lexicalCandidatesAreNotAstOrPermission=True, allOldExecutedToolsAndProofsUnchanged=True,
        actualVmActions=0, actualDatabaseActions=0, actualRootOrAuthorityActions=0, externalActions=0,
        newAccepted=0, formalUpdated=False, effortPercent=None, wholeF03Accepted=False, whole451Accepted=False,
        originalPlanProgressDelta=0, category='INTERNAL_TOOL_PREVENTION_BUG2155_2156_NOT_PRODUCTION_PROGRESS'))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=actual, toolMetadataTests=result.testsRun, failures=len(result.failures), errors=len(result.errors))))
    raise SystemExit(actual)


if __name__ == '__main__':
    main()
