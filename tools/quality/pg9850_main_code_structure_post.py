"""Independent Python binary metadata check; no JVM, product test or held target parse."""
from collections import Counter
import copy
import json
from pathlib import Path
import zipfile
import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode, selftest, code_vectors
from host_tool_invocation import capture, verify

ROOT = data.ROOT
BASE = data.BASE
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
OUT = BASE / 'PG9850-main-code-structure-post-v1'
HELD = frozenset(('api:dev/codex/schubert/nk/api/error/TemporaryInfrastructureException.class',
    'web:dev/codex/schubert/nk/web/bootstrap/WebStartupException.class'))


def validate(proof, rows, independent, old):
    if len(rows) != 1843 or len(independent) != 1841 or len({r['physicalKey'] for r in rows}) != 1843:
        raise ValueError('entire distinct physical set required')
    if any(proof[k] for k in ('targetClasspathContainsProduct','targetDefinedOrInitialized','productTestsExecuted',
        'newExclusionSettings','newAccepted','formalUpdated','currentCoverageComputed','historicalSuccessTransferred',
        'wholeG01Accepted','whole451Accepted')):
        raise ValueError('static structure is not measured coverage or acceptance')
    if set(independent) & HELD or proof['parsedClasses'] != 1841 or set(proof['heldClasses']) != HELD:
        raise ValueError('HOLD is never parsed or missing')
    for row in rows:
        key = row['physicalKey']
        if key not in old or any(row[k] != v for k,v in old[key].items()):
            raise ValueError('original full physical/hash/counter fields unchanged')
        if key in HELD:
            if row['structure'] is not None or row['structureStatus'] != 'HOLD_GRAPH9_BINARY_NOT_PARSED':
                raise ValueError('held structure must remain unobserved')
            continue
        value = independent[key]
        if row['structure'] != value:
            raise ValueError('independent all fields/methods/code length identity')
        if any(m['hasCode'] for m in value['methods']):
            expected = 'SYNTHETIC_CODE_REQUIRES_APPLICABILITY_REVIEW' if value['flags'] & 0x1000 else 'CODE_PRESENT_NOT_RUNTIME_QUALIFICATION'
        elif key.endswith('/package-info.class') and value['fields'] == 0 and value['methods'] == []:
            expected = 'NO_CODE_PACKAGE_ANNOTATION'
        elif value['flags'] & 0x2000 and value['flags'] & 0x0200:
            expected = 'NO_CODE_ANNOTATION_INTERFACE'
        elif value['flags'] & 0x0200:
            expected = 'NO_CODE_INTERFACE'
        else:
            expected = 'NO_CODE_OTHER_UNRESOLVED'
        if row['structureStatus'] != expected:
            raise ValueError('Code/flag applicability is not inferred from missing counters')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary_sha = 'a2b6e797428c46e7940de9e224d044b58c30233388d019c903e74fdce51876d4'
    proof = data.read_checked(BASE/'PG9848-main-code-structure-v2/manifest.json',primary_sha)
    assert proof['actualExit'] == 0 and proof['source'] == SOURCE
    rows = data.read_checked(BASE/'PG9848-main-code-structure-v2/class-structures.json',proof['classStructuresSha256'])
    normal = data.read_checked(BASE/'PG9812-cleanup-values-six-compile-v1/manifest.json',proof['normalManifestSha256'])
    gap = data.read_checked(BASE/'PG9828-existing-host-gap-map-v1/manifest.json',proof['gapManifestSha256'])
    old_rows = data.read_checked(BASE/'PG9828-existing-host-gap-map-v1/physical-class-gap-map.json',gap['physicalGapMapSha256'])
    old = {r['physicalKey']:r for r in old_rows}
    vectors = selftest() + code_vectors()
    independent = {}
    for module,item in normal['jars'].items():
        path = Path(item['path'])
        assert data.sha(path.read_bytes()) == item['sha256']
        with zipfile.ZipFile(path) as jar:
            names = [n for n in jar.namelist() if n.endswith('.class')]
            assert len(names) == len(set(names))
            for name in names:
                key = module + ':' + name
                if key in HELD:
                    continue
                raw = jar.read(name)
                assert key not in independent and data.sha(raw) == old[key]['currentSha256']
                independent[key] = decode(raw,name)
    validate(proof,rows,independent,old)
    negatives = []
    changed = next(i for i,r in enumerate(rows) if r['structure'] is not None and r['structure']['methods'])
    held_index = next(i for i,r in enumerate(rows) if r['physicalKey'] in HELD)
    for name,edit in (
        ('missing-row',lambda p,r:r.pop()),
        ('duplicate-row',lambda p,r:r.__setitem__(0,copy.deepcopy(r[1]))),
        ('wrong-code-length',lambda p,r:r[changed]['structure']['methods'][0].update(codeLength=-1)),
        ('held-promoted',lambda p,r:r[held_index].update(structure={})),
        ('counter-mutated',lambda p,r:r[0]['historicalCounters'].update(LINE=dict(missed=0,covered=999999))),
        ('coverage-promoted',lambda p,r:p.update(currentCoverageComputed=True)),
        ('runtime-promoted',lambda p,r:p.update(targetDefinedOrInitialized=True)),
        ('formal-promoted',lambda p,r:p.update(formalUpdated=True))):
        p,r = copy.deepcopy(proof),copy.deepcopy(rows)
        edit(p,r)
        try:
            validate(p,r,independent,old)
        except ValueError:
            negatives.append(name)
        else:
            raise AssertionError('bad structure claim accepted: '+name)
    assert vectors == 35 and len(negatives) == 8
    group_counts = {}
    for label,predicate in (
        ('oldEmpty426',lambda r:r['historicalSha256'] is not None and not r['historicalCounters'] and r['physicalKey'] not in gap.get('removedClasses',[]) and r['physicalKey'] not in old_missing),
        ('oldAbsent34',lambda r:r['physicalKey'] in old_missing),
        ('added174',lambda r:r['byteState']=='ADDED')):
        group_counts[label] = dict(Counter(r['structureStatus'] for r in rows if predicate(r)))
    # Read only original compiler receipts; never rerun the failed or successful reader.
    work = ROOT.parent/'pgpt-runs/PG379/pg9848-main-code-structure-v1'
    failed = json.loads((work/'compile-reader-exit.safe.json').read_bytes())
    diagnostic = (work/'compile-reader.stderr').read_bytes()
    assert failed['actualExit'] == 1 and data.sha(diagnostic) == failed['stderrSha256']
    assert data.sha((ROOT/'tools/quality/architecture/MainClassCodeStructureAudit.java').read_bytes()) == '2108510103f6398369878d15a92cf4232ba3d0db47c03b8ef93dbaabf7853cd6'
    assert data.sha((ROOT/'tools/quality/pg9848_main_code_structure.py').read_bytes()) == 'f603c21c9ee32c085f04e4f1f4dd7b3c0d97b0b7e59fca4f912aa089f0331f85'
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'independent-structures.json',independent)
    data.write(OUT/'historical-noncounter-structure-summary.json',group_counts)
    (OUT/'original-reader-compile-diagnostic.txt').write_bytes(diagnostic)
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=primary_sha,
        independentParserSha256=data.sha((ROOT/'tools/quality/classfile_code_metadata.py').read_bytes()),
        independentStructuresSha256=data.sha((OUT/'independent-structures.json').read_bytes()),
        historicalGroupSummarySha256=data.sha((OUT/'historical-noncounter-structure-summary.json').read_bytes()),
        physicalClasses=1843,independentlyParsed=1841,heldClasses=sorted(HELD),
        structureCounts=proof['structureCounts'],historicalGroups=group_counts,
        parserVectors=vectors,claimRejectionVectors=negatives,originalCompilerFailure=failed,
        earlierPyflakesFailure=dict(actualExit=1,sourceSha256='8791cfa3a0084e1ddbe2d13d71dfed11c3003d314a3e7cb544aa98c5917fb9ff',
            diagnostic="classfile_code_metadata.py:69:18 local variable '_super' is assigned to but never used",readerStarted=False),
        targetDefinedOrInitialized=False,productTestsExecuted=0,newAccepted=0,formalUpdated=False,
        newExclusionSettings=False,currentCoverageComputed=False,historicalSuccessTransferred=False,
        wholeG01Accepted=False,whole451Accepted=False,effortPercent=None)
    data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,independentlyParsed=1841,held=2,groups=group_counts,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    # Historical non-XML set is taken from the immutable old qualification, never inferred from empty values.
    old_qualification = data.read_checked(BASE/'PG6930-current4222-cases/qualification.json',
        '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731')
    old_missing = frozenset(old_qualification['coveragePhysicalClassKeysNotInXml'])
    assert len(old_missing) == 34
    main()
