"""Independent current851/1666/ABI and unsuppressed PMD, no PT or operational actions."""
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from pg5940_private_lock_compile import TC, BASE, W, OLD, MODULES, SLOT as COMPILE, plan, sha, validate_source, physical_changes
from pg5584_field_accessor_inspection import compile_only_artifacts
from pmd_diagnostic_identity import diagnostic_row

SLOT = 'pg5942-private-lock-static-v1'


def public_signatures(snapshot, keys):
    parts = []
    for module in MODULES:
        names = sorted(k.split(':', 1)[1][:-6].replace('/', '.') for k in keys if k.startswith(module+':'))
        if names:
            parts.append(subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-public', '-s', '-classpath', str(snapshot/('src/schubert-nk-'+module+'/target/classes')), *names], text=True))
    return '\n'.join(parts)


def expected_rules(before, actual):
    expected = Counter(before); expected['AvoidSynchronizedStatement'] -= 93
    if expected != Counter(actual) or expected['AvoidSynchronizedStatement'] < 0:
        raise ValueError('exact93 monitor removal; no lost/unclassified diagnostics or exclusions')


def main():
    cp = W/COMPILE/'manifest.safe.json'; current = json.loads(cp.read_bytes()); snapshot = cp.parent/'source'
    oldp = W/'pg5914-api-expression-static-v1/manifest.safe.json'; old = json.loads(oldp.read_bytes())
    oldpublic = BASE/'PG5914-api-expression-static-v1/manifest.json'
    if sha(oldpublic) != '318d3783a5bfa4fe9a3920b252d3449eca01b9131c925758eadf13f8289548b4' or sha(oldp) != json.loads(oldpublic.read_bytes())['privateManifestSha256'] or old['source'] != OLD or old['actualExit'] != 0:
        raise ValueError('actual original851/1666 raw static proof')
    if current['actualExit'] != 0 or current['testsExecuted'] != 0 or any(current['staticSixModules'].values()):
        raise ValueError('current actual compile-only/no PT/zero six null/type/SpotBugs first')
    sources = validate_source(current['source'], snapshot)
    physical = {m+':'+p.relative_to(snapshot/('src/schubert-nk-'+m+'/target/classes')).as_posix(): sha(p) for m in MODULES for p in (snapshot/('src/schubert-nk-'+m+'/target/classes')).rglob('*.class')}
    if physical != current['allPhysicalMainSha256']:
        raise ValueError('all compiled bytes still identical')
    changed = physical_changes(old['auxClassHashes'], physical)
    previous = W/'pg5912-api-expression-selected35-v1/source'
    if public_signatures(previous, changed) != public_signatures(snapshot, changed):
        raise ValueError('all actual changed public descriptors invariant')
    for name in ('pmd.xml', 'checkstyle.xml'):
        if sha(snapshot/'tools/quality/static'/name) != sha(previous/'tools/quality/static'/name):
            raise ValueError('same unfiltered rules; no exclusion/suppression change')
    os.umask(0o077); out = W/SLOT; out.mkdir(mode=0o700)
    filelist = out/'all-main.txt'; filelist.write_text(''.join(str(snapshot/p)+'\n' for p in sorted(sources)))
    tail = (W/'pg5914-api-expression-static-v1/aux-classpath.txt').read_text().splitlines()[6:]
    release = W/'pg5430-release-v1'; bom = release/'RELEASE-MANIFEST.json'
    if sha(bom) != '85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6':
        raise ValueError('fixed third-party-only dependency BOM')
    approved = {str(release/r['path']): r['sha256'] for r in json.loads(bom.read_bytes())['artifacts'] if '/lib/' in r['path'] and r['path'].endswith('.jar') and not os.path.basename(r['path']).startswith('schubert-nk-')}
    unique = {}
    for name, digest in approved.items():
        unique.setdefault(digest, name)
    provided, _ = compile_only_artifacts(); approved.update({str(p): sha(p) for p in provided})
    if tail != [*unique.values(), *map(str, provided)] or any(sha(Path(p)) != approved[p] for p in tail):
        raise ValueError('actual immutable provided/third-party dependencies only')
    tools = TC/'static-gates-20261015'
    if sha(tools/'record-fix-v1/pmd-record-1298.jar') != '4859fb956de018a843abe55ddb92b0a98921878b80525aaa2a77c5b5d8c2820c' or sha(tools/'checkstyle-14.3.0-all.jar') != '754e218ab1fcabb1e1c5f8530e9d3aa37636806c22987bb279dd907a6ee749b2':
        raise ValueError('pinned static analyzers')
    aux = out/'aux-classpath.txt'; aux.write_text('\n'.join([*(str(snapshot/('src/schubert-nk-'+m+'/target/classes')) for m in MODULES), *tail])+'\n')
    pmd, cs = [c.copy() for c in old['commands']]
    for flag, val in [('--file-list', str(filelist)), ('--aux-classpath', 'file:'+str(aux)), ('--report-file', str(out/'pmd.xml')), ('--rulesets', str(snapshot/'tools/quality/static/pmd.xml'))]:
        pmd[pmd.index(flag)+1] = val
    cs[cs.index('-c')+1] = str(snapshot/'tools/quality/static/checkstyle.xml'); cs[cs.index('-o')+1] = str(out/'checkstyle.xml'); cs[-1] = '@'+str(filelist)
    exits = []
    for name, command in (('pmd', pmd), ('checkstyle', cs)):
        with (out/(name+'.private.log')).open('xb') as f:
            exits.append(subprocess.run(command, stdout=f, stderr=subprocess.STDOUT, timeout=240).returncode)
    tree = ET.parse(out/'pmd.xml').getroot(); rows = []
    for file in tree.findall('{*}file'):
        name = os.path.relpath(file.get('name'), snapshot)
        if name not in sources:
            raise ValueError('current actual Main diagnostics only')
        for warning in file.findall('{*}violation'):
            rows.append(diagnostic_row(name, sources[name], warning, len(rows)+1))
    errors = len(tree.findall('.//{*}error')); cs_count = len(ET.parse(out/'checkstyle.xml').getroot().findall('.//error'))
    expected_rules(old['ruleCounts'], Counter(r['rule'] for r in rows))
    if exits[0] not in (0, 4) or exits[1] != 0 or errors or cs_count or len({r['findingId'] for r in rows}) != len(rows) or validate_source(current['source'], snapshot) != sources:
        raise ValueError('all actual raw reports/process0/Checkstyle0/source fixed')
    value = dict(actualExit=0, source=current['source'], previousMainSource=OLD, changedSourcePaths=sorted(r['path'] for r in plan()['sourcePlans']),
                 physicalMain=1666, inputSourceFiles=851, actualAuxClasses=1666, changedPhysicalClasses=changed, unchangedPhysicalClasses=1666-len(changed),
                 existingPublicAbiUnchanged=True, pmdExit=exits[0], pmdRawFindings=len(rows), ruleCounts=dict(Counter(r['rule'] for r in rows)),
                 pmdProcessingErrors=errors, checkstyleExit=exits[1], checkstyleFindings=cs_count, rawDiagnosticsRemovedByPg=93,
                 compileManifestSha256=sha(cp), pmdXmlSha256=sha(out/'pmd.xml'), checkstyleXmlSha256=sha(out/'checkstyle.xml'),
                 commands=[pmd, cs], allSourceHashes=sources, auxClassHashes=physical, testsExecuted=0, formalAccepted=False, F03Accepted=False, fullCoverageClaimed=False, ptAlternativeCompleted=0, vmActions=0)
    with (out/'manifest.safe.json').open('x') as f:
        json.dump(value, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    public = {k: v for k, v in value.items() if k not in ('commands', 'allSourceHashes', 'auxClassHashes')}; public['privateManifestSha256'] = sha(out/'manifest.safe.json')
    target = BASE/'PG5942-private-lock-static-v1'; target.mkdir()
    for name, body in (('manifest.json', public), ('findings.json', rows)):
        with (target/name).open('x') as f:
            json.dump(body, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=current['source'], sourceFiles=851, physicalMain=1666, changedPhysicalClasses=changed,
                         pmdRawFindings=len(rows), processingErrors=errors, checkstyleFindings=cs_count, manifestSha256=sha(target/'manifest.json'), testsExecuted=0)))


if __name__ == '__main__':
    main()
