"""Complete G01-G06 common-tool subleaf and parent, not actual NK case gates."""
import argparse
import copy
import json
import os
from pathlib import Path

import pg6986_chr_comparison_acceptance as previous

host,PMO,SOURCE=previous.host,previous.PMO,previous.SOURCE
ID='WBS-P020-01.03'
PARENT='WBS-P020-01'
PRIOR=PMO/'492_当commonSource個別受入_比較DIF追加.json'
OUT=host.BASE/'PG6988-chr-gate-parent-acceptance-v1'
REVIEW=host.ROOT/'evidence/01_PT/018_NK-OPS-001/1536_CHR_gate工具契約・親範囲_個別受入matrix.md'


def evidence():
    previous.verify(json.loads(PRIOR.read_bytes()))
    q=json.loads(previous.first.Q.read_bytes())
    names=('GateCliTest','GateContractTest','GateContractValidatorNegativeTest')
    cases=[c for c in q['cases'] if c['clazz'].rsplit('.',1)[-1] in names]
    host.require(len(cases)==36 and all(c['result']=='PASS_ORIGINAL_XML' for c in cases),'genuine original36 shared cases only')
    negative=[c for c in cases if c['clazz'].endswith('.GateContractValidatorNegativeTest')]
    statuses=[c for c in negative if c['method'].startswith('rejectsEveryNonPassExecutionStatus(String)[')]
    host.require(len(negative)==17 and len(statuses)==7,'all actual independent rejected statuses, no skipped credit')
    paths=[p for p in q['sourceInputs'] if p.startswith('program/characterization/src/main/java/')
           or p.startswith('program/characterization/tests/resources/')
           or p.startswith('program/characterization/baseline/current/')
           or any(p.endswith('/'+name+'.java') for name in names)]
    inputs={p:q['sourceInputs'][p] for p in paths}
    host.require(all(host.sha(host.ROOT/p)==h for p,h in inputs.items()),'entire common Main/selected oracle/contract/baseline unchanged')
    contract=json.loads((host.ROOT/'program/characterization/tests/resources/cases/gate-contract.json').read_bytes())
    host.require(contract['gates']==['CHR-G01','CHR-G02','CHR-G03','CHR-G04','CHR-G05','CHR-G06']
                 and len(contract['caseOrder'])==24 and contract['currentApplicableCount']==23
                 and contract['differenceIds']==[f'DIF-{i:03}' for i in range(1,17)]
                 and contract['baselineCommit']=='843de94','approved exact original gate contract, no runtime assertion substitution')
    docs=[*previous.first.DOCS,'documents/100_RD/110_総則・方針/112_スコープ定義.md',
          'documents/100_RD/180_試験・受入要件/181_互換性・受入要件.md']
    for p in docs:host.require(previous.first.old.initial.git('origin/main',p)==(host.ROOT/p).read_bytes(),'actual canonical RD/UI/SS')
    tasks=json.loads((PMO/'481_PGPT詳細WBS.json').read_bytes())['tasks']
    parent=next(t for t in tasks if t['id']==PARENT)
    first=json.loads((previous.first.OUT/'manifest.json').read_bytes())
    host.require(set(parent['ownedArtifacts'])==set(first['componentScopeOverlay']) and len(parent['ownedArtifacts'])==4,'whole declared parent scope, no exclusion')
    related=[r for r in json.loads((PMO/'485_WBS網羅性・受入対応.json').read_bytes())['requirements'] if r['id'] in parent['requirementIds']]
    host.require(len(related)==6 and all(r['owner']==PARENT for r in related),'all six original assigned requirements traced')
    return dict(actualExit=0,source=SOURCE,sourceRun='PG6976-chr-path-green-v1',reviewChecks=[ID+':deliverable',ID+':quality',
                PARENT+':contract',PARENT+':scope',PARENT+':quality'],priorRegister=dict(path=str(PRIOR.relative_to(host.ROOT)),sha256=host.sha(PRIOR)),
                sourceHashes=inputs,sourceCases=cases,canonicalDesigns={p:host.sha(host.ROOT/p) for p in docs},
                originalQualificationSha256=host.sha(previous.first.Q),sharedStaticReviewSha256=host.sha(previous.first.STATIC),
                parentScopeOverlay=first['componentScopeOverlay'],requirementTrace=related,
                semanticReview=dict(path=str(REVIEW.relative_to(host.ROOT)),sha256=host.sha(REVIEW)),
                actualCommonCounter=q['counters'],actualCrcMismatch=q['crcClassMismatch'],actualSessionCount=q['actualSessionCount'],
                newTestExecutions=0,old41Imported=False,oldProduction4222Replayed=False,actualCurrentOrNkCasesExecuted=0,
                actualGateG01toG06NewlyAccepted=False,formalUpdated=False,parentAdditionalBudgetPp=0,acceptance='NOT_APPLIED')


