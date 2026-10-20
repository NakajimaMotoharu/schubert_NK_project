"""Read original35 XML and all1666 bytes; no new test/runtime execution."""
import ast
import inspect
import pg5850_protocol_expression_public as previous
from pg5912_api_expression_selected import CASES, COUNTS, TARGETS, source_test_names

SOURCE = '682a4b99eb0b95bcd4f1cd276fea75b5f2e62e3b'


def three100(counters):
    return len(counters) == 3 and all(set(c) == {'LINE', 'METHOD', 'CLASS', 'BRANCH'} and all(
        c[k]['missed'] == 0 and (c[k]['covered'] > 0 or k == 'BRANCH') for k in c) for c in counters.values())


def reader_source():
    raw = inspect.getsource(previous.main)
    changes = {
        'pg5844-protocol-expression-selected105-v1': 'pg5912-api-expression-selected35-v1',
        'PG5848-protocol-expression-static-v1': 'PG5914-api-expression-static-v1',
        'pg5848-protocol-expression-static-v1': 'pg5914-api-expression-static-v1',
        '3c2ce6616b6b050543ec7ab9e580f2f2890d8bbf58fc7597da35a913c2f24100': '318d3783a5bfa4fe9a3920b252d3449eca01b9131c925758eadf13f8289548b4',
        'PG5850-protocol-expression105-v1': 'PG5916-api35-v1',
        "'protocolTests'": "'apiTests'", 'targetSixFour100': 'targetThreeFour100',
        'actual current105 and full source/static proof': 'actual current35 and full source/static proof',
        'actual105/26, six targets100 and exactly eight PG diagnostics removed': 'actual35/10, three targets100 and exactly twelve PG diagnostics removed'}
    for old, new in changes.items():
        if old not in raw:
            raise ValueError('explicit current API35 reader binding')
        raw = raw.replace(old, new)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self, node):
            values = {105: 35, 26: 10, 96: 24, 8: 12, 1586: 1544}
            return ast.copy_location(ast.Constant(values[node.value]), node) if type(node.value) is int and node.value in values else node
    raw = ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    compile(raw, '<original API35 independent reader>', 'exec')
    return raw


def main():
    scope = {**vars(previous), 'SOURCE': SOURCE, 'CASES': CASES, 'COUNTS': COUNTS, 'TARGETS': TARGETS,
             'source_test_names': source_test_names, 'four100': three100}
    exec(compile(reader_source(), '<original API35 reader>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    main()
