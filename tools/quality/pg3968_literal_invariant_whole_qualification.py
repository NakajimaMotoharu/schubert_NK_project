"""Independent whole3717, original3716 case retention and exact registered Main families."""
import ast
import inspect
import json
import pg3738_hygiene_whole_qualification as previous
from pg3966_literal_invariant_full_six import ROOT, W, SOURCE, EXPECTED, NEW_CASES, MAIN, require


def qualification_inputs(original):
    old = json.loads((W / 'pg3930-current-boundary-whole-qualified-v1/manifest.safe.json').read_bytes())['result']
    literal = json.loads((W / 'pg3952-literal-candidate-v1/manifest.safe.json').read_bytes())['result']
    return {'source': SOURCE, 'snapshot': original['snapshot'], 'expected': EXPECTED, 'newCases': NEW_CASES, 'priorManifestSha256': old['serverManifestSha256'],
            'priorJarHashes': old['jarHashes'], 'approvedChangedSources': sorted(set(literal['changes']) | {MAIN})}


def server_code():
    class Current(ast.NodeTransformer):
        count = 0
        def visit_Compare(self, node):
            node = self.generic_visit(node)
            if isinstance(node.left, ast.Call) and isinstance(node.left.func, ast.Name) and node.left.func.id == 'len' and len(node.left.args) == 1 and isinstance(node.left.args[0], ast.Name) and node.left.args[0].id == 'additions':
                require(len(node.comparators) == 1 and isinstance(node.comparators[0], ast.Constant) and node.comparators[0].value == 2, 'exact old two-case cardinality boundary')
                node.comparators[0].value = 1; self.count += 1
            return node
        def visit_Constant(self, node):
            value = node.value
            if type(value) is int and value in {3712, 3714}: return ast.copy_location(ast.Constant({3712: 3716, 3714: 3717}[value]), node)
            if isinstance(value, str):
                value = value.replace('PG3738-hygiene-whole-qualified-v1', 'PG3968-literal-invariant-whole-qualified-v1').replace('PG3734', 'PG3966').replace('PG3412', 'PG3928')
                value = value.replace('all original3712 exact identities retained plus exactly2 actual independent Root tests', 'all original3716 exact identities retained plus exactly1 independent immutable boundary Test')
                return ast.copy_location(ast.Constant(value), node)
            return node
    transform = Current(); tree = ast.fix_missing_locations(transform.visit(ast.parse(inspect.getsource(previous.server))))
    require(transform.count == 1, 'one exact new-case comparison changed')
    return ast.unparse(tree)


def qualification_payload(original):
    return '\n'.join(inspect.getsource(f) for f in [require, previous.source_file, previous.classify]) + '\n' + server_code() + '\nserver(' + repr(qualification_inputs(original)) + ')\n'


def main():
    raw = inspect.getsource(previous.main).replace('pg3734-server-six-v1', 'pg3966-server-six-v1').replace('pg3738-hygiene-whole-qualified-v1', 'pg3968-literal-invariant-whole-qualified-v1').replace('PG3738-hygiene-whole-qualified-v1', 'PG3968-literal-invariant-whole-qualified-v1')
    values = {**previous.__dict__, 'SOURCE': SOURCE, 'qualification_payload': qualification_payload}
    exec(compile(raw, '<independent new-Main3717 qualification>', 'exec'), values)
    return values['main']()


if __name__ == '__main__':
    raise SystemExit(main())
