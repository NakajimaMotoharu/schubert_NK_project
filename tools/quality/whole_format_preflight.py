"""BUG1381: compose a whole runner with an all-project format-only prerequisite.

This changes future generated payloads, not immutable already-running jobs.
"""
import ast
import inspect


def format_preflight(args, source, out, env, inputs):
    import hashlib
    import json
    import os
    import subprocess
    projects = ','.join('src/schubert-nk-' + m for m in
                        ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'])
    split = args.index('-pl')
    if args[split + 1] != projects or args[split + 2:] != [
            'clean', 'spotless:check', 'test-compile', 'jar:test-jar', 'test',
            'spotbugs:check', 'jacoco:report', 'jar:jar']:
        raise ValueError('exact six projects and original whole goals required')
    command = args[:split + 2] + ['spotless:check']
    unchanged = lambda: all(hashlib.sha256((source / p).read_bytes()).hexdigest() == h
                            for p, h in inputs.items())
    if not unchanged():
        raise ValueError('original frozen inputs before format')
    with (out / 'format-preflight.private.log').open('xb') as handle:
        result = subprocess.run(command, cwd=source, env=env,
                                stdout=handle, stderr=subprocess.STDOUT, umask=0o027)
        handle.flush(); os.fsync(handle.fileno())
    same = unchanged()
    with (out / 'format-preflight.safe.json').open('x') as handle:
        json.dump({'command': command, 'actualExit': result.returncode,
                   'sameInputs': same, 'testsIssued': False}, handle, sort_keys=True)
        handle.flush(); os.fsync(handle.fileno())
    if type(result.returncode) is not int or result.returncode != 0 or not same:
        raise ValueError('format preflight failed; no PT command allowed')


def compose(raw):
    tree = ast.parse(raw)
    mains = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main']
    if len(mains) != 1:
        raise ValueError('one fixed whole main')
    main = mains[0]
    sites = [i for i, n in enumerate(main.body) if isinstance(n, ast.With)
             and 'maven.private.log' in ast.unparse(n.items[0].context_expr)]
    if len(sites) != 1 or 'format_preflight' in raw:
        raise ValueError('one not-yet-instrumented whole execution boundary')
    main.body.insert(sites[0], ast.parse('format_preflight(args, SOURCE, OUT, env, inputs)').body[0])
    helper = ast.parse(inspect.getsource(format_preflight)).body[0]
    tree.body.insert(tree.body.index(main), helper)
    return ast.unparse(ast.fix_missing_locations(tree))
