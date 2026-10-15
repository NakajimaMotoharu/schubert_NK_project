"""Independent actual3702, Protocol85, six modules; no arithmetic PT addition."""
import ast
import inspect

import pg2800_jdbc_null_fixed_full_qualified as engine
import pg3276_header_group_full_qualified as previous
from pg3302_directional_group_full_six import SOURCE, validate
from pg3274_header_group_full_six import rebase


def server():
    tree = ast.parse(rebase(previous.server(), 'PG3274', 'PG3302', 3701, 3702))
    hits = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == 'protocol' and isinstance(value, ast.Tuple) and ast.literal_eval(value) == (84, 17, 174):
                    value.elts[0] = ast.Constant(85); hits += 1
    if hits != 1:
        raise ValueError('one exact independent Protocol85 module count required')
    tree = ast.fix_missing_locations(tree); compile(tree, '<independent whole3702>', 'exec')
    return ast.unparse(tree)


def main():
    raw = inspect.getsource(engine.main).replace('pg2800-jdbc-null-fixed-full-qualified-v1', 'pg3304-directional-group-full-qualified-v1').replace('pg2798-server-six-v1', 'pg3302-server-six-v1').replace('PG2798', 'PG3302')
    namespace = {**engine.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server': server}
    exec(compile(raw, '<independent whole3702 transport>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
