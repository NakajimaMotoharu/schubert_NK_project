"""Registry/source-domain updates for existing Test PG; preserve all canonical and historical fields."""
import copy
import difflib
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_literal_batch_sources import original_value, prior_normal, out
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced, SECTIONS, INV, SNAP
from pg9338_wbs_reference_metadata_post import validate as validate_docs

def state_after(cfg):
    ids,refs,pending = cfg.PREVIOUS_STATE();original = original_value(cfg)
    removed = {r['id'] for row in original['sources'] for r in row['mapping']}
    retained = {r['id'] for row in original['sources'] for r in row['findings']}-removed
    assert len(removed) == cfg.EXPECTED_CORRECTIONS and removed <= ids-refs and len(ids) == cfg.BEFORE_RAW
    return ids-removed,refs,pending|(retained&refs)

def inputs(cfg,source,normal_pin,proof_pin):
    prior = data.read_checked(data.BASE/cfg.PRIOR_TRACE[0]/'manifest.json',cfg.PRIOR_TRACE[1])
    normal = data.read_checked(out(cfg,cfg.NORMAL_NUMBER)/'manifest.json',normal_pin)
    proof = data.read_checked(out(cfg,cfg.POST_NUMBER)/'manifest.json',proof_pin)
    assert normal['source'] == proof['source'] == source and normal['actualExit'] == proof['actualExit'] == normal['testsExecuted'] == 0
    assert proof['productTestsExecuted'] == 0 and proof['dynamicPtStatus'] == 'NOT_EXECUTED_HOLD' and proof['coverageStatus'] == 'NOT_MEASURED'
    assert proof['allMainPhysicalUnchanged'] == 1843 and proof['currentTestPhysical'] == 1974 and proof['newTestPhysical'] == 0
    assert proof['privateConstantsAdded'] == cfg.EXPECTED_CORRECTIONS
    hashes = normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items())
    assert {r['path'] for r in prior['sourceRows'] if r['sha256'] != hashes[r['path']]} == set(cfg.PATHS)
    old = prior_normal(cfg);original = original_value(cfg)
    for row in original['sources']:
        assert data.sha(row['text'].encode()) == row['sha256'] == cfg.PATHS[row['path']][0] == old['begin']['inputHashes'][row['path']]
    raw,snap = [subprocess.check_output(['git','show',source+':'+path],cwd=data.ROOT) for path in [INV,SNAP]]
    return prior,proof,hashes,raw,snap

def expected(cfg,source,proof_pin,prior,p,hashes):
    value = copy.deepcopy(prior)
    for key in ['invocation','wholeWbsAuditBefore']:value.pop(key,None)
    rows = copy.deepcopy(prior['sourceRows'])
    for path,(_,_,owner) in cfg.PATHS.items():
        selected = [r for r in rows if r['path'] == path];assert len(selected) == 1
        assert selected[0]['canonicalOwner'] == selected[0]['canonicalCostOwner'] == owner
        selected[0]['sha256'] = hashes[path]
    ids,refs,pending = state_after(cfg)
    value.update(source=source,sourceRows=rows,modifiedTestPaths=sorted(cfg.PATHS),newTestPaths=[],newMethodIds=[],newTestIds=[],newPathsAdded=0,
        priorRegistryReference=dict(path=str((data.BASE/cfg.PRIOR_TRACE[0]/'manifest.json').relative_to(data.ROOT)),sha256=cfg.PRIOR_TRACE[1],source=prior['source'],oldRuntimeDomainsReassigned=False),
        currentQualification=dict(source=source,status='PG_STATIC_ONLY_NOT_PT_QUALIFIED',proofManifestSha256=proof_pin,productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',measuredProductCounters=None,
            allMainPhysicalUnchanged=p['allMainPhysicalUnchanged'],currentTestPhysical=p['currentTestPhysical'],changedTestPhysical=p['changedTestPhysical'],newTestPhysical=0,rawStaticScope=p['rawStatic'],rawStaticGateExit=p['rawStaticGateExit'],spotbugsSixExit=0,oldPtQualificationTransferred=False),
        sourceDerivedRaw=len(ids),mainRaw=1502,testRaw=cfg.BEFORE_TEST_RAW-cfg.EXPECTED_CORRECTIONS,totalPriorCorrections=cfg.BEFORE_CORRECTIONS+cfg.EXPECTED_CORRECTIONS,
        joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),contextStateTransition='f03_literal_batch_trace.state_after('+cfg.PREFIX+')',
        rawDeltaBasis='Exact original'+str(cfg.EXPECTED_CORRECTIONS)+' literal-only Test corrections; untouched diagnostics retained, global analyzer not replayed',actualViolationCount=None,
        wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0)
    return value

def validate(value,cfg,source,proof_pin,prior,p,hashes):
    actual = copy.deepcopy(value)
    for key in ['invocation','wholeWbsAuditBefore']:actual.pop(key,None)
    assert actual == expected(cfg,source,proof_pin,prior,p,hashes)

