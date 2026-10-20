"""Independently read original199 XML/all1666 bytes/six targets; never replay PT."""
import ast
import inspect
import pg5850_protocol_expression_public as previous
from pg5904_storage30_selected import CASES, COUNTS, TARGETS, source_test_names

SOURCE = '7a664ce0a99860bb75e1e1a3ae30354a9840528a'


def reader_source():
    raw = inspect.getsource(previous.main)
    changes = {
        'pg5844-protocol-expression-selected105-v1': 'pg5904-storage30-selected199-v1',
        'PG5848-protocol-expression-static-v1': 'PG5906-storage30-static-v1',
        'pg5848-protocol-expression-static-v1': 'pg5906-storage30-static-v1',
        '3c2ce6616b6b050543ec7ab9e580f2f2890d8bbf58fc7597da35a913c2f24100': 'a0c4d80e21a1a20a05928d26a35168be6802aa01e2bc8a682bb6e49959ca5365',
        'PG5850-protocol-expression105-v1': 'PG5908-storage199-v1',
        "'protocolTests'": "'storageTests'"}
    for old, new in changes.items():
        if old not in raw:
            raise ValueError('explicit current storage reader binding')
        raw = raw.replace(old, new)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self, node):
            values = {105: 199, 26: 33, 96: 188, 8: 30, 1586: 1556}
            return ast.copy_location(ast.Constant(values[node.value]), node) if type(node.value) is int and node.value in values else node
    raw = ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    compile(raw, '<original storage199 independent reader>', 'exec')
    return raw


def main():
    scope = {**vars(previous), 'SOURCE': SOURCE, 'CASES': CASES, 'COUNTS': COUNTS, 'TARGETS': TARGETS, 'source_test_names': source_test_names}
    exec(compile(reader_source(), '<original storage199 reader>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    main()
