"""Allowlisted projection of original fresh3814 XML, no new tests/signing/deployment."""
import ast
import inspect
import pg5058_whole_case_projection as previous
from pg5128_root_full import SOURCE

SLOT = 'PG5128-current3814-cases'


def counts(raw):
    class Rebase(ast.NodeTransformer):
        def visit_Constant(self, node):
            if type(node.value) is int and node.value in (3791, 553, 1650):
                return ast.copy_location(ast.Constant({3791:3814, 553:556, 1650:1654}[node.value]), node)
            return node
    return ast.unparse(ast.fix_missing_locations(Rebase().visit(ast.parse(raw))))


def export_source():
    return counts(inspect.getsource(previous.export).replace('PG4968', 'PG5128'))


def main_source():
    raw = inspect.getsource(previous.main)
    if raw.count('inspect.getsource(export)') != 1: raise ValueError('one complete read-only export source')
    raw = raw.replace('inspect.getsource(export)', 'export_source()')
    raw = raw.replace('pg4970-ssc304-whole-qualified-v1', 'pg5130-root-whole-qualified-v1')
    raw = raw.replace('pg5058-original-case-projection-v2', 'pg5132-root-case-projection-v1')
    raw = raw.replace('PG4968', 'PG5128').replace('PG4970', 'PG5130').replace('PG5058_READ_ONLY', 'PG5132_READ_ONLY')
    return counts(raw)


def main():
    ns = {**vars(previous), 'SOURCE':SOURCE, 'SLOT':SLOT, 'export_source':export_source}
    exec(compile(main_source(), '<original3814 case projection only>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    main()
