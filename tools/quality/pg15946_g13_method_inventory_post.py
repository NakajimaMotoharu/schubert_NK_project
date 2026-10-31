"""Python independent class metadata; exclude two held entries before read/hash/parse."""
import collections
import copy
import json
from pathlib import Path
import zipfile
import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode
from host_tool_invocation import capture, verify
import pg15944_g13_current_main_method_inventory as original

PIN = 'dd9307aadd9b2eb9acb1b1cefaf34b68bc6aa01424ba57af2e3d6a4d69244af1'
OUT = data.BASE / 'PG15946-g13-current-main-method-post-v1'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def assess(p, rows, sources, expected, expected_sources):
    require(p['actualExit'] == 0 and p['source'] == original.SOURCE and p['normalManifestSha256'] == original.NORMAL[1], 'current source/normal')
    require((p['sourceFiles'], p['physicalClasses'], p['parsedClasses'], p['methodsObserved'], p['codeMethodsObserved'], p['noCodeMethodsObserved'], p['sourceFilesWithoutPhysicalClass']) == (965, 1843, 1841, 11922, 11393, 529, 0), 'exact observed counts')
    require(set(p['heldClasses']) == original.HELD and p['methodsOfHeldClasses'] is None and p['totalMethodDenominatorComplete'] is False, 'held method denominator unknown')
    require(len(rows) == len({r['physicalKey'] for r in rows}) == 1843 and rows == expected and sources == expected_sources, 'every class/method/source exact independent data')
    for field in ('heldEntriesReadOrHashed', 'automaticGeneratedCodeExclusions', 'targetClasspathContainsProduct', 'targetClassesDefinedInitializedOrInvoked', 'currentCoverageComputed', 'oldRuntimeTransferred', 'wholeG13Accepted', 'whole451Accepted', 'formalUpdated'):
        require(p[field] is False, 'no execution/coverage/promotion: ' + field)
    for field in ('productTestsExecuted', 'newAccepted', 'externalActions'):
        require(type(p[field]) is int and p[field] == 0, 'no Product/acceptance')
    require(p['effortPercent'] is None and p['readerRun']['actualExit'] == 0 and p['readerRun']['timedOut'] is False, 'genuine terminal not effort')

