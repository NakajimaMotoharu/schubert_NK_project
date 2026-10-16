"""All eighteen new emitted roles and fixed current originals; host-only ABI, no guest action."""
import inspect
import types
import pg3758_hygiene_unused_compile as previous
import pg3982_literal_invariant_unused_sources as role

TARGET = role.W / role.TOOLS
ARCHIVE = previous.previous.old.previous.graph.engine.P / role.ARCHIVE


def compiler():
    raw = role.role_text(previous.previous.compiler())
    for old, new in [('pg3152-frozen-v1', 'pg3878-frozen-v1'), ('pg3150-browser-business-owned-stop-tools-v1', 'pg3876-current-resume-owned-tools-v1'), ('Pg3150', 'Pg3876')]: raw = raw.replace(old, new)
    marker = "current = json.loads((W / 'pg3980-current-7fff-before-view-v1/manifest.safe.json').read_bytes())"
    if raw.count(marker) != 1: raise ValueError('one current canonical-data-only view role required')
    raw = raw.replace(marker, "current = json.loads((W / " + repr(str(role.VIEW_LOCAL.relative_to(role.W))) + ").read_bytes())['result']")
    compile(raw, '<whole new unused host ABI>', 'exec')
    return raw


def validate_actual_graph(target, hashes):
    graph = previous.previous.old.previous.graph
    raw = inspect.getsource(graph.validate_actual_graph).replace('pg2132', 'pg3982').replace('pg2126-manifest-v1.sig', 'pg3976-manifest-v1.sig')
    values = {**graph.__dict__, 'ARCHIVE': ARCHIVE}
    exec(compile(raw, '<exact new graph bundle and new signature>', 'exec'), values)
    return values['validate_actual_graph'](target, hashes)


def main():
    role.qualify(); graph = previous.previous.old.previous.graph
    values = {**graph.engine.__dict__, '__file__': __file__, 'TARGET': TARGET, 'ARCHIVE': ARCHIVE, 'TOOLS': role.TOOLS, 'CURRENT': role.CURRENT,
              'PRODUCTION': role.SOURCE, 'BEFORE': role.BEFORE, 'sources': role.sources, 'validate_actual_graph': validate_actual_graph, 'inventory': graph.inventory}
    values['write'] = types.FunctionType(graph.write.__code__, {**graph.__dict__, 'TARGET': TARGET})
    exec(compile(compiler(), '<new host-only all ABI compiler>', 'exec'), values)
    return values['main']()


if __name__ == '__main__': raise SystemExit(main())
