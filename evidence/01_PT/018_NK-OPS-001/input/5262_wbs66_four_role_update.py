"""Bind the upcoming four-role handoff to the current authorized evidence and preserved gaps."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

DOC=Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117')
E=Path('evidence/01_PT/018_NK-OPS-001/evidence')
TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/ArtemisStartupEvidenceValueTest.java'


def git(*args):
    return subprocess.check_output(['git',*args],timeout=30)


def pin(p):
    return dict(path=str(p),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())


def read(loc):
    return json.loads(Path(loc).read_bytes())


def main():
    start=read(next(DOC.glob('563_*')))
    data=start['values']
    core=data['productionCoreMain']
    head=data['source']
    assert all(git('rev-parse',name).decode().strip()==head for name in ('HEAD','origin/dev-foundation'))
    pins=data['oracleReferences']
    assert all(pin(row['path'])==row for row in pins)
    preceding, runtime, jars, pmd, source_lint, value, chr_l01, native_tool=(read(row['path']) for row in pins)
    assert jars['sourceCore']==pmd['source']==source_lint['source']==value['sourceCore']==core
    assert git('diff','--name-only',source_lint['testSource'],head,'--','src').decode().splitlines()==[TEST]
    assert {k:v['verifiedClasses'] for k,v in jars['jars'].items()}==dict(protocol=176,storage=79,bootstrap=201,batch=646)
    assert jars['modelNodes']==309 and jars['physicalEdges']==17867
    assert pmd['rawFindingCount']==61 and pmd['reviewedSiteCount']==33 and pmd['unclassified']==pmd['applicable']==0
    assert value['firstDynamicSuccess']==value['firstDynamicTotal']==3 and value['pmdApplicable']==0
    assert chr_l01['tests']==182 and chr_l01['actualL01'] is False and native_tool['actualNativeStreams']==0
    at_base=preceding['historicalSsc447']
    assert (at_base['success'],at_base['failed'],at_base['errors'],at_base['skipped'],at_base['notRun'])==(152,0,0,0,0)
    assert at_base['rawMiss']==dict(L=4,M=4,C=0,B=58,I=85)
    assert preceding['officialAccepted']==17 and preceding['officialAll']==190 and preceding['netIncrease']==0
    assert preceding['priorityFiveAccepted']==0 and preceding['priorityFiveCriteria']==25
    assert preceding['shortTermDistinct']==11 and preceding['directCriteria']==59
    templates=runtime['c02']['verifiedTemplateHashes']
    assert len(templates)==14 and not runtime['c02']['activeRuntimeConfirmed']
    assert all(hashlib.sha256(git('show',f'{core}:{name}')).hexdigest()==h for name,h in templates.items())
    assert runtime['f04']['previousActualExit']==255 and runtime['f04']['previousAuthBodyDidNotRun']
    local_free=shutil.disk_usage(Path.cwd()).free
    result=dict(actualExit=0,run=data['run'],startEvent=start['eventId'],sourceCore=core,head=head,
         officialAcceptance=17,officialDenominator=190,formalPT=1964,formalScopes=53,net=0,
         primaryFive=0,primaryFiveCriteria=25,uniqueShortTerms=11,allShortCriteria=59,completedOriginalRowPrice=0,
         ssc447=at_base,newProductTrials=0,externalContacts=0,externalReceipt=None,publishedRoles=['F02','F03','C02','F04'],
         f02=dict(realJars=4,physical=1102,resolvedModel=309,typedEdges=17867,totalModules=6,
                  needed=['same current API/Web build and typed boundary','Expiry held dependency','same-source runtime and 451']),
         f03=dict(nonHeldMain=source_lint['eligibleMain'],allMain=source_lint['allMain'],
                  nonHeldTest=source_lint['eligibleTest']+1,allTest=source_lint['allTest']+1,
                  newTestProof=pin(pins[5]['path']),separateSourceOnlyReceipts=source_lint['eligibleTest'],
                  newRawBatch61=61,newReviewedBatchSites=33,newBatchApplicable=0,
                  needed=['whole-six typed analysis','protected Main4/Test32 and Root11','former applicable/unclassified PMD','same-source 451']),
         c02=dict(currentTemplates=14,actualUnit=False,need=runtime['c02']['need']),
         f04=dict(lastOriginalExit=255,lastActorStarted=False,need=runtime['f04']['remaining']),
         supportingLocal=dict(nkL01=False,actualNativeStreams=0,comparisonUnitTests=182,localAvailableBytes=local_free,
                            gateNormalMinimumBytes=20*1024**3),
         effortPercent=None,formalUpdated=False,qualifiedEvidence=pins,verifier=pin(Path(__file__)),
         terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out=E/data['run']
    out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(pin(out/'manifest.json'))


if __name__=='__main__':
    main()
