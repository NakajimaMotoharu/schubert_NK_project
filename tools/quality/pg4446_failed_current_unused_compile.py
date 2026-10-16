"""Host-only closed18 current-data tool compile against exact deployed7bb Jars."""
import hashlib
import inspect
import types
import pg3984_literal_invariant_unused_compile as previous
import pg4444_failed_current_unused_sources as role
from bundle_hash_contract import require_bound

TARGET = role.W / role.TOOLS
ARCHIVE = previous.previous.previous.old.previous.graph.engine.P / role.ARCHIVE


def compiler():
    raw = role.role_text(previous.compiler())
    raw = role.once(raw, "current = json.loads((W / 'pg3980-current-before-view-v1/manifest.safe.json').read_bytes())['result']",
                    "current = json.loads((W / 'pg4442-failed-current-view-qualified-v1/manifest.safe.json').read_bytes())['result']")
    raw = role.once(raw, "current['productionSource'] != CURRENT or current['privateBeforeSha256'] != BEFORE",
                    "current['source'] != CURRENT or current['canonicalBefore10Sha256'] != BEFORE or current['dataViewAccepted'] is not True or current['oldParentNormal'] is not False")
    raw = role.once(raw, "prior['productionSource'] != CURRENT", "prior['productionSource'] != '7fffab57a567914956b66452e5e54388642efdec'")
    raw = raw.replace('qualified same current shared ABI required', 'pinned historical generic shared tools required; current7bb Jars are separately compiled')
    raw = raw.replace('actual full current genuine-DONE before required', 'fresh fully qualified failed-parent data before required')
    # The reusable generic tool classes keep their original qualified bytes and
    # attribution. Only the closed18 current data tools are recompiled against
    # actual deployed7bb release Jars; no old Main/native qualification is moved.
    raw = raw.replace("'genuineParentBeforeSha256': BEFORE", "'failedCurrentDataBeforeSha256': BEFORE, 'historicalGenericToolSource': '7fffab57a567914956b66452e5e54388642efdec', 'currentCompileJarSource': CURRENT, 'oldParentNormal': False")
    compile(raw, '<closed18 failed-current host ABI compile>', 'exec')
    return raw


def validate_actual_graph(target, hashes):
    expected = hashlib.sha256((target / 'bundle.safe.json').read_bytes()).hexdigest()
    for name in ['pg4444_native_refs.py', 'pg4444_input_preflight.py']:
        require_bound((target / name).read_text(), expected)
    graph = previous.previous.previous.old.previous.graph
    raw = inspect.getsource(graph.validate_actual_graph).replace('pg2132', 'pg4444').replace('pg2126-manifest-v1.sig', 'pg4432-manifest-v1.sig')
    namespace = {**graph.__dict__, 'ARCHIVE': ARCHIVE}
    exec(compile(raw, '<closed graph new4432 signature>', 'exec'), namespace)
    return namespace['validate_actual_graph'](target, hashes)


def main():
    role.qualify(); graph = previous.previous.previous.old.previous.graph
    namespace = {**graph.engine.__dict__, '__file__': __file__, 'TARGET': TARGET, 'ARCHIVE': ARCHIVE,
        'TOOLS': role.TOOLS, 'CURRENT': role.CURRENT, 'PRODUCTION': role.SOURCE, 'BEFORE': role.BEFORE,
        'sources': role.sources, 'validate_actual_graph': validate_actual_graph, 'inventory': graph.inventory}
    namespace['write'] = types.FunctionType(graph.write.__code__, {**graph.__dict__, 'TARGET': TARGET})
    exec(compile(compiler(), '<host-only failed-current compile>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
