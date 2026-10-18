"""Independent actual3814/556/all1654 qualification; no full replay or VM operations."""
import ast
import hashlib
import inspect
import json
import os
import re
import subprocess
from lan_server import copy, run
import pg4970_ssc304_whole_qualification as previous
import pg5120_root_elf_selected as selection
import pg5122_root_elf_public as cases
from pg5128_root_full import SOURCE, ROOT, W

SLOT = 'pg5130-root-whole-qualified-v1'
MODIFIED = {'batch:' + name + '.class' for name in (selection.CLASS, selection.PENDING)}
ADDITIONS = {'batch:' + selection.CLASS + '$DigestFactory.class'} | {
    'batch:' + selection.PENDING + suffix + '.class' for suffix in ('$WaitIo', '$LaunchRead', '$1')}


def added_cases():
    values = []
    for name, required in (('RootElfDigestPortTest', cases.NAMES), ('RootPendingWaitTest', cases.PENDING_NAMES),
                           ('RootEntryRejectionTest', cases.GUARD_NAMES)):
        path = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/' + name + '.java'
        text = subprocess.check_output(['git', 'show', SOURCE + ':' + path], cwd=ROOT, text=True)
        names = re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(', text)
        if len(names) != text.count('@Test') or len(names) != len(set(names)) or set(names) != set(required):
            raise ValueError('exact independently specified new case identities')
        values.extend(('dev.codex.schubert.nk.batch.file.' + name, method) for method in names)
    if len(values) != 23: raise ValueError('exact new23 only')
    return values


def physical_difference(old, new, candidate):
    import re
    if any(type(image) is not dict or any(type(k) is not str or type(v) is not str or re.fullmatch('[a-f0-9]{64}', v) is None
                                         for k, v in image.items()) for image in (old, new, candidate)):
        raise ValueError('strict actual SHA256 inventories')
    if len(old) != 1650 or len(new) != 1654 or set(new) != set(old) | ADDITIONS or new != candidate:
        raise ValueError('exact all1654 current Main and four declared additions')
    changed = {k for k in old if old[k] != new[k]}
    if changed != MODIFIED: raise ValueError('exact two Root outer Main changed; unrelated debug drift rejected')
    rows = [{'oldClass': k, 'class': k, 'oldSha256': old[k], 'newSha256': new[k], 'action': 'MODIFIED'} for k in sorted(changed)]
    rows.extend({'oldClass': None, 'class': k, 'oldSha256': None, 'newSha256': new[k],
                 'action': 'ADDED_NATIVE_BINDING' if k.endswith('$1.class') else 'ADDED_INTERNAL_INTERFACE'} for k in sorted(ADDITIONS))
    return rows, len(old) - len(changed)


def qualifier_source():
    raw = previous.qualifier_source()
    for old, new in (("out = base / 'runs/PG4968-six-v1'", "out = base / 'runs/PG5128-six-v1'"),
                     ("source = base / 'source-full-PG4968'", "source = base / 'source-full-PG5128'"),
                     ("old = base / 'runs/PG4844-six-v1'", "old = base / 'runs/PG4968-six-v1'"),
                     ('transfer/PG4968-source.tar', 'transfer/PG5128-source.tar')):
        if raw.count(old) != 1: raise ValueError('one current/prior namespace ' + old)
        raw = raw.replace(old, new, 1)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self, node):
            if type(node.value) is int and node.value in {3761, 3791, 553, 1650, 30}:
                return ast.copy_location(ast.Constant({3761:3791, 3791:3814, 553:556, 1650:1654, 30:23}[node.value]), node)
            return node
    raw = ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    return raw.replace('actual qualified old3721 baseline manifest', 'actual qualified a2ecc3791 baseline manifest').replace(
        'all849 Main source bytes', 'all Main source bytes').replace('all3721 original identities retained plus eighteen independently specified methods',
                                                                  'all3791 original identities retained plus exact23 independently specified methods')


