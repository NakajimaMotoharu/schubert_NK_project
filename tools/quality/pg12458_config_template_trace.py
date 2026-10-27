"""One reviewed C06 Test source hash update and exact host-only public-template qualification."""
import copy
import difflib
import json
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced
from pg9338_wbs_reference_metadata_post import validate
from pg10420_role_code_trace import INV, SNAP, SECTIONS
from trace_owner_join import join_rows, validate as validate_join

SOURCE = 'd6c01d3aed6bd1b546b6f5989fe80705e6e1262f'
OUT = data.BASE/'PG12458-config-template-trace-v1'
POST = data.BASE/'PG12460-config-template-trace-post-v1'

def inputs():
    prior = data.read_checked(data.BASE/'PG12418-batch-runtime-trace-v1/manifest.json','e216153b1e7151ef811c19aa839e1d3aa6f4b0f74bd0ea929d199bed94bbc85f')
    proof = data.read_checked(data.BASE/'PG12456-config-template-post-v1/manifest.json','5ee8066c74ce84a6f02c82a96fb3685dc47f56d91fbfb3a05634931c430ed429')
    plan = data.read_checked(data.BASE/'PG12446-config-template-plan-v1/manifest.json','3ccd10cea379621ccbe31b03ea8faa0aed9844013b648ac199447d41ca446d95')
    normal = data.read_checked(data.BASE/'PG12450-config-template-six-compile-v1/manifest.json','face6e2196f8345f8ba51f4e1d29ff10df42231737e801e109d8f0e32b6d43f2')
    assert proof['source'] == normal['source'] == SOURCE and proof['actualExit'] == normal['actualExit'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert all(normal['begin']['inputHashes'][r['path']] == r['sha256'] for r in plan['sourceChanges'])
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    return prior,proof,plan,raw,snap

def expected(prior,proof,plan,raw):
    value = copy.deepcopy(prior)
    for key in ('actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore'):
        value.pop(key,None)
    changes = {r['path']:r for r in plan['sourceChanges']};bindings = []
    for row in value['sourceRows']:
        if row['path'] not in changes:
            continue
        item = changes[row['path']]
        assert row['sha256'] == item['beforeSha256'] and row['owner'] == row['canonicalOwner'] == row['canonicalCostOwner'] == 'WBS-C06'
        row['sha256'] = item['sha256']
        bindings.append(dict(path=row['path'],beforeSha256=item['beforeSha256'],sha256=item['sha256'],canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner']))
    assert len(bindings) == 1 and len(value['sourceRows']) == 983
    logical = {r['path']:r for r in json.loads(raw)['artifacts']}
    owner_input = [dict(path=r['path'],sha256=r['sha256'],owner=r['canonicalOwner']) for r in bindings]
    hashes = {r['path']:r['sha256'] for r in bindings}
    joined = join_rows(owner_input,logical,hashes,'WBS-F03');validate_join(joined,owner_input,logical,hashes,'WBS-F03')
    assert joined[0]['canonicalOwner'] == joined[0]['canonicalCostOwner'] == 'WBS-C06'
    assert joined[0]['ownershipStatus'] == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED'
    value.update(source=SOURCE,oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,
        currentPublicTemplateFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,originalLogicalJoin=joined,stringConstants=6,literalReferences=30,fieldRenames=1,fieldReferences=2,independentInverseNegativeVectors=22,additionalSharedCostPp=0,oldRuntimeReassigned=False),
        currentPublicTemplateHostQualification=dict(source=SOURCE,proofManifestSha256='5ee8066c74ce84a6f02c82a96fb3685dc47f56d91fbfb3a05634931c430ed429',originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=4,newProductTestIds=0,suites=1,failures=0,errors=0,skipped=0,aborted=0,publicResourceCount=7,publicResourceNegativeVectors=proof['publicResourceNegativeVectors'],executedTestCrc64=proof['artifactMeasurements']['batch']['executedTestCrc64'],measurementSha256=proof['measurementSha256'],productMainExecuted=False,mainCoverageQualification='NOT_APPLICABLE_NO_PRODUCT_MAIN_EXECUTED',wholeArtifactsCoverage100=False,rawStatic=0,whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    assert all(value[k] == v for k,v in prior.items() if k not in ('actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore','source','sourceRows','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged'))
    return value

def documents(raw,snap):
    for name in SECTIONS:
        section = json.loads(raw)[name];assert 'previousPublicTemplateRegistryReference' not in section
        section['previousPublicTemplateRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2337_公開設定Template七指摘_製造単体結果.md',currentAddedTestPaths=[])
        section['currentPublicTemplateBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentPublicTemplateFixtureBinding',qualification='SOURCE_BOUND_7_SAMEVALUE_FIXES_INVERSE22_ORIGINAL4_PUBLIC_RESOURCES7_NO_MAIN_EXECUTION')
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None)
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None)
        raw,_,_ = replaced(raw,name,section)
    snap,_,_ = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap

def main():
    invocation = capture(__file__);assert not OUT.exists();prior,proof,plan,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    before = audit();assert before['actualExit'] == 1
    value = expected(prior,proof,plan,raw);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,wholeWbsAuditBefore=before,**value));print(data.sha((OUT/'manifest.json').read_bytes()))

def emit():
    _,_,_,raw,snap = inputs();assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    after,after_snap = documents(raw,snap);patch = '*** Begin Patch\n'
    for name,a,b in ((INV,raw,after),(SNAP,snap,after_snap)):
        patch += '*** Update File: '+str(data.ROOT/name)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(a.decode().splitlines(),b.decode().splitlines(),n=0))[2:])+'\n'
    return patch+'*** End Patch\n'

def post():
    invocation = capture(__file__);assert not POST.exists();prior,proof,plan,raw,snap = inputs()
    reference = expected(prior,proof,plan,raw);value = json.loads((OUT/'manifest.json').read_bytes())
    def require(candidate):
        if any(candidate.get(k) != v for k,v in reference.items()):
            raise ValueError('exact C06 owner/source and host-only public template qualification required')
    require(value);after,after_snap = documents(raw,snap)
    assert (data.ROOT/INV).read_bytes() == after and (data.ROOT/SNAP).read_bytes() == after_snap
    validate(after,after_snap,json.loads(raw),json.loads(snap));labels = []
    for key,wrong in [('canonicalOwner','WBS-F03'),('canonicalCostOwner','WBS-F02'),('sha256','0'*64)]:
        bad = copy.deepcopy(reference);row = bad['currentPublicTemplateFixtureBinding']['sourceChanges'][0]
        assert row[key] != wrong;row[key] = wrong
        try:
            require(bad)
        except ValueError:
            labels.append(key)
        else:
            raise AssertionError('invalid source/owner metadata accepted')
    for key,wrong in [('observedTestExecutions',3),('productMainExecuted',True),('oldExecUnion',True)]:
        bad = copy.deepcopy(reference);row = bad['currentPublicTemplateHostQualification']
        assert row[key] != wrong;row[key] = wrong
        try:
            require(bad)
        except ValueError:
            labels.append(key)
        else:
            raise AssertionError('invalid qualification accepted')
    observed = audit();assert observed['actualExit'] == 1 and observed['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(after_snap),oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,coverage=None,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:];main()