def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    p = data.read_checked(original.OUT / 'manifest.json', PIN)
    rows = data.read_checked(original.OUT / 'class-method-inventory.json', p['classesSha256'])
    sources = data.read_checked(original.OUT / 'source-denominator.json', p['sourcesSha256'])
    n = data.read_checked(data.BASE / original.NORMAL[0] / 'manifest.json', original.NORMAL[1])
    d = data.read_checked(data.BASE / 'PG15918-g13-current-static-descriptor-v1/manifest.json', p['descriptorManifestSha256'])
    artifacts = data.read_checked(data.BASE / 'PG15918-g13-current-static-descriptor-v1/artifacts.json', d['artifactsSha256'])
    source_map = {r['path']: r for r in artifacts if r['path'].startswith('src/') and r['kind'] == 'JAVA'}
    require(len(source_map) == 965 and all(data.sha((data.ROOT / path).read_bytes()) == r['sha256'] for path, r in source_map.items()), 'same full current source')
    qualification = data.read_checked(data.BASE / 'PG9850-main-code-structure-post-v1/manifest.json', '995f0f16fdc8b9df3daf40a5ba19768ac9dfcf70c2e0d4f96fb4d15ea20b953e')
    require(qualification['actualExit'] == 0 and qualification['parserVectors'] == 35 and qualification['independentParserSha256'] == data.sha((data.ROOT / 'tools/quality/classfile_code_metadata.py').read_bytes()) == '2227e1e8df1ff91b606f094c7ee64366023273ca740d4d47126ed0928190e2f0', 'unchanged qualified passive decoder, no selftest replay')
    expected = []
    for role, item in sorted(n['jars'].items()):
        require(data.sha(Path(item['path']).read_bytes()) == item['sha256'], 'fixed current jar container')
        with zipfile.ZipFile(item['path']) as archive:
            for entry in sorted(x for x in archive.namelist() if x.endswith('.class')):
                physical = role + ':' + entry
                if physical in original.HELD:
                    # Strictly before archive.read or decoder: this is not an alternate held parser.
                    model, digest = None, None
                    filename = entry.rsplit('/', 1)[-1][:-len('.class')] + '.java'
                else:
                    raw = archive.read(entry)
                    model, digest = decode(raw, entry), data.sha(raw)
                    filename = model['sourceFile']
                path = 'src/schubert-nk-' + role + '/src/main/java/' + entry.rsplit('/', 1)[0] + '/' + filename
                owner = source_map[path]
                expected.append(dict(physicalKey=physical, sourcePath=path, sourceSha256=owner['sha256'], owner=owner['owner'], costOwner=owner['costOwner'], ownershipMeaning='SOURCE_RESPONSIBILITY_NOT_METHOD_ORACLE_TRACE', classSha256=digest, metadataStatus='UNOBSERVED_HOLD_GRAPH9' if model is None else 'STATIC_METADATA_NOT_RUNTIME_OR_COVERAGE', structure=model, methodTestRequirementTrace='NOT_VERIFIED', coverage=None, accepted=False))
    counts = collections.Counter(r['sourcePath'] for r in expected)
    expected_sources = [dict(path=path, sha256=r['sha256'], physicalClasses=counts[path], heldPhysicalClasses=sum(x['sourcePath'] == path and x['structure'] is None for x in expected), exactMethodTrace='NOT_VERIFIED') for path, r in sorted(source_map.items())]
    assess(p, rows, sources, expected, expected_sources)
    negatives = []
    for field, value in [('source', '0'*40), ('physicalClasses', 1841), ('parsedClasses', 1843), ('methodsObserved', 11920), ('methodsOfHeldClasses', 0), ('totalMethodDenominatorComplete', True), ('heldEntriesReadOrHashed', True), ('automaticGeneratedCodeExclusions', True), ('targetClasspathContainsProduct', True), ('currentCoverageComputed', True), ('oldRuntimeTransferred', True), ('wholeG13Accepted', True), ('productTestsExecuted', 11922), ('newAccepted', True), ('effortPercent', 100)]:
        bad = copy.deepcopy(p)
        bad[field] = value
        try:
            assess(bad, rows, sources, expected, expected_sources)
        except ValueError:
            negatives.append(field)
        else:
            raise ValueError('unrejected metadata promotion: ' + field)
    for label, mutate in [('drop-class', lambda r, s: r.pop()), ('duplicate', lambda r, s: r.__setitem__(0, r[1])), ('wrong-owner', lambda r, s: r[0].update(owner='WBS-G13.07')), ('wrong-source', lambda r, s: r[0].update(sourceSha256='0'*64)), ('missing-method', lambda r, s: next(x for x in r if x['structure'] and x['structure']['methods'])['structure']['methods'].pop()), ('wrong-code-length', lambda r, s: next(x for x in r if x['structure'] and x['structure']['methods'])['structure']['methods'][0].update(codeLength=0)), ('held-parsed', lambda r, s: next(x for x in r if x['structure'] is None).update(structure={})), ('held-hash', lambda r, s: next(x for x in r if x['structure'] is None).update(classSha256='0'*64)), ('coverage', lambda r, s: r[0].update(coverage=100)), ('method-trace', lambda r, s: r[0].update(methodTestRequirementTrace='VERIFIED')), ('source-drop', lambda r, s: s.pop())]:
        rr, ss = copy.deepcopy(rows), copy.deepcopy(sources)
        mutate(rr, ss)
        try:
            assess(p, rr, ss, expected, expected_sources)
        except ValueError:
            negatives.append(label)
        else:
            raise ValueError('unrejected metadata row: ' + label)
    verify(p['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=original.SOURCE, invocation=invocation, parentManifestSha256=PIN,
        independentDecoderSha256=qualification['independentParserSha256'], existingDecoderVectorsReference='PG9850/35_NOT_REEXECUTED',
        independentNegativeVectors=len(negatives), negativeLabels=negatives, independentlyParsed=1841, heldEntriesReadOrHashed=False,
        methodsObserved=11922, codeMethodsObserved=11393, noCodeMethodsObserved=529, methodsOfHeldClasses=None,
        wholeG13Accepted=False, whole451Accepted=False, currentCoverageComputed=False, productTestsExecuted=0,
        newAccepted=0, formalUpdated=False, effortPercent=None, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, independentNegativeVectors=len(negatives), observedMethods=11922, heldMethods=None)))

if __name__ == '__main__':
    main()
