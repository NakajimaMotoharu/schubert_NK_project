"""API-Web scrape fixture current28 and source owner/cost binding; whole quality remains HOLD."""
import copy
import difflib
import json
from pathlib import Path
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced
from pg9338_wbs_reference_metadata_post import validate
from pg10420_role_code_trace import INV, SNAP, SECTIONS

SOURCE = '913eedbc22a42fa077c2c408baa7d63f7004abc3'
BASE = '6bad2ef19'
OUT = data.BASE/'PG12052-api-web-scrape-fixture-trace-v1'
POST = data.BASE/'PG12054-api-web-scrape-fixture-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG12024-web-business-record-trace-v1/manifest.json',
        'b20e91c8e05ae52ab6df7f34ed93053b7d05f324659e75e6987d7fc3c7fbc167')
    proof = data.read_checked(data.BASE/'PG12050-api-web-scrape-fixture-post-v1/manifest.json',
        '4babe5c4dc240cfb62fcd375acfeb59f6558ecc0d95c353ff534ad4b57cd1204')
    plan = data.read_checked(data.BASE/'PG12040-api-web-scrape-fixture-plan-v1/manifest.json',
        '63a2eee4ac2062bb33b61922403de8c798b95160a1bf1efac0b53e5b2f82c173')
    normal = data.read_checked(data.BASE/'PG12044-api-web-scrape-fixture-six-compile-v1/manifest.json',
        'fe989f6495c165f388cd4cc916da0ea8ed6901420c61d7ada7e2a742f8e6b672')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG12053-api-web-scrape-fixture-context-v2/manifest.json','8a1d76ee89e42839efa9b827a5c563825fec0bb04537ba46b8d89b3546c113a0')
    context_post=data.read_checked(data.BASE/'PG12051-api-web-scrape-fixture-context-post-v1/manifest.json','7b1c08141fbb4e9b6880db84fdf123d954067fb837530eb5c9e2d54fc8f741d7')
    assert context['source']==context_post['source']==SOURCE and context['actualExit']==context_post['actualExit']==0
    old = [subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    return prior,proof,plan,old


def expected(prior,proof,plan):
    value=copy.deepcopy(prior)
    for key in ('actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore'):value.pop(key,None)
    changed={r['path']:r for r in plan['sourceChanges']};bindings=[]
    for row in value['sourceRows']:
        if row['path'] not in changed:continue
        item=changed[row['path']];assert row['sha256']==item['beforeSha256'] and row['canonicalOwner']==row['canonicalCostOwner']==row['owner'];row['sha256']=item['sha256'];bindings.append(dict(path=row['path'],beforeSha256=item['beforeSha256'],sha256=item['sha256'],canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner']))
    assert len(bindings)==2 and len(value['sourceRows'])==983 and {r['canonicalOwner'] for r in bindings}=={'WBS-P018-09'} and value['registered']==1808 and len(value['unregisteredJavaPaths'])==2
    value.update(source=SOURCE,oldRowsChangedShaOnly=2,allOtherPriorRowsUnchanged=981,
        currentApiWebScrapeFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=21,literalReferences=162,orderConstants=1,comparisonReferences=2,constants={r['path']:r['constants'] for r in plan['sourceChanges']},independentInverseNegativeVectors=53,allMainClassesUnchanged=1843,additionalSharedCostPp=0,oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentApiWebScrapeFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='4babe5c4dc240cfb62fcd375acfeb59f6558ecc0d95c353ff534ad4b57cd1204',originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=28,uniqueMethods=28,newProductTestIds=0,suites=2,failures=0,errors=0,skipped=0,aborted=0,completeApiMainClasses=467,completeWebMainClasses=358,measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsFourCounters100=False,selectedValueMainClasses=2,selectedValueFourCounters100=True,selectedValueMeasured=dict(LINE=21,METHOD=4,CLASS=2,BRANCH=6),selectedValueMissed=dict(LINE=0,METHOD=0,CLASS=0,BRANCH=0),rawStatic=5,sourceLocalContexts=5,unclassifiedRaw=0,contextManifestSha256='8a1d76ee89e42839efa9b827a5c563825fec0bb04537ba46b8d89b3546c113a0',contextPostManifestSha256='7b1c08141fbb4e9b6880db84fdf123d954067fb837530eb5c9e2d54fc8f741d7',whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys={'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'};assert all(value[k]==v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousApiWebScrapeFixtureRegistryReference' not in section
        section['previousApiWebScrapeFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2291_APIWeb_scrape二十三是正_製造単体結果.md',currentAddedTestPaths=[])
        section['currentApiWebScrapeFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentApiWebScrapeFixtureBinding',
            qualification='SOURCE_BOUND_21_STRINGS_162_REFS_COUNTER_IF2_ORIGINAL28_DIRECT_POLICY2_21L4M2C6B_MISS0_RAW5_CONTEXT_FULL_API_WEB_NOT100')
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None)
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None)
        raw,before,after = replaced(raw,name,section)
        pairs.append((before,after))
    snap,before,after = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap,pairs,[(before,after)]


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior,proof,plan,(raw,snap) = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    observed = audit()
    assert observed['actualExit'] == 1
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,wholeWbsAuditBefore=observed,**expected(prior,proof,plan)))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    _,_,_,(raw,snap) = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    after,asnap,_,_ = documents(raw,snap)
    patch = '*** Begin Patch\n'
    for name,before,result in ((INV,raw,after),(SNAP,snap,asnap)):
        patch += '*** Update File: '+str(data.ROOT/name)+'\n'
        lines = list(difflib.unified_diff(before.decode().splitlines(),result.decode().splitlines(),n=0))[2:]
        patch += '\n'.join('@@' if line.startswith('@@') else line for line in lines)+'\n'
    return patch+'*** End Patch\n'


def contract(value,reference):
    if any(value.get(k) != v for k,v in reference.items()):
        raise ValueError('exact source/owner/cost/runtime metadata required')


def post():
    invocation = capture(Path(__file__))
    assert not POST.exists()
    # No applicability review claim: the measured8 warnings retain explicit source contexts and current whole pending.
    prior,proof,plan,(raw,snap) = inputs()
    value = json.loads((OUT/'manifest.json').read_bytes())
    reference = expected(prior,proof,plan)
    contract(value,reference)
    after,asnap,_,_ = documents(raw,snap)
    assert (data.ROOT/INV).read_bytes() == after and (data.ROOT/SNAP).read_bytes() == asnap
    validate(after,asnap,json.loads(raw),json.loads(snap))
    bads = []
    for field,v in [('canonicalOwner','WBS-G13.07'),('canonicalCostOwner','WBS-F03'),('sha256','0'*64)]:
        bad = copy.deepcopy(reference)
        bad['currentApiWebScrapeFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',24),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentApiWebScrapeFixtureRuntimeQualification'][field] = v
        bads.append(bad)
    for bad in bads:
        try:
            contract(bad,reference)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid source/owner/cost/runtime metadata accepted')
    observed = audit()
    assert observed['actualExit'] == 1 and observed['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),
        metadataNegativeVectors=len(bads),registered=1808,javaPaths=1810,unknown=2,oldRowsChangedShaOnly=2,
        allOtherPriorRowsUnchanged=981,originalBudgetAndAcceptanceUnchanged=True,oldRuntimeReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