def candidate_main():
    selected = W / 'pg5126-root-guards-green-v1'
    result = json.loads((selected / 'manifest.safe.json').read_bytes())
    if not (type(result['actualExit']) is int and result['actualExit'] == 0 and result['phaseExits'] == [0, 0]
            and result['sourceSnapshot'] == SOURCE and result['tests'] == 50 and result['suites'] == 8):
        raise ValueError('actual frozen selected50/8 first')
    if selection.main_delta(selected / 'source', 'pending') != result['mainDelta']:
        raise ValueError('actual selected physical bytes')
    prior = json.loads(selection.FULL.read_bytes())['result']
    old = prior['allPhysicalMainSha256']
    # Unbuilt prior bytes are independent expected values only, never claimed new success.
    candidate = {k:v for k,v in old.items() if k.split(':', 1)[0] not in selection.BUILT}
    for module in selection.BUILT:
        classes = selected / 'source' / ('src/schubert-nk-' + module + '/target/classes')
        candidate.update({module + ':' + p.relative_to(classes).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in classes.rglob('*.class')})
    physical_difference(old, candidate, candidate)
    return prior, candidate


def main():
    original = json.loads((W / 'pg5128-root-six-v1/manifest.safe.json').read_bytes())
    if type(original['actualExit']) is not int or original['actualExit'] != 0 or original['source'] != SOURCE:
        raise ValueError('actual original full0 required; never rerun for collection')
    if subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=ROOT):
        raise ValueError('all source/Test/settings unchanged')
    prior, candidate = candidate_main()
    before = json.loads((W / 'pg5128-root-six-v1/begin.safe.json').read_bytes())
    data = {'source': SOURCE, 'priorManifestSha256': prior['serverManifestSha256'], 'priorJarHashes': prior['jarHashes'],
            'archiveSha256': before['archiveSha256'], 'aliases': {}, 'newCases': added_cases(), 'candidateMain': candidate,
            'allMainSourceSha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in ROOT.glob('src/*/src/main/java/**/*.java')}}
    raw = ('import json\nMODIFIED=set(' + repr(sorted(MODIFIED)) + ')\nADDITIONS=set(' + repr(sorted(ADDITIONS)) + ')\n'
           + inspect.getsource(physical_difference) + '\n' + qualifier_source() + '\nprint(json.dumps(qualify(' + repr(data) + ')))\n')
    from pyflakes.api import check
    if check(raw, '<complete independent Root whole qualifier>'): raise ValueError('complete namespace static0')
    os.umask(0o077); out = W / SLOT; out.mkdir(mode=0o700)
    path = out / 'qualify.private.py'; path.write_text(raw); digest = hashlib.sha256(raw.encode()).hexdigest()
    remote = '/home/mini/schubert-nk-pgpt/transfer/PG5130-whole-qualified-v1'
    code, _ = run('mkdir -m700 ' + remote, timeout=30)
    if code: raise ValueError('new-only qualification namespace; recover original')
    code, _ = copy(path, remote + '/', timeout=60)
    if code: raise ValueError('fixed independent qualifier transfer')
    code, output = run('sha256sum ' + remote + '/qualify.private.py', timeout=30)
    if code or output.split()[0] != digest: raise ValueError('actual fixed payload bytes')
    code, output = run('python3 -B ' + remote + '/qualify.private.py', timeout=180)
    (out / 'observer.private.log').write_text(output)
    value = {'actualExit':code, 'source':SOURCE, 'payloadSha256':digest, 'formalAccepted':False, 'wholeReplayed':False}
    if code == 0: value['result'] = json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps({k:v for k,v in value.items() if k != 'result'}))
    if code == 0: print(json.dumps({k:value['result'][k] for k in ('tests', 'suites', 'mainClasses', 'staticSixModules', 'unchangedPhysicalClasses', 'global100', 'F03Accepted')}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