def main(cfg,source,normal_pin,proof_pin):
    invocation = capture(__file__);target = out(cfg,cfg.TRACE_NUMBER);assert not target.exists()
    prior,p,hashes,raw,snap = inputs(cfg,source,normal_pin,proof_pin)
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    value = expected(cfg,source,proof_pin,prior,p,hashes);observed = audit();assert observed['actualExit'] == 1 and not observed['passed']
    value.update(invocation=invocation,wholeWbsAuditBefore=observed);validate(value,cfg,source,proof_pin,prior,p,hashes);verify(invocation)
    target.mkdir();data.write(target/'manifest.json',value);print(data.sha((target/'manifest.json').read_bytes()))

def documents(cfg,source,raw,snap):
    target = out(cfg,cfg.TRACE_NUMBER);post = out(cfg,cfg.TRACE_POST_NUMBER);value = json.loads((target/'manifest.json').read_bytes())
    marker = 'previousLiteralBatchPG'+str(cfg.TRACE_NUMBER)+'Reference'
    for name in SECTIONS:
        section = json.loads(raw)[name];assert marker not in section
        section[marker] = {k:copy.deepcopy(section[k]) for k in ['source','manifest','sha256','record','currentAddedTestPaths']}
        section.update(source=source,manifest=str((target/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((target/'manifest.json').read_bytes()),record=cfg.RECORD,currentAddedTestPaths=[])
        if name == SECTIONS[0]:section.update(independentPostManifest=str((post/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None,javaPaths=value['javaPaths'],registered=value['registered'],unregistered=2,main=dict(total=965,registered=965,unregistered=0),test=dict(total=value['totalTest'],registered=value['registeredTest'],unregistered=2))
        else:section.update(guardManifest=str((post/'manifest.json').relative_to(data.ROOT)),guardSha256=None,sourceRows=value['sourceCount'],newLogicalCandidates=value['newLogicalCandidates'],legacyOwnerLabelsDifferingFromCanonical=value['legacyOwnerLabelsDifferingFromCanonical'])
        raw,_,_ = replaced(raw,name,section)
    snap,_,_ = replaced(snap,'inventorySha256',data.sha(raw));return raw,snap

def emit(cfg,source,normal_pin,proof_pin):
    _,_,_,raw,snap = inputs(cfg,source,normal_pin,proof_pin);assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    after,after_snap = documents(cfg,source,raw,snap);patch = '*** Begin Patch\n'
    for name,a,b in [(INV,raw,after),(SNAP,snap,after_snap)]:patch += '*** Update File: '+str(data.ROOT/name)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(a.decode().splitlines(),b.decode().splitlines(),n=0))[2:])+'\n'
    return patch+'*** End Patch\n'

def post(cfg,source,normal_pin,proof_pin):
    invocation = capture(__file__);target = out(cfg,cfg.TRACE_POST_NUMBER);trace = out(cfg,cfg.TRACE_NUMBER);assert not target.exists()
    prior,p,hashes,raw,snap = inputs(cfg,source,normal_pin,proof_pin);value = json.loads((trace/'manifest.json').read_bytes());validate(value,cfg,source,proof_pin,prior,p,hashes)
    actual_raw,actual_snap = (data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes();validate_docs(actual_raw,actual_snap,json.loads(raw),json.loads(snap));assert (actual_raw,actual_snap) == documents(cfg,source,raw,snap)
    path = next(iter(cfg.PATHS));labels = []
    for label,change in [('source',lambda v:v.update(source='0'*40)),('owner',lambda v:next(r for r in v['sourceRows'] if r['path'] == path).update(canonicalOwner='WBS-F03')),
        ('neighbour',lambda v:v['sourceRows'][0].update(sha256='0'*64)),('raw',lambda v:v.update(sourceDerivedRaw=cfg.BEFORE_RAW)),('accepted',lambda v:v.update(newAccepted=1)),
        ('PT',lambda v:v['currentQualification'].update(productTestsExecuted=82)),('coverage',lambda v:v['currentQualification'].update(measuredProductCounters={})),('old-domain',lambda v:v['priorRegistryReference'].update(oldRuntimeDomainsReassigned=True))]:
        bad = copy.deepcopy(value);change(bad);assert json.dumps(bad,sort_keys=True) != json.dumps(value,sort_keys=True)
        try:validate(bad,cfg,source,proof_pin,prior,p,hashes)
        except AssertionError:labels.append(label)
        else:raise AssertionError('invalid PG-only source qualification accepted')
    observed = audit();assert observed['actualExit'] == 1 and not observed['passed'];verify(invocation);target.mkdir()
    data.write(target/'manifest.json',dict(actualExit=0,source=source,invocation=invocation,traceManifestSha256=data.sha((trace/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousLabels=labels,
        oldRegistryRows=len(prior['sourceRows']),currentRegistryRows=len(value['sourceRows']),onlyModifiedSourceHashesChanged=sorted(cfg.PATHS),allOwnersCostsAndOldRuntimePreserved=True,unknownPathsUnchanged=2,wholeWbsAudit=observed,
        inventorySha256=data.sha(actual_raw),snapshotSha256=data.sha(actual_snap),productTestsExecuted=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((target/'manifest.json').read_bytes()))