def verify(register):
    prior=json.loads(PRIOR.read_bytes());previous.verify(prior)
    host.require(register['source']==SOURCE and register['reviewState']=='COMPLETE' and register.get('acceptedBy')
                 and register['parentAccepted'] is True and register['newOriginal190Item']==1
                 and register['formalUpdated'] is False and register['wholeEffortCompletionRate'] is None,'one parent only, not global/actual gate acceptance')
    states=register['records']
    host.require(set(states)==set(prior['records'])|{ID,PARENT} and all(states[k]==v for k,v in prior['records'].items()), 'only child03+parent added, old children/needed F02 intact')
    path=host.ROOT/register['witness']['path'];host.require(path==OUT/'manifest.json' and host.sha(path)==register['witness']['sha256'],'original completed parent witness')
    host.require(host.sha(path)=='b5dbbca26d4d36aed003dbff9434e40bde408e2d86b1358037fb1b6013a2cfb2','actual fixed completed parent evidence')
    proof=json.loads(path.read_bytes());host.require(proof['actualExit']==0 and proof['source']==SOURCE
                 and proof['priorRegister']['sha256']==host.sha(PRIOR) and not proof['actualGateG01toG06NewlyAccepted'],'same-source finite actual tool contract')
    host.require(host.sha(host.ROOT/proof['semanticReview']['path'])==proof['semanticReview']['sha256'],'explicit individual full PG/review unchanged')
    for p,h in proof['sourceHashes'].items():host.require(host.sha(host.ROOT/p)==h,'no source/oracle/baseline drift')
    for p,h in proof['canonicalDesigns'].items():host.require(host.sha(host.ROOT/p)==h and previous.first.old.initial.git('origin/main',p)==(host.ROOT/p).read_bytes(),'approved requirements unchanged')
    tasks=json.loads((PMO/'481_PGPT詳細WBS.json').read_bytes())['tasks']+json.loads((PMO/'484_WBSコスト枠・細分化.json').read_bytes())['children']
    for rid in (ID,PARENT):
        task=next(copy.deepcopy(t) for t in tasks if t['id']==rid);task['acceptance']=states[rid]
        previous.first.audit.check_acceptance(task,SOURCE,states)
        host.require(states[rid]['evidence']==[dict(path=str(path.relative_to(host.ROOT)),sha256=host.sha(path),source=SOURCE,
                     run='PG6976-chr-path-green-v1',verifiedChecks=[c['id'] for c in task['acceptanceChecks']])],'every child/parent criterion exactly supported')
    host.require(register['newAcceptedIds']==[previous.first.ID,previous.ID,ID,PARENT]
                 and register['revalidatedDependencyIds']==['WBS-F02'],'do not count F02 or all three children as extra original190 items')
    return dict(actualExit=0,newSubleafThisStage=1,allCommonSubleaves=3,newParentOriginal190Item=1,parentAdditionalBudgetPp=0,
                actualCurrentOrNkCaseExecuted=0,formalUpdated=False,effortPercent=None)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--register',type=Path);args=parser.parse_args()
    if args.register:print(json.dumps(verify(json.loads(args.register.read_bytes()))));return
    value=evidence();os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,originalCaseRefs=36,manifestSha256=host.sha(OUT/'manifest.json'),accepted=0)))


if __name__=='__main__':main()
