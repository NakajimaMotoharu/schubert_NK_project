"""Read-only historical XML/current Jar/follow-up gap map. Never runs or qualifies product code."""
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import evidence_followup_index as followup
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
OLD_SOURCE = 'e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
OLD = data.BASE / 'PG6930-current4222-cases'
OUT = data.BASE / 'PG9828-existing-host-gap-map-v1'
TYPES = {'LINE','METHOD','CLASS','BRANCH'}


def reported_status(counters):
    if not counters:
        return 'NO_HISTORICAL_COUNTERS'
    if not set(counters) <= TYPES:
        raise ValueError('known four counter dimensions only')
    for value in counters.values():
        if set(value) != {'missed','covered'} or any(type(v) is not int or v < 0 for v in value.values()):
            raise ValueError('nonnegative exact integer counters required')
    if any(v['missed'] for v in counters.values()):
        return 'HISTORICAL_REPORTED_MISSES'
    if not {'LINE','METHOD','CLASS'} <= set(counters):
        return 'INCOMPLETE_HISTORICAL_COUNTER_DIMENSIONS'
    if any(sum(counters[k].values()) == 0 for k in ('LINE','METHOD','CLASS')):
        return 'ZERO_DENOMINATOR_NOT_HUNDRED'
    return 'HISTORICAL_REPORTED_NO_MISSES_NOT_CURRENT_QUALIFICATION'


