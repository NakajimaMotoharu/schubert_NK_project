"""Saved Main observations: all11 cumulative source deltas, no F03/runtime PASS."""
import collections
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import wbs_candidate_trace as trace

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE = 'db33c6a371d3dbc8e84f70462e0e56351bbb18b4'
OUT = data.BASE / 'PG15930-f03-current-main-review-join-v2'
BASELINE = ('PG13253-current-all-java-static-v2', '751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
FRESH = ('PG14226-typed-marker-guard-three-main-static-v1', '0ae9027c8f4819697a6d6926b5b6723dc611c525690d98b0dccfc63259a4c293')

def require(ok, message):
    if not ok:
        raise ValueError(message)

def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def signature(row):
    return encoded([row['path'], row['sourceSha256'], row.get('tool', 'pmd'), row.get('rule', row['attributes'].get('rule')), row['attributes']])

def main_paths(source):
    return {p for p in trace.git_files(source) if p.startswith('src/') and '/src/main/java/' in p and p.endswith('.java')}

def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    b = data.read_checked(data.BASE / BASELINE[0] / 'manifest.json', BASELINE[1])
    fresh_path = data.BASE / FRESH[0] / 'manifest.json'
    fraw = fresh_path.read_bytes()
    require(data.sha(fraw) == FRESH[1], 'fixed fresh public manifest')
    f = json.loads(fraw)
    require(b['source'] == OLD_SOURCE and f['source'] == SOURCE and b['actualExit'] == f['actualExit'] == 0 and b['analysisComplete'] is f['analysisComplete'] is True, 'complete saved analyzer observations')
    baseline = data.read_checked(data.BASE / BASELINE[0] / 'findings.json', b['findingsSha256'])
    fresh = data.read_checked(fresh_path.parent / 'findings.json', f['findingsSha256'])
    require(len(baseline) == 8022 and len(fresh) == 18 and f['mainSourceCount'] == 3 and f['testSourceCount'] == 0, 'fixed all/main subset domains')
    for folder, result in [(data.BASE / BASELINE[0], b), (fresh_path.parent, f)]:
        require(not result['processingErrors'], 'no analyzer processing errors')
        for tool in ('pmd', 'checkstyle'):
            require(data.sha((folder / (tool + '.xml')).read_bytes()) == result['reports'][tool]['sha256'], 'saved raw report hash')
    paths = main_paths(SOURCE)
    require(len(paths) == 965 and paths == main_paths(OLD_SOURCE), 'same full Main path domain')
    current = trace.git_artifacts(SOURCE, sorted(paths))
    previous = trace.git_artifacts(OLD_SOURCE, sorted(paths))
    changed = {p for p in paths if current[p] != previous[p]}
    query_three = {r['path'] for r in fresh}
    require(len(changed) == 11 and len(query_three) == 3 and query_three < changed, 'all cumulative Main changes, not latest subset only')
    supplemental = []
    supplemental_refs = []
    bound_eight = set()
    for folder, pin in [
        ('PG13505-main-assignment-seven-v1', 'aaa38f93d84f57a9ef670699063e6f290fc863326badd2db9d7a4592730929bf'),
        ('PG13534-main-assignment-final-four-v1', '36eab3cec0c0a59a9bda0e44b9c98ce7e97701f0d80fee9a9c0f4a6361c20cda')]:
        saved = data.read_checked(data.BASE / folder / 'manifest.json', pin)
        require(saved['actualExit'] == 0 and saved['productTestsExecuted'] == 0, 'saved static only')
        selected = {p for p, h in saved['candidateSourceHashes'].items() if p in changed - query_three and h == data.sha(current[p])}
        require(len(selected) == 4 and not selected & bound_eight, 'two exact nonoverlap groups of four current bytes')
        bound_eight |= selected
        for tool in ('pmd', 'checkstyle'):
            report = data.BASE / folder / (tool + '.xml')
            require(data.sha(report.read_bytes()) == saved['reports'][tool], 'saved supplemental XML')
            root = ET.fromstring(report.read_bytes())
            for node in root:
                tag = node.tag.rpartition('}')[2]
                if tag in ('error', 'configerror'):
                    raise ValueError('supplemental analyzer processing error')
                if tag != 'file':
                    continue
                name = node.get('name')
                marker = '/src/schubert-nk-'
                require(marker in name, 'fixed public source file path')
                path = name[name.index(marker) + 1:]
                require(path in saved['candidateSourceHashes'], 'XML within exact saved selected scope')
                for item in node:
                    tag = item.tag.rpartition('}')[2]
                    require(tag == ('violation' if tool == 'pmd' else 'error'), 'only diagnostic, not processing error')
                    if path not in selected:
                        continue
                    attributes = dict(item.attrib)
                    rule = attributes.get('rule', attributes.get('source', 'UNKNOWN'))
                    require(rule not in ('com.puppycrawl.tools.checkstyle.Checker', 'com.puppycrawl.tools.checkstyle.TreeWalker'), 'no checkstyle processing error')
                    supplemental.append(dict(tool=tool, path=path, sourceSha256=data.sha(current[path]),
                        module=path.split('/')[1].removeprefix('schubert-nk-'), kind='main', attributes=attributes,
                        rule=rule, message=' '.join(''.join(item.itertext()).split()) if tool == 'pmd' else attributes.get('message', '')))
        supplemental_refs.append(dict(manifest=folder + '/manifest.json', sha256=pin, selectedPaths=sorted(selected)))
    require(bound_eight == changed - query_three and len(bound_eight) == 8, 'no changed Main without saved exact-byte observation')

    require(all(not (data.ROOT / p).is_symlink() and (data.ROOT / p).read_bytes() == current[p] for p in paths), 'current all Main bytes')
    retained = [r for r in baseline if r['kind'] == 'main' and r['path'] not in changed]
    observations = retained + fresh + supplemental
    require(all(r['sourceSha256'] == data.sha(current[r['path']]) for r in observations), 'every observation exact current byte')
    reviews = collections.defaultdict(list)
    inputs = []
    rejected = collections.Counter()
    for folder in sorted(data.BASE.iterdir()):
        name = folder.name.lower()
        if not folder.is_dir() or not any(t in name for t in ('main', 'context', 'type', 'catch', 'resource', 'thread', 'classloader', 'protocol')):
            continue
        rp = folder / 'review.json'
        mp = folder / 'manifest.json'
        if not rp.is_file() or not mp.is_file():
            continue
        require(not rp.is_symlink() and not mp.is_symlink(), 'public review regular files')
        mr = mp.read_bytes()
        m = json.loads(mr)
        if m.get('actualExit') != 0 or not isinstance(m.get('reviewSha256'), str):
            continue
        rv = data.read_checked(rp, m['reviewSha256'])
        rr = rv.get('rows', []) if isinstance(rv, dict) else rv
        if not isinstance(rr, list):
            continue
        inputs.append(dict(manifest=str(mp.relative_to(data.ROOT)), sha256=data.sha(mr), reviewSha256=m['reviewSha256'], rows=len(rr)))
        for ordinal, row in enumerate(rr):
            if not isinstance(row, dict) or row.get('path') not in paths or not isinstance(row.get('attributes'), dict):
                rejected['OUTSIDE_MAIN_OR_NO_EXACT_COORDINATES'] += 1
                continue
            if row.get('sourceSha256') != data.sha(current[row['path']]):
                rejected['SOURCE_BYTE_MISMATCH'] += 1
                continue
            if row.get('rawRetained') is not True or row.get('productTestsExecuted') != 0:
                rejected['NOT_STATIC_RETAINED_REVIEW'] += 1
                continue
            reviews[signature(row)].append(dict(manifest=str(mp.relative_to(data.ROOT)), manifestSha256=data.sha(mr), reviewSha256=m['reviewSha256'], reviewOrdinal=ordinal, oldFindingId=row.get('id'), meaning='EXACT_BYTE_COORDINATE_REVIEW_REFERENCE_NOT_APPLICABILITY_OR_RUNTIME_PASS'))
    rows = []
    duplicate_ordinals = collections.Counter()
    for original in observations:
        sig = signature(original)
        ordinal = duplicate_ordinals[sig]
        duplicate_ordinals[sig] += 1
        row = dict(original)
        row.update(currentSource=SOURCE, staticObservationId='CURRENT-MAIN-' + data.sha(sig + b':' + str(ordinal).encode()), sameCoordinateOccurrence=ordinal,
                   measurementDomain='SAVED_EXACT_BYTE_EIGHT_MAIN_PG13505_13534' if original['path'] in bound_eight else 'FRESH_THREE_MAIN_PG14226' if original['path'] in query_three else 'UNCHANGED_MAIN_INPUT_PG13253',
                   contextReferences=reviews.get(sig, []), applicability='NOT_DETERMINED_BY_REFERENCE_JOIN',
                   currentWholeQualification=False, ptExecutionExempt=False, actualViolation=None)
        rows.append(row)
    require(len(rows) == len({r['staticObservationId'] for r in rows}), 'all unique diagnostic occurrences')
    pending = [r for r in rows if not r['contextReferences']]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'main-source-inputs.json', {p: data.sha(current[p]) for p in sorted(paths)})
    data.write(OUT / 'review-inputs.json', inputs)
    data.write(OUT / 'current-main-observations.json', rows)
    data.write(OUT / 'unreferenced-main-queue.json', [dict(id=r['staticObservationId'], path=r['path'], sourceSha256=r['sourceSha256'], rule=r['rule'], attributes=r['attributes']) for r in pending])
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation, source=SOURCE,
        baselineManifestSha256=BASELINE[1], freshManifestSha256=data.sha(fraw), mainSources=965, unchangedMainSources=954, changedMainSources=11, supplementalReferences=supplemental_refs, supplementalMainSources=8,
        priorAuxiliaryContextNotRequalified=True, currentWholeAnalyzerNotIssued=True,
        observationCount=len(rows), scannerCounts=dict(collections.Counter(r['tool'] for r in rows)), ruleCounts=dict(collections.Counter(r['rule'] for r in rows)),
        exactByteCoordinateReferenced=sum(bool(r['contextReferences']) for r in rows), unreferencedMain=len(pending), reviewInputManifests=len(inputs), reviewInputRejectedRows=dict(rejected),
        sourceInputsSha256=data.sha((OUT / 'main-source-inputs.json').read_bytes()), reviewInputsSha256=data.sha((OUT / 'review-inputs.json').read_bytes()),
        observationsSha256=data.sha((OUT / 'current-main-observations.json').read_bytes()), queueSha256=data.sha((OUT / 'unreferenced-main-queue.json').read_bytes()),
        testSourceScopeIncluded=False, characterizationJavaIncluded=False, analyzerReexecuted=False,
        applicabilityAcceptedFromReference=False, actualViolationCount=None, oldRuntimeTransferred=False,
        wholeF03Accepted=False, whole451Accepted=False, newAccepted=0, formalUpdated=False, effortPercent=None,
        productTestsExecuted=0, productClassesLoaded=0, externalActions=0, privateRawRead=False))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, observations=len(rows), referenced=sum(bool(r['contextReferences']) for r in rows), unreferenced=len(pending), reviewInputs=len(inputs))))

if __name__ == '__main__':
    main()
