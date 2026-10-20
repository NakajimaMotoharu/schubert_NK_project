"""Refresh existing943 candidate from genuine current4034; historical941/17 and all costs immutable."""
import argparse
import copy
import inspect
import json
import pg6102_current_support_trace as base

ROOT,PMO,NAMES,W,BASE=base.ROOT,base.PMO,base.NAMES,base.W,base.BASE
SOURCE='97dd2ba6185143632439f32dfc1d663061f1e55c'
OUT=W/'pg6258-current4034-trace-v1'
PUBLIC=BASE/'PG6258-current4034-host-measurement-v1'
require,sha,trace,audit=base.require,base.sha,base.trace,base.audit


def read_qualified():
    qp=BASE/'PG6244-current4034-cases/qualification.json';cp=qp.with_name('cases.json')
    receipt=json.loads((W/'pg6250-original4034-artifacts-v2/manifest.safe.json').read_bytes())
    originalpath=W/'pg6244-confirmed-rollback-six-v1/manifest.safe.json';original=json.loads(originalpath.read_bytes())
    require(receipt['actualExit']==original['actualExit']==0 and receipt['source']==original['source']==SOURCE
        and receipt['wholeReplayed']is False and receipt['originalManifestSha256']==sha(originalpath.read_bytes())
        and receipt['publicQualificationSha256']==sha(qp.read_bytes())and receipt['publicCasesSha256']==sha(cp.read_bytes()),
        'genuine original4034 receipt and immutable returned artifacts, not begin or prior successful run')
    q=json.loads(qp.read_bytes())
    require(q['actualExit']==q['FESFlakyNotRun']==q['staticSixModules']==0 and q['productionSource']==SOURCE
        and(q['tests'],q['suites'],q['mainClasses'])==(4034,606,1667)
        and q['currentOriginalXmlQualified']is True and q['returnedOriginalTerminalExact']is True,
        'exact same-source original4034 qualification')
    return qp,q


def definitions(qsha,csha):
    scope={**vars(base),'SOURCE':SOURCE,'OUT':OUT,'PUBLIC':PUBLIC,'QSHA':qsha,'CSHA':csha,
        'read_qualified':read_qualified,'candidates':candidates}
    for name in ('measurement','publish','stage','apply','report'):
        raw=inspect.getsource(getattr(base,name))
        raw=raw.replace('PG6088-six-v1','PG6244-six-v1').replace('tests=3985, suites=595','tests=4034, suites=606')
        raw=raw.replace('PG6102-current943-trace-v1','PG6258-current943-trace-v1')
        if name=='report':
            raw=raw.replace('physicalSupportAdditions=2,','physicalSupportAdditions=2,physicalSupportAdditionsThisUpdate=0,')
        exec(compile(raw,'<current4034 '+name+'>','exec'),scope)
    return scope


def authenticated():
    qp,_=read_qualified()
    return definitions(sha(qp.read_bytes()),sha(qp.with_name('cases.json').read_bytes()))


def measurement():return authenticated()['measurement']()


def candidates(texts,before_head):
    inventory,snapshot=[json.loads(texts[n],object_pairs_hook=audit.unique_object)for n in NAMES[2:]]
    previous=inventory['currentPhysicalCandidate'];old=inventory['artifacts']
    require(previous['version']==2 and len(old)==941 and len(previous['artifacts'])==943
        and previous['source']=='870010d6681d74519237be7a7ca6381a190f471a',
        'only saved prior943 host-only candidate, never overwrite a later candidate')
    oldblob=trace.git_artifacts(before_head,['documents/400_PGPT/470_PMO/'+NAMES[2]])['documents/400_PGPT/470_PMO/'+NAMES[2]]
    require(oldblob==texts[NAMES[2]].encode(),'previous candidate/history preserved in immutable metadata commit')
    measured=measurement();require(json.loads((PUBLIC/'manifest.json').read_bytes())==measured,'exact current original4034 measurement')
    candidate=copy.deepcopy(previous);blobs=trace.git_artifacts(SOURCE,[a['path']for a in candidate['artifacts']])
    for artifact in candidate['artifacts']:
        artifact['sha256']=sha(blobs[artifact['path']])
        require(artifact['acceptance']=='UNASSESSED','physical refresh cannot import leaf acceptance')
    candidate.update(source=SOURCE,measurement=dict(path=(PUBLIC/'manifest.json').relative_to(ROOT).as_posix(),
        sha256=sha((PUBLIC/'manifest.json').read_bytes())))
    proposal=copy.deepcopy(inventory);proposal['currentPhysicalCandidate']=candidate
    observed=trace.verify_candidate(proposal)
    history=list(inventory.get('currentPhysicalCandidateHistory',[]))
    history.append(dict(source=previous['source'],metadataSource=before_head,inventoryPath='documents/400_PGPT/470_PMO/'+NAMES[2],
        inventorySha256=sha(texts[NAMES[2]].encode()),candidateSha256=trace.descriptor_digest(previous),
        measurement=previous['measurement'],preservedNotImported=True))
    first=base.rewrite_root(texts[NAMES[2]],dict(currentPhysicalCandidate=candidate,currentPhysicalCandidateHistory=history,
        currentCandidateAssessmentHead=before_head,
        artifactHashMeaning='Historical941/source/17acceptance immutable. Existing current943 refreshed only to actual same-source original4034 host-only bytes/counters. Two implementation supports were already present; this update adds0 artifacts/fees/acceptances. Native/global100/F03/formal remain pending; effortnull.'))
    second=base.rewrite_root(texts[NAMES[3]],dict(inventorySha256=sha(first.encode()),currentPhysicalCandidateMeasurement=observed,
        candidateInventoryMeaning='Historical941/17/formal/cost fields unchanged. Existing943 uses original4034 host-only coverage; current support additions0. Prior native/candidate success not imported; effortnull.'))
    require(json.loads(first)['artifacts']==old,'historical artifacts immutable')
    current=json.loads(second)
    require(all(current[k]==snapshot[k]for k in ('rows','counts','source','measurementRun','formal','wholeEffortCompletionRate')),
        'historical rows/acceptance/formal/effort immutable')
    return {**texts,NAMES[2]:first,NAMES[3]:second},observed


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['publish','stage','apply','report'])
    args=parser.parse_args();authenticated()[args.action]()
