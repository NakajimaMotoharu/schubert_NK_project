"""Read-only current six-report capsule; no old-source relabel or acceptance changes."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import types
import pg3280_wbs_current_source as previous
import wbs_progress_audit as audit
from pg3798_hygiene_current_observer import SOURCE
from pg1446_current_cold_stage import W

ROOT=Path(__file__).resolve().parents[2];PMO=ROOT/'documents/400_PGPT/470_PMO'
OUT=W/'pg3912-current-wbs-measurement-v1'
PUBLIC=Path('evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3912-current-wbs-measurement-v1')
REMOTE='/home/mini/schubert-nk-pgpt/runs/PG3892-native-v1'
MODULES=previous.MODULES;COUNTERS=previous.COUNTERS


def sha(raw):return hashlib.sha256(raw).hexdigest()


def require(value,message):
    if not value:raise ValueError(message)


def historical_artifacts(inventory):
    paths=[a['path']for a in inventory['artifacts']]
    require(len(paths)==len(set(paths))==941,'exact canonical941 ownership paths')
    require(not subprocess.check_output(['git','diff',SOURCE,'HEAD','--',*paths]),'all actual artifacts identical to qualified source')
    request=''.join(inventory['source']+':'+p+'\n'for p in paths).encode()
    process=subprocess.run(['git','cat-file','--batch'],input=request,capture_output=True,check=True)
    raw=process.stdout;offset=0;changes=[]
    for item in inventory['artifacts']:
        end=raw.index(b'\n',offset);header=raw[offset:end].split();require(len(header)==3 and header[1]==b'blob','actual historical Git blob required');size=int(header[2]);offset=end+1
        old=raw[offset:offset+size];offset+=size;require(raw[offset:offset+1]==b'\n','bounded Git blob delimiter');offset+=1
        require(sha(old)==item['sha256'],'historical inventory really matched old source')
        current=(ROOT/item['path']).read_bytes()
        if sha(current)!=item['sha256']:changes.append({'path':item['path'],'owner':item['owner'],'oldSha256':item['sha256'],'newSha256':sha(current)})
    require(offset==len(raw),'all and only historical941 blobs consumed')
    return changes


def runtime_proofs():
    definitions={
      'parent':('pg3858-current-resume-terminal-v1',['genuineParentDone','genuinePid1StartDone','genuineRootDone','newActivationSameRunCutoff','normalUnit0or10']),
      'full':('pg3870-current-resume-composite-full-seal-v1',['currentFourOwnedLive','sqlOracleQualified']),
      'browser':('pg3866-current-resume-browser-actual-v1',['sameFourOrdinaryOwnersBeforeAfter','all24IndependentPost']),
      'stop':('pg3882-current-resume-owned-post-v1',['all24UnchangedTwice','allActorGone','allClientAdvisoryFlock0','allTenUnitsKernelEmpty','whole187SignedArtifactBytesVerified','normalCurrentOwnedStopScopesSealed']),
      'retired':('pg3908-current-runtime-retirement-post-v1',['all24UnchangedTwice','allActorGone','allClientAdvisoryFlock0','allTenUnitsKernelEmpty','whole187SignedArtifactBytesVerified','normalCurrentRetirementScopesSealed','exactRuntimeEntryRetired'])}
    result={}
    for label,(slot,flags)in definitions.items():
        path=W/slot/'manifest.safe.json';v=json.loads(path.read_bytes());require(type(v['actualExit'])is int and v['actualExit']==0 and v['productionSource']==SOURCE and all(v[k]is True for k in flags),'actual current complete runtime stage')
        value={'source':SOURCE,'run':slot,'receiptSha256':sha(path.read_bytes()),'actualExit':0,'verifiedFlags':flags,'currentLiveAuthority':False}
        if label=='parent':require(v['completionCode']==10 and 0<v['elapsedSeconds']<1800,'genuine original-budget WARNING10');value.update(completionCode=10,completionOutcome='WARNING',elapsedSeconds=v['elapsedSeconds'],managerExitCodeObserved=v['managerExitCodeObserved'])
        if label=='full':require(v['signedArtifacts']==187,'signed actual187');value['signedArtifacts']=187
        if label=='browser':
            require(v['passedCases']==v['plannedCases']==12 and v['independentNormalTlsBeforeAfter']['normalChainAndIpSanValidated'],'actual12 and independent TLS');value.update(finiteBrowserCases=12,independentOwnedTls=True,browserStandardTrustStoreQualified=False,fullChrA01=False)
        result[label]=value
    return result


def main():
    require(not subprocess.check_output(['git','status','--porcelain']),'clean fixed measurement reader')
    full=json.loads((W/'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes());native=json.loads((W/'pg3892-current-two-cohort-native-v1/manifest.safe.json').read_bytes());f=full['result'];n=native['result']
    require(full['actualExit']==native['actualExit']==0 and f['productionSource']==n['productionSource']==SOURCE,'actual same-source authorities')
    require((f['tests'],f['suites'],f['mainClasses'],f['FESFlakyNotRun'],f['staticSixModules'])==(3714,545,1643,0,0),'genuine current3714 full authority')
    require(n['qualified3734Tests']==3714 and n['currentNativeStreams']==18 and n['validatedNativePoints']==20 and n['classByteMismatch']==0 and not n['oldNativeImported']and not n['historicalSourceNativeImported'],'current physical CRC/session only')
    require(set(f['modules'])==set(n['xmlHashes'])==set(n['moduleCounters'])==set(MODULES),'all6 exact current modules')
    require(sum(m['tests']for m in f['modules'].values())==3714,'all3714 actual module counts')
    inventory=json.loads((PMO/'485_WBS網羅性・受入対応.json').read_bytes());changes=historical_artifacts(inventory);require(len(changes)==260,'actual hygiene260, no scope addition')
    try:before={'passed':True,'result':audit.verify()}
    except ValueError as error:before={'passed':False,'error':str(error),'reason':'Old4856 physical inventory deliberately fails on newly qualified7fff artifacts; not a passing audit.'}
    runtime=runtime_proofs();os.umask(0o077);OUT.mkdir();rawdir=OUT/'raw';rawdir.mkdir()
    old_hashes={name:sha((PMO/name).read_bytes())for name in ['481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json','485_WBS網羅性・受入対応.json','486_WBS現行実績.json']}
    (OUT/'before-audit.safe.json').write_text(json.dumps(before,sort_keys=True));(OUT/'all260-artifact-changes.safe.json').write_text(json.dumps(changes,sort_keys=True))
    fetch=types.FunctionType(previous.fetch_fixed.__code__,{**previous.__dict__,'REMOTE':REMOTE})
    fetch('manifest.safe.json',rawdir/'manifest.safe.json');require(sha((rawdir/'manifest.safe.json').read_bytes())==native['manifestSha256']and json.loads((rawdir/'manifest.safe.json').read_bytes())==n,'exact immutable native authority/result')
    projections={}
    for module in MODULES:
        path=rawdir/(module+'-union.xml');fetch(path.name,path);raw=path.read_bytes();require(sha(raw)==n['xmlHashes'][module],'exact current XML bytes');projections[module]=previous.redact_report(raw,n['moduleCounters'][module])
    target=ROOT/PUBLIC;target.mkdir();modules=[]
    for module,(raw,redaction)in projections.items():
        path=target/'coverage'/module/'site/jacoco/jacoco.xml';path.parent.mkdir(parents=True);path.write_bytes(raw)
        modules.append({'module':module,'coverageXmlSha256':sha(raw),'rawCoverageXmlSha256':n['xmlHashes'][module],'pt':f['modules'][module],'redaction':redaction})
    value={'actualExit':0,'productionSource':SOURCE,'run':'PG3912-current-wbs-measurement-v1','kind':'SAME_BYTE_HOST_NATIVE_WBS_MEASUREMENT_NOT_ACCEPTANCE','FES':0,'staticIssues':0,'staticIssuesScope':'Compiler/NullAway/SpotBugs six modules only; F03 explicitly NOT_ACCEPTED/raw1840/technical278/unclassified1562','F03Accepted':False,'sourceSnapshot':f['sourceSnapshot'],'tests':3714,'suites':545,'mainClasses':1643,'coverageRoot':str(PUBLIC/'coverage'),'modules':modules,'moduleCounters':n['moduleCounters'],'fullPrivateReceiptSha256':sha((W/'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes()),'nativePrivateReceiptSha256':sha((W/'pg3892-current-two-cohort-native-v1/manifest.safe.json').read_bytes()),'originalNativeManifestSha256':native['manifestSha256'],'nativeStreams':18,'nativePoints':20,'beforeFileHashes':old_hashes,'beforeSource':inventory['source'],'beforeBinding':inventory['measurementBindings'],'all941ArtifactsQualifiedSource':True,'all941ArtifactChanges':260,'artifactChanges':changes,'semanticCoverageContentChanged':False,'runtimeStageProofs':runtime,'runtimeVerifiedRows':['WBS-N05','WBS-N06','WBS-N07','WBS-N08','WBS-N09','WBS-N10','WBS-N14'],'runtimeProofIsPartialStageNotLeafAcceptance':True,'unmappedHistoricalRuntimeRequiresRecheck':['WBS-N11','WBS-N12','WBS-N13','WBS-CHR-A01'],'scopeChanged':False,'acceptedLeafDelta':0,'formalAccepted':False,'effortPercent':None,'secretsSaved':False,'vmActions':0,'mavenReissued':False,'beforeAudit':before,'stagedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    raw=(json.dumps(value,ensure_ascii=False,sort_keys=True)+'\n').encode();(target/'manifest.json').write_bytes(raw)
    (OUT/'manifest.safe.json').write_text(json.dumps({'actualExit':0,'publicManifest':str(PUBLIC/'manifest.json'),'publicManifestSha256':sha(raw),'beforeFileHashes':old_hashes,'sourceBindingApplied':False,'acceptedLeafDelta':0},sort_keys=True))
    print(json.dumps({'actualExit':0,'modules':6,'source':SOURCE,'artifactChanges':260,'beforeAuditPassed':before['passed'],'acceptedLeafDelta':0,'manifestSha256':sha(raw)}));return 0


if __name__=='__main__':raise SystemExit(main())
