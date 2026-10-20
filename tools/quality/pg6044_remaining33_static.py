"""Analyze actual PG6040 generated jars and canonical Main; no build/PT/runtime replay."""
import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path
from pg5940_private_lock_compile import ROOT, W, BASE, TC, sha
from pg6040_remaining33_whole import SOURCE, OLD, plan
from pg5584_field_accessor_inspection import compile_only_artifacts
from pg6008_api_bounds_static import executable_sections
from pg5910_storage_static_rebind import ordered_pairs
from pmd_diagnostic_identity import diagnostic_row

MODULES = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')


def physical_changes(before, after, owners):
    changes = {k for k in before.keys() & after.keys() if before[k] != after[k]}
    if len(before) != 1667 or set(before) != set(after) or not owners <= changes:
        raise ValueError('all1667/every22 owner changed/no added or removed Main')
    if any(not any(k == o or k.startswith(o[:-6]+'$') for o in owners) for k in changes):
        raise ValueError('only declared owner/nested physical differences')
    return sorted(changes)


def expected_rules(before, after):
    expected = Counter(before); expected['AvoidLiteralsInIfCondition'] -= 33
    if expected != Counter(after) or expected['AvoidLiteralsInIfCondition'] != 0:
        raise ValueError('all33 literal diagnostics only;other raw rules remain unfiltered')


def disassembly_proof(before, jars, changed):
    proof = []
    for module in MODULES:
        names = [k.split(':', 1)[1][:-6].replace('/', '.') for k in changed if k.startswith(module+':')]
        if not names:
            continue
        command = [str(TC/'jdk-25.0.4/bin/javap')]
        oldcp = str(before/('src/schubert-nk-'+module+'/target/classes')); newcp = str(jars/('schubert-nk-'+module+'.jar'))
        def read(flags, cp):
            return subprocess.check_output(command+flags+['-classpath', cp, *names], text=True)
        oldabi, newabi = read(['-public', '-s'], oldcp), read(['-public', '-s'], newcp)
        if oldabi != newabi:
            raise ValueError('each changed existing public descriptor remains identical')
        oldcode = executable_sections(read(['-c', '-p', '-s'], oldcp))
        newcode = executable_sections(read(['-c', '-p', '-s'], newcp))
        if oldcode != newcode:
            raise ValueError('each changed owner/nested method descriptor and symbolic instruction must remain equivalent')
        proof.append(dict(module=module, classes=names, allMethodDescriptorsAndSymbolicInstructionsEqual=True,
                          existingPublicAbiUnchanged=True, normalizedDisassemblySha256=hashlib.sha256(newcode.encode()).hexdigest(),
                          publicAbiSha256=hashlib.sha256(newabi.encode()).hexdigest()))
    return proof


