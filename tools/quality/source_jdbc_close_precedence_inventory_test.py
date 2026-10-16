"""Independent typed source fixtures: only exact approved close/primary precedence is recognized."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
JDK = pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')


def facts(raw):
    result = []
    for line in raw.splitlines():
        fields = line.split('\t')
        if len(fields) != 7 or fields[0] != 'JDBC_CLOSE' or not fields[1].endswith('.java'):
            raise ValueError('exact typed close fact schema')
        if not 0 < int(fields[2]) <= int(fields[3]) or fields[4] not in {'java.sql.Statement', 'java.sql.ResultSet'}:
            raise ValueError('bounded typed JDBC fact')
        result.append(dict(zip(['kind', 'path', 'firstLine', 'lastLine', 'resourceType', 'primary', 'secondary'], fields)))
    return result


class DirectJdbcClose(unittest.TestCase):
    def test_exact_shape_and_independent_nonmatching_sources(self):
        template = 'void NAME(java.sql.Statement s, java.sql.Statement other) throws java.sql.SQLException { Throwable primary=null; try {work();} catch(java.sql.SQLException|RuntimeException|Error original){primary=original;throw original;} finally { if(s!=null){try{s.close();}catch(java.sql.SQLException|RuntimeException|Error secondary){if(JdbcResourceFailures.replace(primary,secondary))throw secondary;}}}}'
        samples = [('good', template), ('direct', template.replace('if(s!=null){try', 'try').replace('throw secondary;}}}}', 'throw secondary;}}}')),
                   ('annotated', template.replace('Throwable primary', '@MaybeNull Throwable primary')),
                   ('wrongArgument', template.replace('replace(primary,secondary)', 'replace(primary,new Error())')),
                   ('wrongThrow', template.replace('throw secondary;', 'throw new Error();')),
                   ('wrongHelper', template.replace('JdbcResourceFailures.replace', 'Other.replace')),
                   ('wrongPrimaryCapture', template.replace('primary=original;', 'primary=null;')),
                   ('reversedCondition', template.replace('if(JdbcResourceFailures', 'if(!JdbcResourceFailures')),
                   ('wrongResourceGuard', template.replace('if(s!=null)', 'if(other!=null)')),
                   ('wrongCaughtTypes', template.replace('java.sql.SQLException|RuntimeException|Error secondary', 'java.sql.SQLException|RuntimeException secondary'))]
        fixture = 'package dev.codex.schubert.nk.batch.repository;\nclass Fixture { static void work() throws java.sql.SQLException {}\n' + '\n'.join(text.replace('NAME', name) for name, text in samples) + '\n}\nclass JdbcResourceFailures {static boolean replace(@MaybeNull Throwable p,Throwable s){return p==null;}}\nclass Other {static boolean replace(Throwable p,Throwable s){return p==null;}}\n@java.lang.annotation.Target(java.lang.annotation.ElementType.TYPE_USE) @interface MaybeNull {}\n'
        with tempfile.TemporaryDirectory(prefix='pgpt-jdbc-finally-') as folder:
            base = pathlib.Path(folder); classes = base / 'classes'; classes.mkdir(); source = base / 'source'; source.mkdir()
            (source / 'Fixture.java').write_text(fixture)
            compile_result = subprocess.run([str(JDK / 'javac'), '-Xlint:all', '-Werror', '-d', str(classes), str(ROOT / 'tools/quality/SourceJdbcClosePrecedenceInventory.java')], capture_output=True, text=True, timeout=30)
            self.assertEqual(0, compile_result.returncode, compile_result.stderr)
            result = subprocess.run([str(JDK / 'java'), '-cp', str(classes), 'SourceJdbcClosePrecedenceInventory', str(source), ''], capture_output=True, text=True, timeout=30)
            self.assertEqual(0, result.returncode, result.stderr)
            rows = facts(result.stdout)
            self.assertEqual(3, len(rows))
            self.assertEqual({'3', '4', '5'}, {r['firstLine'] for r in rows})
            self.assertTrue(all(r['primary'] == 'primary' and r['secondary'] == 'secondary' for r in rows))

    def test_malformed_extent_kind_or_resource_type_refused(self):
        for raw in ['WRONG\tF.java\t1\t2\tjava.sql.Statement\tp\ts', 'JDBC_CLOSE\tF.java\t2\t1\tjava.sql.Statement\tp\ts', 'JDBC_CLOSE\tF.java\t1\t2\tjava.lang.Object\tp\ts']:
            with self.assertRaises(ValueError):
                facts(raw)


if __name__ == '__main__':
    unittest.main()
