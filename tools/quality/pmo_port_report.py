"""Pure guarded projection of already verified port manifests; not a qualification gate.

No I/O, Product execution, events, quota access or source qualification happens here.
Callers still bind actual artifacts/oracles/dependencies/postconditions and fresh quota.
"""
import re


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value):
    return type(value) is int and value >= 0


def source_marker(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{40}', value) is not None


def project_port(manifest, expected):
    require(isinstance(manifest, dict) and isinstance(expected, dict), 'explicit manifest and expectation required')
    require(integer(manifest.get('actualExit')) and manifest['actualExit'] == 0, 'successful actual terminal required')
    for key in ('failures', 'errors', 'skipped', 'aborted'):
        require(integer(manifest.get(key)) and manifest[key] == 0, 'all unsuccessful counts must explicitly be zero')
    count = manifest.get('tests')
    require(integer(count) and count > 0 and type(expected.get('tests')) is int and count == expected['tests'], 'exact independently expected test count required')
    selected = manifest.get('selectedTestMethods')
    require(isinstance(selected, list) and len(selected) == count, 'complete selected method identities required')
    pairs = []
    for pair in selected:
        require(isinstance(pair, (list, tuple)) and len(pair) == 2 and all(isinstance(s, str) and re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$.]*', s) for s in pair), 'bounded class and method identities required')
        pairs.append(tuple(pair))
    require(len(set(pairs)) == count, 'duplicate method identities are not extra tests')
    require(source_marker(manifest.get('source')) and manifest['source'] == expected.get('source') and source_marker(manifest.get('productionCoreMain')), 'frozen run source and explicit Main marker required')
    require(manifest.get('oldExecUnion') is False and manifest.get('manualCoverageExclusions') == [], 'union and manual exclusions cannot be projected as complete')
    hits = manifest.get('heldFourProbeHits')
    require(isinstance(hits, dict) and len(hits) == 4 and all(integer(v) and v == 0 for v in hits.values()), 'four explicit held probe counts required')
    physical = manifest.get('physicalHashes')
    coverage = manifest.get('coverage')
    require(isinstance(physical, dict) and type(expected.get('physical')) is int and len(physical) == expected['physical'] > 0, 'complete physical closure required')
    require(all(isinstance(n, str) and re.fullmatch(r'[A-Za-z0-9_$/]+', n) and isinstance(h, str) and re.fullmatch(r'[0-9a-f]{64}', h) for n, h in physical.items()), 'physical names and hashes required')
    require(isinstance(coverage, dict) and set(coverage) == set(physical), 'every physical class must have an explicit coverage entry')
    empty = manifest.get('abstractInterfacesNoExecutableMethods'), manifest.get('compilerGeneratedNoCodeClasses')
    require(all(isinstance(v, list) for v in empty), 'explicit no-code classifications required')
    no_code = empty[0] + empty[1]
    require(len(set(no_code)) == len(no_code) and set(no_code) <= set(physical), 'no-code classifications must be unique physical entries')
    four = {key: 0 for key in ('LINE', 'METHOD', 'CLASS', 'BRANCH')}
    for name, counters in coverage.items():
        require(isinstance(counters, dict), 'structured counters required')
        if not counters:
            require(name in no_code, 'empty counter is not an implicit exclusion')
            continue
        require(name not in no_code and {'LINE', 'METHOD', 'CLASS'} <= set(counters), 'executable class counters required')
        for key, counter in counters.items():
            require(isinstance(counter, dict) and integer(counter.get('covered')) and integer(counter.get('missed')) and counter['missed'] == 0, 'every reported counter must have zero misses')
            if key in four:
                four[key] += counter['covered']
    require([four[k] for k in four] == expected.get('four') and four['CLASS'] == len(physical) - len(no_code), 'independent expected counters and full executable class count required')
    require(integer(manifest.get('testClasses')) and manifest['testClasses'] == len({p[0] for p in pairs}), 'actual selected test class count required')
    return dict(schema='PGPT_PORT_PROJECTION_V1', source=manifest['source'], mainSource=manifest['productionCoreMain'], tests=count, testClasses=manifest['testClasses'], fourCounters=four, missed=0, physical=len(physical), noCodeClasses=no_code, selectedMethods=sorted(pairs), qualificationTransferred=False)


def render_port(projection, evidence_path, evidence_hash, spec_path):
    require(projection.get('schema') == 'PGPT_PORT_PROJECTION_V1', 'validated projection required')
    for path in (evidence_path, spec_path):
        require(isinstance(path, str) and path.startswith('evidence/01_PT/') and '..' not in path.split('/') and not any(x in path for x in ('\n', '\r', 'private')), 'public evidence references only')
    require(re.fullmatch(r'[0-9a-f]{64}', evidence_hash) is not None, 'exact manifest hash required')
    four = projection['fourCounters']
    counter = ' / '.join(f'{key}={four[key]}' for key in ('LINE', 'METHOD', 'CLASS', 'BRANCH'))
    return (f"# 単体試験の限定結果\n\n仕様: {spec_path}\n\n"
            f"Test source: {projection['source']} / Main source: {projection['mainSource']}。"
            f"選択{projection['tests']}件・{projection['testClasses']} Testclass、失敗/エラー/skipped/abortedは全0。"
            f"全physical {projection['physical']}、{counter}、各報告counterの未網羅0。分岐0は実行分岐なしを意味する。\n\n"
            f"manifest: {evidence_path}\nSHA256: {evidence_hash}\n\n"
            "この文書は独立後検証済みmanifestの数値projectionであり、source/依存/独立oracle/後条件の資格認定は別途必要。"
            "個別WBS受入・正式1964PT/53scope・工数完成率・全451・IT/STは更新しない。\n")
