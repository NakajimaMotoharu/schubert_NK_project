"""Close comparison subleaf against explicit PG oracle review, no test replay."""
import argparse
import copy
import json
import os
from pathlib import Path

import pg6984_chr_adapter_acceptance as first

host,PMO,SOURCE=first.host,first.old.PMO,first.SOURCE
PRIOR=PMO/'491_当commonSource個別受入_adapter・必要F02.json'
ID='WBS-P020-01.02'
OUT=host.BASE/'PG6986-chr-comparison-acceptance-v1'
REVIEW=host.ROOT/'evidence/01_PT/018_NK-OPS-001/1534_CHR比較・DIF_個別PG受入matrix.md'
METHODS=('acceptsTwentyFourPassCasesAndExactlySixteenApprovedDifferences','rejectsNullMissingAndWrongInputTypesWithoutNpe',
         'reportsCatalogArtifactStatusSetSymlinkAndUnregisteredDrift','rejectsMalformedObservationEnvelope',
         'rejectsUnknownOutOfScopeBroadWrongOverlappingAndUnusedObservations')


def prior_register():
    value=json.loads(PRIOR.read_bytes());first.verify(value);return value


def evidence():
    prior_register()
    q=json.loads(first.Q.read_bytes())
    paths=['program/characterization/src/main/java/dev/codex/schubert/characterization/ArtifactComparator.java',
           'program/characterization/tests/java/dev/codex/schubert/characterization/ArtifactComparatorTest.java',
           *['program/characterization/tests/resources/cases/'+p for p in ('catalog.json','dif-allowlist.json')]]
    hashes={p:host.sha(host.ROOT/p) for p in paths}
    host.require(all(q['sourceInputs'][p]==h for p,h in hashes.items()),'full current Main/Test/fixture equals original44')
    cases=[c for c in q['cases'] if c['clazz']=='dev.codex.schubert.characterization.ArtifactComparatorTest']
    host.require(len(cases)==5 and {c['method'] for c in cases}==set(METHODS)
                 and all(c['result']=='PASS_ORIGINAL_XML' for c in cases),'five exact actual independent cases, not more declarations')
    allow=json.loads((host.ROOT/paths[-1]).read_bytes())
    rules=allow['differences']
    host.require([r['id'] for r in rules]==[f'DIF-{i:03}' for i in range(1,17)]
                 and all(r['mode'] in ('difference','required','contract') and r['cases'] and r['selectors']
                         and '*' not in r['field'] and all('*' not in v for v in r['selectors']) for r in rules), 'exact narrow declared16DIF')
    host.require(rules[0]['cases']==['CHR-A01','CHR-U01','CHR-U02'],'approved QA045 login scope preserved')
    return dict(actualExit=0,source=SOURCE,sourceRun='PG6976-chr-path-green-v1',priorRegister=dict(path=str(PRIOR.relative_to(host.ROOT)),sha256=host.sha(PRIOR)),
                inputHashes=hashes,originalCases=cases,independentOracleReview=dict(path=str(REVIEW.relative_to(host.ROOT)),sha256=host.sha(REVIEW)),
                originalQualificationSha256=host.sha(first.Q),sharedQualityReference=first.STATIC.relative_to(host.ROOT).as_posix(),
                targetPhysicalClasses={k:v for k,v in q['physicalClasses'].items() if 'ArtifactComparator' in k},
                exactDifRules=rules,newPtExecuted=0,original44Repeated=False,realNkCasesExecuted=0,formalUpdated=False,acceptance='NOT_APPLIED')


def verify(register):
    previous=prior_register();states=register['records']
    host.require(register['source']==SOURCE and register['reviewState']=='COMPLETE' and register.get('acceptedBy')
                 and register['parentAccepted'] is False and register['newOriginal190Item']==0
                 and register['formalUpdated'] is False and register['wholeEffortCompletionRate'] is None,'explicit subleaf source/quality boundary')
    host.require(set(states)==set(previous['records'])|{ID} and all(states[k]==v for k,v in previous['records'].items()), 'only new child02, prior source/dependencies intact')
    path=host.ROOT/register['witness']['path'];host.require(path==OUT/'manifest.json' and host.sha(path)==register['witness']['sha256'],'exact witness')
    host.require(host.sha(path)=='bc707bdcd14572c9801a68bfda9bae2531f32d3152d65585d5f58ca4b947f2ee','actual completed bounded original witness')
    proof=json.loads(path.read_bytes());host.require(proof['source']==SOURCE and proof['actualExit']==0
                 and proof['acceptance']=='NOT_APPLIED' and proof['priorRegister']['sha256']==host.sha(PRIOR), 'genuine completed PG original evidence binding')
    review=proof['independentOracleReview'];host.require(host.sha(host.ROOT/review['path'])==review['sha256'],'explicit independent review unchanged')
    host.require(all(host.sha(host.ROOT/p)==h for p,h in proof['inputHashes'].items()), 'no target byte drift')
    task=next(copy.deepcopy(t) for t in json.loads((PMO/'484_WBSコスト枠・細分化.json').read_bytes())['children'] if t['id']==ID)
    task['acceptance']=states[ID];first.audit.check_acceptance(task,SOURCE,states)
    checks=[c['id'] for c in task['acceptanceChecks']]
    host.require(states[ID]['evidence']==[dict(path=str(path.relative_to(host.ROOT)),sha256=host.sha(path),source=SOURCE,
                 run='PG6976-chr-path-green-v1',verifiedChecks=checks)]
                 and register['newAcceptedIds']==[first.ID,ID] and register['revalidatedDependencyIds']==['WBS-F02'], 'exact criterion proof, no double reauthentication/new parent')
    return dict(actualExit=0,newSubleafThisStage=1,newSubleavesAtCommonSource=2,parentAccepted=False,newOriginal190Item=0,testsReplayed=0,formalUpdated=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--register',type=Path);args=parser.parse_args()
    if args.register:print(json.dumps(verify(json.loads(args.register.read_bytes()))));return
    value=evidence();os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,manifestSha256=host.sha(OUT/'manifest.json'),fiveOriginalCases=5,newAccepted=0)))


if __name__=='__main__':main()
