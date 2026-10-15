"""Independent actual3701/542/1643/static6, never sum related84 with old3699."""
import inspect
import pg2800_jdbc_null_fixed_full_qualified as engine
import pg3260_statement_group_full_qualified as previous
from pg3274_header_group_full_six import SOURCE, validate, rebase


def server():
    raw = rebase(previous.server(), 'PG3258', 'PG3274', 3699, 3701)
    # The exact independent module table changes Protocol only, Batch remains1299.
    import ast
    tree = ast.parse(raw)
    hits = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == 'protocol' and isinstance(value, ast.Tuple) and ast.literal_eval(value) == (82, 17, 174):
                    value.elts[0] = ast.Constant(84); hits += 1
    if hits != 1:
        raise ValueError('exact one module Protocol82 to84 count boundary required')
    tree = ast.fix_missing_locations(tree); compile(tree, '<independent whole3701 module counts>', 'exec')
    return ast.unparse(tree)


def main():
    raw = inspect.getsource(engine.main).replace('pg2800-jdbc-null-fixed-full-qualified-v1', 'pg3276-header-group-full-qualified-v1').replace('pg2798-server-six-v1', 'pg3274-server-six-v1').replace('PG2798', 'PG3274')
    ns = {**engine.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server': server}
    exec(compile(raw, '<independent fixed Header3701 source and XML>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
