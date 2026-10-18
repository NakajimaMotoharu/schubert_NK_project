"""Current a2ecc/all1650 physical CRC/session join to original3791/553, no old exec."""
import ast
import json
import subprocess
import pg4926_current_native_qualified as previous
import pg5070_current_native_catalog as catalog
from pg4980_ssc304_signed_candidate import validate_gate

SOURCE = catalog.role.SOURCE
W, P = previous.W, previous.P
FULL = 'pg4970-ssc304-whole-qualified-v1'
SLOT = 'pg5072-current-native-qualified-v1'


def qualify(value):
    return validate_gate(value, SOURCE)


def qualify_snapshot():
    q = qualify(json.loads((W / FULL / 'manifest.safe.json').read_bytes()))
    if (subprocess.check_output(['git', 'status', '--porcelain'])
            or subprocess.check_output(['git', 'diff', q['sourceSnapshot'], 'HEAD', '--',
                                        'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'])):
        raise ValueError('same clean qualified3791 source/Test/settings first')
    catalog.role.admission.authenticate_host()


def server():
    raw = previous.server()
    for a, b in [('PG4926', 'PG5072'), ('PG4844', 'PG4968'),
                 ('qualified4844Tests', 'qualified4968Tests'), (previous.SOURCE, SOURCE)]:
        raw = raw.replace(a, b)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self, node):
            if type(node.value) is int and node.value in {3761, 551, 1647}:
                node.value = {3761: 3791, 551: 553, 1647: 1650}[node.value]
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def source():
    raw = previous.source()
    for a, b in [(previous.catalog.SLOT, catalog.SLOT), (previous.SLOT, SLOT),
                 (previous.FULL, FULL), ('PG4926', 'PG5072')]:
        raw = raw.replace(a, b)
    return raw


def main():
    template = previous.previous
    ns = {**template.transport.entry().__globals__, 'CODE': server(), 'SOURCE': SOURCE,
          'qualify_snapshot': qualify_snapshot}
    exec(compile(source(), '<current3791 exact native transport>', 'exec'), ns)
    with template.management_gate(P / 'current-management-critical.lock'):
        return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
