"""Add-only LGS vector trace; no diagnostics correction, acceptance or historical runtime reassignment."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
import pg13571_lgs_boundary_config_v5 as cfg
from pg9954_pure_query_registry_metadata import INV, SNAP, SECTIONS, replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE = 'e8e06bedba3311c8335dbb5ba9c4fdffafd86acf'
PRIOR = ('PG13542-main-assignment-final-four-v1', 'e41388eefdb85268ef6a3afb9d75571084b878fd21517514174140a7398bf4fd')
OUT = data.BASE/'PG13584-lgs-boundary-trace-v1'
NORMAL = ('PG13572-lgs-boundary-two-vectors-v1', '849422e3b3794d6c1d580ffc016c36e1bc83b8864eefd33ab1eae10b3793db7a')

def state_after():
    ids, refs, pending = cfg.previous_state()
    assert len(ids) == 6247 and len(refs) == 3349 and len(pending) == 2488
    assert {'PMD-08082', 'PMD-08083'} <= pending & refs & ids
    return ids, refs, pending

def inputs():
    prior = data.read_checked(data.BASE/PRIOR[0]/'manifest.json', PRIOR[1])
    normal = data.read_checked(data.BASE/NORMAL[0]/'manifest.json', NORMAL[1])
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p, sha in hashes.items())
    assert len(prior['sourceRows']) == 995
    assert {r['path'] for r in prior['sourceRows'] if r['sha256'] != hashes[r['path']]} == {cfg.PATH}
    raw, snap = [subprocess.check_output(['git', 'show', SOURCE+':'+p], cwd=data.ROOT) for p in [INV, SNAP]]
    return prior, hashes, raw, snap

def expected(prior, hashes, proof, pin):
    ids, refs, pending = state_after()
    rows = copy.deepcopy(prior['sourceRows'])
    row, = [r for r in rows if r['path'] == cfg.PATH]
    assert row['canonicalOwner'] == row['canonicalCostOwner'] == 'WBS-P016-14'
    row['sha256'] = hashes[cfg.PATH]
    assert proof['source'] == SOURCE and proof['actualExit'] == 0 and proof['tests'] == 8 and proof['suites'] == 1
    assert proof['crcMismatch'] == 0 and proof['singleSession'] and len(proof['physicalClasses']) == 5
    assert proof['totals'] == {'LINE': {'missed': 0, 'covered': 93}, 'METHOD': {'missed': 0, 'covered': 16}, 'CLASS': {'missed': 0, 'covered': 5}, 'BRANCH': {'missed': 2, 'covered': 24}}
    assert proof['coverageGateExit'] == 1 and not proof['targetUnitFour100']
    value = copy.deepcopy(prior)
    for key in ['invocation', 'wholeWbsAuditBefore']:
        value.pop(key, None)
    value.update(source=SOURCE, sourceRows=rows, modifiedTestPaths=[cfg.PATH], modifiedMainPaths=[], modifiedMainBindings=[],
        newTestPaths=[], newMethodIds=[], newTestIds=[], addedSubvectorIds=cfg.VECTOR_IDS,
        priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)), sha256=PRIOR[1], source=prior['source'], oldRuntimeDomainsReassigned=False),
        currentQualification=dict(source=SOURCE, status='WHOLE8_CURRENT_LGS_THREE_UNIT_MEASURED_BRANCH_NOT_100',
            proofManifestSha256=pin, productTestsExecuted=8, junitMethodsAdded=0, addedSubvectors=2,
            measuredProductCounters=proof['totals'], measuredPhysicalClasses=sorted(proof['physicalClasses']), coverageGateExit=1,
            oldPtQualificationTransferred=False, sourceRowsHistoricalRuntimeUnchanged=True),
        sourceDerivedRaw=len(ids), mainRaw=1491, testRaw=4756, totalPriorCorrections=3194,
        joinedContextWarnings=len(refs), sourceReboundCurrentWholePending=len(pending), noCurrentReferenceInThisJoin=len(ids-refs),
        rawDeltaBasis='Zero diagnostic removals; two added independent LGS boundary subvectors; no global replay',
        record=cfg.RECORD, newAccepted=0, formalUpdated=False, effortPercent=None, whole451Accepted=False, wholeF03Accepted=False)
    return value

def documents(value, raw, snap):
    target_pin = data.sha((OUT/'manifest.json').read_bytes())
    parsed = json.loads(raw)
    result = raw
    for name in SECTIONS:
        section = copy.deepcopy(parsed[name])
        marker = 'beforeLgsBoundaryPG13584Reference'
        assert marker not in section
        section[marker] = {k:copy.deepcopy(section[k]) for k in ['source', 'manifest', 'sha256', 'record']}
        section.update(source=SOURCE, manifest=str((OUT/'manifest.json').relative_to(data.ROOT)), sha256=target_pin,
            record=cfg.RECORD, currentAddedTestPaths=[], lgsBoundaryTwoSubvectorQualification=value['currentQualification'])
        result, _, _ = replaced(result, name, section)
    result_snap, _, _ = replaced(snap, 'inventorySha256', data.sha(result))
    validate_docs(result, result_snap, parsed, json.loads(snap))
    return result, result_snap
