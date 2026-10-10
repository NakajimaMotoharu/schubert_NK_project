"""New-only full32 helper closure; previous failed sources remain immutable."""
import ast
import builtins
from pg1002_cold_readonly import capture
from pg1023_cold_readback_sources import guest
from pg1031_cold_handoff_preflight_v4 import payload as previous


def missing_globals(raw, roots):
    tree = ast.parse(raw)
    definitions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    global_names = set(definitions) | set(dir(builtins))
    for n in tree.body:
        if isinstance(n, ast.Assign):
            global_names.update(x.id for t in n.targets for x in ast.walk(t) if isinstance(x, ast.Name))
        elif isinstance(n, ast.Import):
            global_names.update(a.asname or a.name.split('.')[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            global_names.update(a.asname or a.name for a in n.names)
    unknown = set()
    pending = list(roots)
    visited = set()
    while pending:
        name = pending.pop()
        if name in visited:
            continue
        visited.add(name)
        if name not in definitions:
            unknown.add(name)
            continue
        function = definitions[name]
        local = {a.arg for a in function.args.args}
        local.update(n.id for n in ast.walk(function) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store))
        for n in ast.walk(function):
            if isinstance(n, ast.Import):
                local.update(a.asname or a.name.split('.')[0] for a in n.names)
            elif isinstance(n, ast.ImportFrom):
                local.update(a.asname or a.name for a in n.names)
            elif isinstance(n, ast.ExceptHandler) and n.name:
                local.add(n.name)
        references = {n.id for n in ast.walk(function) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)} - local
        unknown.update(references - global_names)
        pending.extend(references & set(definitions))
    return sorted(unknown)


def payload():
    raw = previous().replace('pg1031-cold-handoff-preflight-v4', 'pg1032-cold-handoff-preflight-v5')
    raw = raw.replace('PG1031_REFUSED', 'PG1032_REFUSED')
    function = next(n for n in ast.parse(guest()).body if isinstance(n, ast.FunctionDef) and n.name == 'configuration_value')
    raw = ast.unparse(function) + '\n' + raw
    if missing_globals(raw, ['snapshot', 'complete_configuration', 'read', 'actor', 'controls']):
        raise ValueError('observer function closure refused')
    ast.parse(raw)
    return raw


if __name__ == '__main__':
    capture('pg1032-cold-handoff-preflight-v5', payload())
