"""Independent new finite runtime delta after the latest qualified retirement image."""
import ast
import inspect
import json
import types
import pg2980_scoped_resume_independent_post as oracle
import pg3040_current_runtime_retirement_post as current
from pg3060_browser_resume_sources import SOURCE, SAVE, TOOLS
from pg1446_current_cold_stage import W
import pg1257_fresh_independent_terminal_post as schema

SLOT = 'pg3066-browser-resume-independent-post-v1'


def existing_parent_metadata(initial, prepared, root, directory, target, lower, upper, literal):
    def require(value):
        if not value:
            raise ValueError('retained parent finite metadata refused')
    require(type(lower) is int and type(upper) is int and 0 < lower <= upper)
    require(set(initial) == {root, directory} and set(prepared) == {root, directory, target})
    require(initial[root] == prepared[root])
    original = initial[directory]['metadata']
    parent = prepared[directory]['metadata']
    file = prepared[target]['metadata']
    root_meta = initial[root]['metadata']
    for row in [original, parent, file, root_meta]:
        require(type(row) is list and len(row) == 9 and all(type(x) is int for x in row))
    require(root_meta[2:6] == [0, 0, 0o40755, 3])
    require(original[0] == root_meta[0] and original[1] > 0 and original[1] != root_meta[1])
    require(original[2:6] == [0, 0, 0o40755, 2] and original[6] >= 0)
    require(parent[:6] == original[:6] and parent[6] >= original[6])
    require(all(max(original[i], lower) <= parent[i] <= upper for i in [7, 8]))
    require(file[0] == root_meta[0] and file[1] > 0 and file[1] not in {root_meta[1], parent[1]})
    require(file[2:7] == [0, 0, 0o100644, 1, len(literal)])
    require(all(lower <= file[i] <= upper for i in [7, 8]))


def independent_block(seals):
    raw = oracle.payload(seals)
    node = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == 'independent_resume_delta')
    raw = ast.get_source_segment(raw, node)
    for old, new in [('pg2970-current-cold-resume-tools-v1', TOOLS), ('pg2974-current-cold-resume-preparation-v1', SAVE), ('pg2970', 'pg3060'), ('zz-pg2970', 'zz-pg3060')]:
        raw = raw.replace(old, new)
    start = raw.index('    require(0<lower<=upper and set(initial[\'runtime\'])=={root}')
    end = raw.index("    require(prepared[root]['sha256']", start)
    raw = raw[:start] + "    existing_parent_metadata(initial['runtime'],prepared,root,directory,target,lower,upper,literal)\n    require(not (fresh/'runtime-parent-created.private.json').exists())\n" + raw[end:]
    return inspect.getsource(existing_parent_metadata) + '\n' + raw + '\nafter,fresh_private,exec_record=independent_resume_delta(after)\n'


def payload(seals):
    raw = current.payload(seals).replace(current.SLOT, SLOT).replace('PG3040-current-runtime-retirement-post-v1', 'PG3066-browser-resume-independent-post-v1')
    marker = '\nbus = dbus.SystemBus(private=True)\n'
    if raw.count(marker) != 1:
        raise ValueError('one final retirement-checked new resume projection boundary required')
    raw = raw.replace(marker, '\n' + independent_block(seals) + marker)
    marker = "'rawExported': False"
    if raw.count(marker) != 1:
        raise ValueError('one bounded independent result publication required')
    raw = raw.replace(marker, marker + ",'normalResumePrepared':True,'independentResumeOnlyDeltaVerified':True,'coarseClockMeasured':True,'retainedOriginalParent':True,'preparedAfterSha256':hashlib.sha256(fresh_private('after.private.json')).hexdigest(),'nativeCanonicalSha256':hashlib.sha256(json.dumps(native,sort_keys=True).encode()).hexdigest()")
    compile(raw, '<latest all original and retained-parent runtime post>', 'exec')
    return raw


def main():
    actual = json.loads((W / 'pg3064-prepare-resume-v1.safe.json').read_bytes())
    if not (actual['actualExit'] == 0 and actual['sourceQualified'] and actual['freshResumeRuntimePrepared'] and actual['normalSingleRuntimeReload']):
        raise ValueError('actual new finite preparation with normal return required')
    fn = current.namespace()['main']
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT': SLOT, 'payload': payload, 'SOURCE': SOURCE}, 'latest_resume_full_post')()


if __name__ == '__main__':
    raise SystemExit(main())