def selftest():
    good = {k:dict(missed=0,covered=1) for k in ('LINE','METHOD','CLASS')}
    assert reported_status(good) == 'HISTORICAL_REPORTED_NO_MISSES_NOT_CURRENT_QUALIFICATION'
    assert 'BRANCH' not in good
    assert reported_status({}) == 'NO_HISTORICAL_COUNTERS'
    assert reported_status({'LINE':dict(missed=0,covered=1)}) == 'INCOMPLETE_HISTORICAL_COUNTER_DIMENSIONS'
    assert reported_status({**good,'LINE':dict(missed=0,covered=0)}) == 'ZERO_DENOMINATOR_NOT_HUNDRED'
    assert reported_status({**good,'BRANCH':dict(missed=1,covered=0)}) == 'HISTORICAL_REPORTED_MISSES'
    for bad in ({'UNKNOWN':dict(missed=0,covered=1)}, {'LINE':dict(missed=True,covered=1)},
        {'LINE':dict(missed=-1,covered=1)}, {'LINE':dict(missed=0)}, {'LINE':dict(missed=0,covered='1')}):
        try:
            reported_status(bad)
        except ValueError:
            continue
        raise AssertionError('counter parser accepted malformed fixture')
    return 10


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    vectors = selftest()
    qualified_sha = '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'
    old = data.read_checked(OLD / 'qualification.json',qualified_sha)
    witness = data.read_checked(data.BASE / 'PG6944-current4222-host-measurement-v1/manifest.json',
        '6132be4dd8b05f827ceab8dfcbea9a79fdda0e21af8849183c59c8eb732e85f3')
    assert witness['originalQualification']['sha256'] == qualified_sha
    assert old['actualExit'] == witness['actualExit'] == 0 and old['productionSource'] == OLD_SOURCE
    assert (old['tests'],old['suites'],old['mainClasses']) == (4222,660,1669)
    normal_sha = 'e074d972cbaf56b94ba4d25a77e7368b4f53ccd91489be0fbc27f07ef3975c95'
    normal = data.read_checked(data.BASE / 'PG9812-cleanup-values-six-compile-v1/manifest.json',normal_sha)
    assert normal['actualExit'] == 0 and normal['source'] == SOURCE and normal['testsExecuted'] == 0
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    counters,xml_hashes,module_reports = {},{},{}
    for module,info in old['modules'].items():
        xml = OLD / 'coverage' / module / 'site/jacoco/jacoco.xml'
        digest = data.sha(xml.read_bytes())
        assert digest == info['coverageXmlSha256']
        xml_hashes[module] = digest
        nodes = ET.parse(xml).getroot().findall('.//class')
        local = Counter()
        for node in nodes:
            key = module + ':' + node.get('name') + '.class'
            assert key in old['allPhysicalMainSha256'] and key not in counters
            values = {n.get('type'):dict(missed=int(n.get('missed')),covered=int(n.get('covered')))
                for n in node.findall('counter') if n.get('type') in TYPES}
            assert values == old['allActualClassCounters'][key]
            counters[key] = values
            local[reported_status(values)] += 1
        module_reports[module] = dict(xmlClasses=len(nodes),historicalStates=dict(local))
    assert counters == old['allActualClassCounters'] and len(counters) == 1635
    assert sorted(set(old['allPhysicalMainSha256']) - set(counters)) == sorted(old['coveragePhysicalClassKeysNotInXml'])
    assert len(old['coveragePhysicalClassKeysNotInXml']) == 34
    current = {}
    for module,item in normal['jars'].items():
        jar = Path(item['path'])
        assert data.sha(jar.read_bytes()) == item['sha256']
        with zipfile.ZipFile(jar) as archive:
            for name in archive.namelist():
                if name.endswith('.class'):
                    key = module + ':' + name
                    assert key not in current
                    current[key] = data.sha(archive.read(name))
    assert len(current) == 1843
    rows,changes = [],{}
    byte_counts = Counter()
    for key,digest in sorted(current.items()):
        old_hash = old['allPhysicalMainSha256'].get(key)
        status = 'ADDED' if old_hash is None else 'SAME_BYTE' if old_hash == digest else 'CHANGED_BYTE'
        byte_counts[status] += 1
        values = counters.get(key,{})
        rows.append(dict(physicalKey=key,currentSha256=digest,historicalSha256=old_hash,byteState=status,
            historicalCounters=values,historicalCounterState=reported_status(values),
            currentDynamicQualification='NOT_EVALUATED_NO_SOURCE_TRANSFER'))
        if status != 'SAME_BYTE':
            module,name = key.split(':',1)
            outer = name.removesuffix('.class').split('$',1)[0]
            if outer.endswith('/package-info'):
                continue
            path = 'src/schubert-nk-' + module + '/src/main/java/' + outer + '.java'
            assert path in normal['begin']['inputHashes']
            changes.setdefault(path,dict(outerNameCandidate=outer.rsplit('/',1)[-1],sourceSha256=normal['begin']['inputHashes'][path],
                binarySourceFileIdentityNotInferred=True,physicalKeys=[]))['physicalKeys'].append(key)
    assert sum(byte_counts.values()) == 1843 and byte_counts == Counter(SAME_BYTE=1660,ADDED=174,CHANGED_BYTE=9)
    removed = sorted(set(old['allPhysicalMainSha256']) - set(current))
    assert not removed
    corpus = followup.corpus()
    for value in changes.values():
        hits = followup.index_entries(value['outerNameCandidate'],corpus)
        value['publicFollowupMatchCount'] = len(hits)
        value['newestPublicFollowups'] = hits[:4]
        value['acceptanceOrPermissionInferred'] = False
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'physical-class-gap-map.json',rows)
    data.write(OUT / 'delta-source-followup-index.json',changes)
    historical_misses = [r for r in rows if r['historicalCounterState'] == 'HISTORICAL_REPORTED_MISSES']
    result = dict(actualExit=0,source=SOURCE,historicalSource=OLD_SOURCE,invocation=invocation,
        historicalQualificationSha256=qualified_sha,historicalWitnessManifestSha256='6132be4dd8b05f827ceab8dfcbea9a79fdda0e21af8849183c59c8eb732e85f3',
        normalManifestSha256=normal_sha,originalTests=4222,originalSuites=660,originalMainClasses=1669,
        historicalClassCounters=1635,historicalClassesNotInXml=34,historicalModules=module_reports,historicalXmlHashes=xml_hashes,
        currentPhysicalClasses=1843,physicalBytePartition=dict(byte_counts),removedClasses=removed,
        historicalMissClassCount=len(historical_misses),historicalMissesSameByte=sum(r['byteState'] == 'SAME_BYTE' for r in historical_misses),
        changedOuterSourceCandidates=len(changes),followupIndexedCandidates=len(changes),publicCorpusDocuments=len(corpus),
        changesWithNoLiteralDocumentMatch=sum(not v['publicFollowupMatchCount'] for v in changes.values()),
        physicalGapMapSha256=data.sha((OUT / 'physical-class-gap-map.json').read_bytes()),
        sourceFollowupIndexSha256=data.sha((OUT / 'delta-source-followup-index.json').read_bytes()),counterSchemaVectors=vectors,
        productTestsExecuted=0,currentCoverageComputed=False,historicalSuccessTransferred=False,coverageUnion=False,
        missingOrZeroCountersNotPromoted=True,actualExternalOperations=0,graph9Operations=0,
        whole451Accepted=False,wholeG01Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(OUT / 'manifest.json',result)
    print(json.dumps(dict(actualExit=0,currentPhysicalClasses=1843,bytePartition=dict(byte_counts),historicalMissClasses=len(historical_misses),
        changedOuterCandidates=len(changes),noLiteralMatch=result['changesWithNoLiteralDocumentMatch'],
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
