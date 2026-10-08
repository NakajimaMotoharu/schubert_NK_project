"""Local convention preflight, not a javac/NullAway substitute. Emit paths/lines only."""
import pathlib
import re

LITERALS = re.compile(r'"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*[\s\S]*?\*/|//[^\n]*')
QUALIFIED = re.compile(r'@(?:org\.jspecify\.annotations\.)?Nullable\s+[A-Za-z_$][\w$]*(?:\s*\.\s*[A-Za-z_$][\w$]*)+')


def violations(source):
    clean = LITERALS.sub(lambda m: re.sub(r'[^\n]', ' ', m.group()), source)
    return [clean.count('\n', 0, m.start()) + 1 for m in QUALIFIED.finditer(clean)]


def fixtures():
    valid = ('@Nullable Object x;', 'java.security.@Nullable CodeSource x;',
             'Outer.@Nullable Inner x;', 'String x="@Nullable Wrong.Type";',
             '/* @Nullable Wrong.Type */', 'String x="""\n@Nullable Wrong.Type\n""";')
    invalid = ('@Nullable java.security.CodeSource x;', '@Nullable Outer.Inner x;')
    assert all(violations(s) == [] for s in valid)
    assert all(violations(s) == [1] for s in invalid)
    return len(valid) + len(invalid)


def main():
    count = fixtures()
    root = pathlib.Path('src/schubert-nk-bootstrap/src')
    files = sorted(root.glob('main/java/**/*.java')) + sorted(root.glob('test/java/**/*.java'))
    assert files
    bad = [(str(p), line) for p in files for line in violations(p.read_text())]
    print({'qualifiedNullableFixtures': count, 'javaFiles': len(files), 'violations': bad,
           'compilerAndNullAwayStillRequired': True})
    assert not bad


if __name__ == '__main__':
    main()
