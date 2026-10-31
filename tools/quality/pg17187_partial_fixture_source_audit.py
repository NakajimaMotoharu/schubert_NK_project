"""Finite AST/current-proof audit of copied negative fixture keys, no original tool rerun."""
import ast
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE / 'PG17187-partial-fixture-source-audit-v1'
NUMBERS = (17030, 17046, 17062, 17079, 17128, 17144, 17188, 17189)


def literal(node, environment):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return environment.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = literal(node.left, environment), literal(node.right, environment)
        if isinstance(a, str) and isinstance(b, str):
            return a + b
    return None


def valid_target(units, fresh, name, value):
    return name in fresh and name in units and type(value) is bool and units[name]['four100'] is not value


def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    rows = []
    for number in NUMBERS:
        paths = list((data.ROOT / 'tools/quality').glob(f'pg{number}_*.py'))
        assert len(paths) == 1
        path = paths[0]; tree = ast.parse(path.read_text())
        assignments = [n for n in ast.walk(tree) if isinstance(n, ast.Assign)]
        env = {}
        for node in assignments:
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                value = literal(node.value, env)
                if isinstance(value, str):
                    env[node.targets[0].id] = value
        writer = [n.module for n in tree.body if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith('pg')]
        assert len(writer) == 1
        writer_path = data.ROOT / 'tools/quality' / (writer[0] + '.py')
        writer_tree = ast.parse(writer_path.read_text())
        out_nodes = [n.value.right.value for n in writer_tree.body if isinstance(n, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == 'OUT' for t in n.targets)
                     and isinstance(n.value, ast.BinOp) and isinstance(n.value.right, ast.Constant)]
        assert len(out_nodes) == 1 and 'registry-v1' in out_nodes[0]
        m = data.read_checked(data.BASE / out_nodes[0] / 'manifest.json', env['PIN'])
        assert m['actualExit'] == 0 and m['source'] == '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
        fresh = set(m['additionalScopeReferences'][-1]['newSourceNames'])
        fixtures = []
        for node in assignments:
            if len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Subscript) or literal(target.slice, env) != 'four100':
                continue
            holder = target.value
            if not isinstance(holder, ast.Subscript) or not isinstance(holder.value, ast.Subscript) or literal(holder.value.slice, env) != 'fullSourceUnits':
                continue
            if not isinstance(holder.value.value, ast.Name) or holder.value.value.id != 'bad':
                continue
            value = literal(node.value, env)
            if isinstance(holder.slice, ast.Name) and holder.slice.id == 'name':
                assert number == 17189 and value is True
                assert 'for name in sorted(expected_new):' in path.read_text() and 'nondegenerate partial promotion' in path.read_text()
                names = sorted(fresh)
            else:
                name = literal(holder.slice, env)
                assert isinstance(name, str)
                names = [name]
            fixtures.extend(dict(name=name, mutationValue=value, valid=valid_target(m['fullSourceUnits'], fresh, name, value)) for name in names)
        assert fixtures
        if number == 17188:
            assert len(fixtures) == 1 and fixtures[0]['valid'] is False and fixtures[0]['name'] not in m['fullSourceUnits']
        else:
            assert all(v['valid'] for v in fixtures)
        if number == 17189:
            assert len(fixtures) == len(fresh) == 2
        rows.append(dict(tool=str(path.relative_to(data.ROOT)), toolSha256=data.sha(path.read_bytes()),
                         registry=out_nodes[0], registrySha256=env['PIN'], currentNewSources=sorted(fresh),
                         fixtures=fixtures, disposition='FAILED_OLD_FIXTURE_PRESERVED' if number == 17188 else 'ALL_DECLARED_FIXTURES_CURRENT_NONDEGENERATE'))
    units = {'A': {'four100': False}, 'B': {'four100': True}}
    assert valid_target(units, {'A'}, 'A', True)
    assert valid_target(units, {'B'}, 'B', False)
    negatives = [valid_target(units, {'A'}, 'missing', True), valid_target(units, {'B'}, 'A', True),
                 valid_target(units, {'A'}, 'A', False), valid_target(units, {'A'}, 'A', 1),
                 valid_target(units, set(), 'A', True), valid_target(units, {'B'}, 'B', True)]
    assert negatives == [False] * 6
    verify(invocation); OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation,
        source='6b53efeec87f3ec36a840dd8e7759656cb4aee5c', finiteFamilies=rows,
        exactOldFailureCount=1, correctedCurrentSourceFixtures=2, metadataBoundaryVectors=8,
        productTestsExecuted=0, oldToolsReexecuted=0, sourceChanged=False, rulesChanged=False,
        newAccepted=0, formalUpdated=False, wholeF03Accepted=False, whole451Accepted=False, effortPercent=None, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
