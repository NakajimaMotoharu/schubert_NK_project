import subprocess
import tempfile
import unittest
from pathlib import Path
import pg6046_jdbc_ownership_facts as t


class JdbcOwnershipStructureTest(unittest.TestCase):
    def test_independent_positive_and_unprotected_fixtures(self):
        with tempfile.TemporaryDirectory(prefix='pgpt-jdbc-parse-fixture-') as directory:
            root = Path(directory); classes = root/'classes'; classes.mkdir()
            helper = t.ROOT/'tools/quality/SourceJdbcOwnershipInventory.java'
            subprocess.run([str(t.TC/'jdk-25.0.4/bin/javac'), '-proc:none', '-implicit:none', '-Xlint:all', '-Werror', '-d', str(classes), str(helper)], check=True, capture_output=True)
            source = root/'CleanupTerminalRepository.java'
            source.write_text('''class Example {
  void valid() {
    var statement = connection.prepareStatement("quoted \\\" brace { 日本語 😀");
    @Nullable Throwable statementFailure = null;
    try { statement.execute(); }
    catch (SQLException | RuntimeException | Error failure) { statementFailure = failure; throw failure; }
    finally { if (statement != null) { try { statement.close(); }
      catch (SQLException | RuntimeException | Error secondary) {
        if (JdbcResourceFailures.replace(statementFailure, secondary)) throw secondary;
      } } }
  }
  void references() {
    var statement = connection.prepareStatement("select fixed");
    @Nullable Throwable statementFailure = null;
    Entry prior;
    try { use(statement); }
    catch (SQLException | IOException | RuntimeException | Error failure) { statementFailure = failure; throw failure; }
    finally { if (statement != null) { try { statement.close(); }
      catch (SQLException | RuntimeException | Error secondary) {
        if (JdbcResourceFailures.replace(statementFailure, secondary)) throw secondary;
      } } }
  }
  void gap() { var rows = query.executeQuery(); callback(); try { use(rows); } finally { rows.close(); } }
}
''')
            result = subprocess.run([str(t.TC/'jdk-25.0.4/bin/java'), '-cp', str(classes), 'SourceJdbcOwnershipInventory', str(source)], text=True, capture_output=True, check=True)
            records = t.decode_records(result.stdout)
            self.assertEqual(['valid', 'references', 'gap'], [r['method'] for r in records])
            self.assertTrue(t.validate_scope(records[0])['protectedImmediately'])
            self.assertTrue(t.validate_scope(dict(records[0]) | {'finallyBody': records[0]['finallyBody'].replace('secondary', 'failure')})['protectedImmediately'])
            self.assertEqual('Entry prior;', records[1]['nonExecutableDeclarations'])
            self.assertTrue(t.validate_scope(records[1])['declaredIOExceptionPreserved'])
            with self.assertRaises(ValueError):
                t.validate_scope(dict(records[1]) | {'method': 'notReferences'})
            with self.assertRaises(ValueError):
                t.validate_scope(records[2])
            for field, bad in [('catches', 'catch (SQLException failure) { throw failure; }'),
                               ('finallyBody', '{ statement.close(); }'),
                               ('primaryDeclaration', 'Throwable statementFailure = new Error();'),
                               ('finallyBody', records[0]['finallyBody'].replace('replace(statementFailure, secondary)', 'replace(statementFailure, unbound)')),
                               ('finallyBody', records[0]['finallyBody'].replace('Error secondary', 'Throwable secondary'))]:
                with self.assertRaises(ValueError):
                    t.validate_scope(dict(records[0]) | {field: bad})


if __name__ == '__main__':
    unittest.main()
