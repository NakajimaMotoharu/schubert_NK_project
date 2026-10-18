"""Hash-verified new six XML, native session IDs redacted; no formal acceptance."""
import ast
import pg4928_current_native_public as previous
from pg5072_current_native_qualified import SOURCE, FULL

SLOT = 'pg5074-current-native-public-v1'
PUBLIC = previous.PUBLIC.parent / 'PG5072-current-native-measurement-v1'


def source():
    raw = previous.source()
    for a, b in [('pg4926-current-native-qualified-v1', 'pg5072-current-native-qualified-v1'),
                 ('pg4846-ssc301-302-whole-qualified-v1', FULL), ('PG4926-native-v1', 'PG5072-native-v1'),
                 ('PG4926-current-native-measurement-v1', 'PG5072-current-native-measurement-v1')]:
        raw = raw.replace(a, b)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self, node):
            if type(node.value) is int and node.value in {3761, 551, 1647, 1655}:
                node.value = {3761: 3791, 551: 553, 1647: 1650, 1655: 1657}[node.value]
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def main():
    template = previous.previous.previous
    ns = {**vars(template), 'SOURCE': SOURCE, 'SLOT': SLOT, 'PUBLIC': PUBLIC}
    exec(compile(source(), '<same current3791 native redacted evidence>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