def main():
    oldsp = BASE/'PG6034-corrected-boundary-static-v1/manifest.json'; oldpp = W/'pg6034-corrected-boundary-static-v1/manifest.safe.json'
    if sha(oldsp) != '4be1ee7550f3cf719b5da6a362ad418c444eadd2deea7b7368c50807a20b3ad8' or sha(oldpp) != json.loads(oldsp.read_bytes())['privateManifestSha256']:
        raise ValueError('actual prior32f all8511667/static1329 immutable')
    old = json.loads(oldpp.read_bytes()); qp = BASE/'PG6040-current3976-cases/qualification.json'
    receipt = json.loads((W/'pg6042-original3976-artifacts-v1/manifest.safe.json').read_bytes())
    if receipt['actualExit'] != 0 or receipt['source'] != SOURCE or receipt['publicQualificationSha256'] != sha(qp):
        raise ValueError('genuine original3976 artifact reader receipt required')
    q = json.loads(qp.read_bytes()); jars = W/'pg6042-original3976-artifacts-v1/jars'; declaration = plan()
    if not (q['actualExit'] == q['FESFlakyNotRun'] == q['staticSixModules'] == 0 and q['productionSource'] == SOURCE
            and (q['tests'], q['suites'], q['mainClasses']) == (3976, 593, 1667) and q['allSixFormatBeforeAnyPt']):
        raise ValueError('same-source true3976/593/1667/null/static/format first')
    expected = dict(old['allSourceHashes'])
    owners = set()
    for row in declaration['sourcePlans']:
        if expected[row['path']] != row['beforeSha256']:
            raise ValueError('original22 exact source identity')
        expected[row['path']] = row['predictedAfterSha256']
        owners.add(row['path'].split('/')[1].removeprefix('schubert-nk-')+':'+row['path'].split('/src/main/java/')[1][:-5]+'.class')
    current = {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if current != expected or current != q['allSourceHashes'] or len(current) != 851 or old['source'] != OLD or len(owners) != 22:
        raise ValueError('all851 fixed actual Main,22 predicted edits only')
    physical = {}
    for module in MODULES:
        jarpath = jars/('schubert-nk-'+module+'.jar')
        if sha(jarpath) != q['modules'][module]['jarSha256']:
            raise ValueError('only original actual Jar bytes,not a rebuilt candidate')
        with zipfile.ZipFile(jarpath) as jar:
            names = [n for n in jar.namelist() if n.endswith('.class')]
            if len(names) != len(set(names)):
                raise ValueError('unique actual Jar class members')
            physical.update({module+':'+n: hashlib.sha256(jar.read(n)).hexdigest() for n in names})
    if physical != q['allPhysicalMainSha256']:
        raise ValueError('all1667 actual original Main class bytes')
    changed = physical_changes(old['auxClassHashes'], physical, owners)
    methods = disassembly_proof(W/'pg6032-error-boundary-selected965-v1/source', jars, changed)
    before_root = W/'pg6032-error-boundary-selected965-v1/source'
    for filename in ('pmd.xml', 'checkstyle.xml'):
        if sha(ROOT/'tools/quality/static'/filename) != sha(before_root/'tools/quality/static'/filename):
            raise ValueError('unfiltered original rule files unchanged')
    os.umask(0o077); out = W/'pg6044-remaining33-static-v1'; out.mkdir(mode=0o700)
    files = out/'all-main.txt'; files.write_text(''.join(str(ROOT/p)+'\n' for p in sorted(current)))
    tail = (W/'pg6034-corrected-boundary-static-v1/aux-classpath.txt').read_text().splitlines()[6:]
    release = W/'pg5430-release-v1'; bom = release/'RELEASE-MANIFEST.json'
    if sha(bom) != '85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6':
        raise ValueError('fixed third-party-only runtime dependencies')
    approved = {str(release/r['path']): r['sha256'] for r in json.loads(bom.read_bytes())['artifacts'] if '/lib/' in r['path'] and r['path'].endswith('.jar') and not os.path.basename(r['path']).startswith('schubert-nk-')}
    unique = {}
    for name, digest in approved.items():
        unique.setdefault(digest, name)
    provided, _ = compile_only_artifacts(); approved.update({str(p): sha(p) for p in provided})
    if tail != [*unique.values(), *map(str, provided)] or any(sha(Path(p)) != approved[p] for p in tail):
        raise ValueError('actual unchanged provided/third-party bytes only')
    tools = TC/'static-gates-20261015'
    if sha(tools/'record-fix-v1/pmd-record-1298.jar') != '4859fb956de018a843abe55ddb92b0a98921878b80525aaa2a77c5b5d8c2820c' or sha(tools/'checkstyle-14.3.0-all.jar') != '754e218ab1fcabb1e1c5f8530e9d3aa37636806c22987bb279dd907a6ee749b2':
        raise ValueError('pinned exact analyzers')
    aux = out/'aux-classpath.txt'; aux.write_text('\n'.join([*(str(jars/('schubert-nk-'+m+'.jar')) for m in MODULES), *tail])+'\n')
    pmd, cs = [c.copy() for c in old['commands']]
    for flag, value in (('--file-list', str(files)), ('--aux-classpath', 'file:'+str(aux)), ('--report-file', str(out/'pmd.xml')), ('--rulesets', str(ROOT/'tools/quality/static/pmd.xml'))):
        pmd[pmd.index(flag)+1] = value
    cs[cs.index('-c')+1] = str(ROOT/'tools/quality/static/checkstyle.xml'); cs[cs.index('-o')+1] = str(out/'checkstyle.xml'); cs[-1] = '@'+str(files)
    exits = []
    for name, command in (('pmd', pmd), ('checkstyle', cs)):
        with (out/(name+'.private.log')).open('xb') as f:
            exits.append(subprocess.run(command, stdout=f, stderr=subprocess.STDOUT, timeout=240).returncode)
    tree = ET.parse(out/'pmd.xml').getroot(); rows = []
    for file in tree.findall('{*}file'):
        name = os.path.relpath(file.get('name'), ROOT)
        if name not in current:
            raise ValueError('current Main-only actual diagnostics')
        for warning in file.findall('{*}violation'):
            rows.append(diagnostic_row(name, current[name], warning, len(rows)+1))
    errors = len(tree.findall('.//{*}error')); cs_count = len(ET.parse(out/'checkstyle.xml').getroot().findall('.//error'))
    expected_rules(old['ruleCounts'], Counter(r['rule'] for r in rows))
    oldraw = json.loads(oldsp.with_name('findings.json').read_bytes()); pairs = ordered_pairs(oldraw, rows)
    paths = {r['path'] for r in declaration['sourcePlans']}
    if any(r['sourcePath'] not in paths and r['findingId'] not in pairs for r in rows) or Counter(r['sourcePath'] for r in oldraw if r['sourcePath'] not in paths) != Counter(r['sourcePath'] for r in rows if r['sourcePath'] not in paths):
        raise ValueError('all unaffected source-local diagnostic sequences remain exact')
    if exits[0] not in (0, 4) or exits[1] != 0 or errors or cs_count or current != {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}:
        raise ValueError('actual raw reports/process0/Checkstyle0/frozen source')
    value = dict(actualExit=0, source=SOURCE, previousMainSource=OLD, inputSourceFiles=851, physicalMain=1667,
        changedSourcePaths=sorted(paths), allSourceHashes=current, auxClassHashes=physical, changedPhysicalClasses=changed,
        unchangedPhysicalClasses=1667-len(changed), allChangedMethodProof=methods, existingPublicAbiUnchanged=True,
        currentWholeQualificationSha256=sha(qp), originalGeneratedJarsUsed=True, additionalBuildsIssued=0, testsExecuted=0,
        pmdExit=exits[0], pmdRawFindings=len(rows), ruleCounts=dict(Counter(r['rule'] for r in rows)), pmdProcessingErrors=errors,
        checkstyleExit=exits[1], checkstyleFindings=cs_count, rawDiagnosticsRemovedByPg=33, commands=[pmd, cs],
        pmdXmlSha256=sha(out/'pmd.xml'), checkstyleXmlSha256=sha(out/'checkstyle.xml'), formalAccepted=False, F03Accepted=False,
        fullCoverageClaimed=False, ptAlternativeCompleted=0, vmActions=0)
    with (out/'manifest.safe.json').open('x') as f:
        json.dump(value, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    public = {k: v for k, v in value.items() if k not in ('commands', 'allSourceHashes', 'auxClassHashes')}
    public['privateManifestSha256'] = sha(out/'manifest.safe.json'); target = BASE/'PG6044-remaining33-static-v1'; target.mkdir()
    for filename, body in (('manifest.json', public), ('findings.json', rows)):
        with (target/filename).open('x') as f:
            json.dump(body, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=SOURCE, sourceFiles=851, physicalMain=1667, changedPhysical=len(changed), raw=len(rows), literalRemainder=0,
        allChangedMethodProofs=len(methods), additionalBuildsIssued=0, manifestSha256=sha(target/'manifest.json'))))


if __name__ == '__main__':
    main()
