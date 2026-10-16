"""Pinned diagnostic on the SSC299 six genuine Jars; F03 remains independent."""
import ast
import inspect
import pg4424_shared_manager_static as old
from pg4694_ssc299_full import SOURCE, ROOT, W


def current_auxiliary(before, qualified):
    result = old.current_auxiliary(before, qualified)
    return {name.replace('/source-full-PG4420/', '/source-full-PG4694/'): digest
            for name, digest in result.items()}


def server_source(data):
    # Embed the actual checked implementation, not a reference to host-only `old`.
    auxiliary = inspect.getsource(old.current_auxiliary).replace('source-full-PG4420', 'source-full-PG4694')
    raw = old.server_source(data)
    before = inspect.getsource(old.current_auxiliary)
    old.require(raw.count(before) == 1, 'single exact six-Jar binding implementation')
    raw = raw.replace(before, auxiliary, 1).replace('source-full-PG4420', 'source-full-PG4694')
    raw = raw.replace('runs/PG3970-current-main-static-v1/manifest.safe.json', 'runs/PG4424-shared-manager-static-v1/manifest.safe.json')
    raw = raw.replace('actualRuleCountDeltaFromOld7bb', 'actualRuleCountDeltaFromOld964e')
    raw = raw.replace('PG4428 original4422 exact payload, all3721 identities,1644 Main and all849 source; SSC295 four logical families/two relocations/one fixed enum; no old native imported.',
                      'PG4696 original PG4694 full XML, all3739 identities,1646 Main and all849 source; SSC299 exact six modified/two internal interfaces; old964e native not imported; BUG1381 format-order gap remains separate.')
    return raw


def main():
    raw = inspect.getsource(old.main)
    replacements = {'pg4428-shared-manager-whole-qualified-v1': 'pg4696-ssc299-whole-qualified-v1',
                    'pg4424': 'pg4700', 'PG4424': 'PG4700', 'shared-manager': 'ssc299',
                    'pg3970-current-main-static-v1': 'pg4424-shared-manager-static-v1',
                    'actualRuleCountDeltaFromOld7bb': 'actualRuleCountDeltaFromOld964e'}
    # Simultaneous substitutions retain the old diagnostic as a comparison, not input ABI.
    for i, key in enumerate(replacements): raw = raw.replace(key, '__STATIC4700_' + str(i) + '__')
    for i, value in enumerate(replacements.values()): raw = raw.replace('__STATIC4700_' + str(i) + '__', value)
    tree = ast.parse(raw)
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and type(n.value) is int and n.value in {3721, 1644}:
            n.value = {3721: 3739, 1644: 1646}[n.value]
    ns = {**vars(old), 'SOURCE': SOURCE, 'ROOT': ROOT, 'W': W, 'server_source': server_source}
    exec(compile(ast.fix_missing_locations(tree), '<SSC299 fixed diagnostic>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__': raise SystemExit(main())
