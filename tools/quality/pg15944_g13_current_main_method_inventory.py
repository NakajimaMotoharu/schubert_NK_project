"""Current compiled Main metadata denominator; no Product class loading or execution."""
import collections
import json
from pathlib import Path
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9346_direct_companion_jdk_post as steps

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
NORMAL = ('PG14216-typed-marker-guard-six-compile-v1', '1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
OUT = data.BASE / 'PG15944-g13-current-main-method-inventory-v1'
SLOT = data.ROOT.parent / 'pgpt-runs/PG379/pg15944-g13-current-main-method-inventory-v1'
HELD = frozenset(('api:dev/codex/schubert/nk/api/error/TemporaryInfrastructureException.class', 'web:dev/codex/schubert/nk/web/bootstrap/WebStartupException.class'))
HELPER = data.ROOT / 'tools/quality/architecture/MainClassCodeStructureAuditV2.java'
HELPER_SHA = 'be11fa6ca294374de33386fe19a169fcdbd708d13c92cb42272c74b99daaf656'
CLASSES = data.ROOT.parent / 'pgpt-runs/PG379/pg9848-main-code-structure-v2/reader'
CLASS_SHA = 'af4389d3230c8f58265d97b1f8522e14bbe863c33ee18a028dd0b1b2cbf989ee'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def main():
    invocation = capture(__file__)
    require(not OUT.exists() and not SLOT.exists(), 'new-only')
    n = data.read_checked(data.BASE / NORMAL[0] / 'manifest.json', NORMAL[1])
    require(n['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == 0, 'fixed normal, no Product PT')
    descriptor = data.read_checked(data.BASE / 'PG15918-g13-current-static-descriptor-v1/manifest.json', 'b238136eb4d965b59ea281c3e610d889b18a0c102839ea9e658b2235fea6a05c')
    artifacts = data.read_checked(data.BASE / 'PG15918-g13-current-static-descriptor-v1/artifacts.json', descriptor['artifactsSha256'])
    sources = {r['path']: r for r in artifacts if r['path'].startswith('src/') and r['kind'] == 'JAVA'}
    require(len(sources) == 965 and all(n['begin']['inputHashes'][p] == r['sha256'] == data.sha((data.ROOT / p).read_bytes()) for p, r in sources.items()), 'all current965 source bytes')
    require(data.sha(HELPER.read_bytes()) == HELPER_SHA and data.sha((CLASSES / 'MainClassCodeStructureAuditV2.class').read_bytes()) == CLASS_SHA, 'fixed data-only helper')
    require({p.name for p in CLASSES.glob('*.class')} == {'MainClassCodeStructureAuditV2.class'}, 'helper-only classpath')
    snapshots = {Path(v['path']).parents[3] for v in n['jars'].values()}
    require(len(snapshots) == 1 and set(n['jars']) == {'api', 'web', 'batch', 'protocol', 'storage', 'bootstrap'}, 'exact six current jars')
    snapshot = snapshots.pop()
    require(all(data.sha(Path(v['path']).read_bytes()) == v['sha256'] for v in n['jars'].values()), 'normal jar containers unchanged')
    SLOT.mkdir()
    catalog = SLOT / 'jars.tsv'
    catalog.write_text(''.join(module + '\t' + v['path'] + '\n' for module, v in sorted(n['jars'].items())))
    steps.SLOT = SLOT
    run = steps.step('read-current-main-metadata', [str(steps.TC / 'jdk-25.0.4/bin/java'), '-cp', str(CLASSES), 'MainClassCodeStructureAuditV2', str(snapshot), str(catalog)])
    require(run['actualExit'] == 0 and not run['timedOut'], 'genuine owned reader terminal')
    lines = (SLOT / 'read-current-main-metadata.stdout').read_text().splitlines()
    require(lines[-1] == 'TOTAL\t1841\t2', 'full physical denominator, held retained')
    values = {}
    held = set()
    for line in lines[:-1]:
        fields = line.split('\t')
        if fields[0] == 'HOLD':
            require(fields[1] in HELD and fields[1] not in held, 'exact two held before entry read')
            held.add(fields[1])
        elif fields[0] == 'CLASS':
            require(len(fields) == 6 and fields[1] not in values and fields[1] not in HELD, 'unique class')
            values[fields[1]] = dict(flags=int(fields[2]), sourceFile=fields[3], fields=int(fields[4]), expectedMethods=int(fields[5]), methods=[])
        else:
            require(fields[0] == 'METHOD' and len(fields) == 7 and fields[1] in values and fields[5] in ('true', 'false'), 'exact method data')
            values[fields[1]]['methods'].append(dict(name=fields[2], descriptor=fields[3], flags=int(fields[4]), hasCode=fields[5] == 'true', codeLength=int(fields[6])))
    require(len(values) == 1841 and held == HELD, 'all metadata and holds')
    result = []
    for module, jar in sorted(n['jars'].items()):
        with zipfile.ZipFile(jar['path']) as archive:
            entries = sorted(x for x in archive.namelist() if x.endswith('.class'))
            for entry in entries:
                physical = module + ':' + entry
                # Do not read or hash held class entries. Container hashes are a separate fixed-input domain.
                if physical in HELD:
                    source_file = entry.rsplit('/', 1)[-1][:-6] + '.java'
                    structure, digest = None, None
                else:
                    structure = values[physical]
                    require(len(structure['methods']) == structure.pop('expectedMethods'), 'exact method count')
                    source_file = structure['sourceFile']
                    digest = data.sha(archive.read(entry))
                path = 'src/schubert-nk-' + module + '/src/main/java/' + entry.rsplit('/', 1)[0] + '/' + source_file
                require(path in sources, 'SourceFile exact source mapping')
                owner = sources[path]
                result.append(dict(physicalKey=physical, sourcePath=path, sourceSha256=owner['sha256'], owner=owner['owner'], costOwner=owner['costOwner'],
                    ownershipMeaning='SOURCE_RESPONSIBILITY_NOT_METHOD_ORACLE_TRACE', classSha256=digest,
                    metadataStatus='UNOBSERVED_HOLD_GRAPH9' if structure is None else 'STATIC_METADATA_NOT_RUNTIME_OR_COVERAGE', structure=structure,
                    methodTestRequirementTrace='NOT_VERIFIED', coverage=None, accepted=False))
    require(len(result) == len({r['physicalKey'] for r in result}) == 1843, 'all1843 retained')
    methods = [m for r in result if r['structure'] is not None for m in r['structure']['methods']]
    counts = collections.Counter(r['sourcePath'] for r in result)
    source_rows = [dict(path=p, sha256=r['sha256'], physicalClasses=counts[p], heldPhysicalClasses=sum(x['sourcePath'] == p and x['structure'] is None for x in result), exactMethodTrace='NOT_VERIFIED') for p, r in sorted(sources.items())]
    require(all(data.sha(Path(v['path']).read_bytes()) == v['sha256'] for v in n['jars'].values()), 'normal containers unchanged after read')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'class-method-inventory.json', result)
    data.write(OUT / 'source-denominator.json', source_rows)
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=SOURCE, invocation=invocation, normalManifestSha256=NORMAL[1],
        descriptorManifestSha256='b238136eb4d965b59ea281c3e610d889b18a0c102839ea9e658b2235fea6a05c', helperSha256=HELPER_SHA, helperClassSha256=CLASS_SHA, readerRun=run,
        sourceFiles=965, physicalClasses=1843, parsedClasses=1841, heldClasses=sorted(HELD), methodsObserved=len(methods),
        codeMethodsObserved=sum(m['hasCode'] for m in methods), noCodeMethodsObserved=sum(not m['hasCode'] for m in methods),
        methodsOfHeldClasses=None, totalMethodDenominatorComplete=False,
        sourceFilesWithoutPhysicalClass=sum(counts[p] == 0 for p in sources),
        classesSha256=data.sha((OUT / 'class-method-inventory.json').read_bytes()), sourcesSha256=data.sha((OUT / 'source-denominator.json').read_bytes()),
        heldEntriesReadOrHashed=False, automaticGeneratedCodeExclusions=False, targetClasspathContainsProduct=False,
        targetClassesDefinedInitializedOrInvoked=False, productTestsExecuted=0, currentCoverageComputed=False,
        oldRuntimeTransferred=False, wholeG13Accepted=False, whole451Accepted=False, newAccepted=0, formalUpdated=False, effortPercent=None, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, physicalClasses=1843, parsedClasses=1841, observedMethods=len(methods), codeMethods=sum(m['hasCode'] for m in methods), heldMethodDenominator=None)))

if __name__ == '__main__':
    main()
