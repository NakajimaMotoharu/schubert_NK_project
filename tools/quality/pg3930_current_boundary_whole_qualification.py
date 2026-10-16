"""Independent original3716 qualification, all original3714 cases and all Main byte identity."""
import ast
import inspect
import json
import pg3738_hygiene_whole_qualification as previous
from pg3928_current_boundary_full_six import ROOT, W, SOURCE, EXPECTED, NEW_CASES, require


def qualification_inputs(original):
    prior = json.loads((W / 'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes())['result']
    return {'source': SOURCE, 'snapshot': original['snapshot'], 'expected': EXPECTED, 'newCases': NEW_CASES,
            'priorManifestSha256': prior['serverManifestSha256'], 'priorJarHashes': prior['jarHashes'], 'approvedChangedSources': []}


def server_code():
    class Rebind(ast.NodeTransformer):
        def visit_Constant(self, node):
            value = node.value
            if type(value) is int and value in {3712, 3714}:
                return ast.copy_location(ast.Constant({3712: 3714, 3714: 3716}[value]), node)
            if isinstance(value, str):
                value = value.replace('PG3738-hygiene-whole-qualified-v1', 'PG3930-current-boundary-whole-qualified-v1').replace('PG3734', 'PG3928').replace('PG3412', 'PG3734')
                return ast.copy_location(ast.Constant(value), node)
            return node
    tree = ast.fix_missing_locations(Rebind().visit(ast.parse(inspect.getsource(previous.server))))
    raw = ast.unparse(tree)
    # All changed-source allowlists are empty: any physical byte delta fails qualification.
    compile(raw, '<original3716 and all1643 exact Main identity>', 'exec')
    return raw


def qualification_payload(original):
    return '\n'.join(inspect.getsource(x) for x in [require, previous.source_file, previous.classify]) + '\n' + server_code() + '\nserver(' + repr(qualification_inputs(original)) + ')\n'


def main():
    raw = inspect.getsource(previous.main).replace('pg3734-server-six-v1', 'pg3928-server-six-v1').replace('pg3738-hygiene-whole-qualified-v1', 'pg3930-current-boundary-whole-qualified-v1').replace('PG3738-hygiene-whole-qualified-v1', 'PG3930-current-boundary-whole-qualified-v1')
    namespace = {**previous.__dict__, 'qualification_payload': qualification_payload}
    exec(compile(raw, '<read original current3716 only>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
