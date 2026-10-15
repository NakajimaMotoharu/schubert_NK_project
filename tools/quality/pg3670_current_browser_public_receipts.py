"""Whitelist current Root/Browser/normal-stop/native/retirement receipts; no private payload export."""
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
from pg1446_current_cold_stage import W
from pg3564_current_browser_resume_sources import SOURCE,BOM

ROOT=Path(__file__).resolve().parents[2]
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3670-current-browser-resume-native-retired-v1'
COMMON={'actualExit','productionSource','operatorSource','payloadSha256','startedUTC','completedUTC','formalAccepted'}
RECEIPTS={
 'terminal':('pg3582-current-browser-terminal-v1/manifest.safe.json',{'genuineParentDone','completionCode','completionOutcome','normalUnit0or10','currentManagerGc','managerExitCodeObserved','elapsedSeconds','wholeAccepted'}),
 'rootRows':('pg3584-current-browser-root-rows-v1/manifest.safe.json',{'independentRowsQualified','old24RowsRetained','newSkippedSteps','newProtectedWarningSteps','sameRunProgressUnchanged','newAnonymousHttpLogs','newAnonymousSessions','newSentOutbox','logOutboxOneToOne'}),
 'browser':('pg3580-current-browser-business-actual-v1/manifest.safe.json',{'phaseExits','sourceQualified','sameFourOrdinaryOwnersBeforeAfter','sameSocksBeforeAfter','independentNormalTlsBeforeAfter','sharedCurrentBrowserIgnoreHttpsErrors','browserStandardTrustStoreQualified','plannedCases','passedCases','all24IndependentPost'}),
 'compositeV2':('pg3650-current-browser-composite-full-seal-v2/manifest.safe.json',{'tables','configurationFields','signedArtifacts','currentFourOwnedLive','sqlOracleQualified','businessFullOraclePending','backupManifestRetentionOraclePending','privateBeforeSha256','businessOracle'}),
 'ownedABI':('pg3602-frozen-v1.safe.json',{'genuineParentBeforeSha256','phases','guestMutations0'}),
 'normalStop':('pg3604-stop-v1.safe.json',{'sourceQualified','operatorSourceUnchanged','action','privateLogSha256','starts0','oldFailedNormalized'}),
 'normalStopPost':('pg3606-current-browser-owned-post-v1/manifest.safe.json',{'all24UnchangedTwice','allTenUnitsKernelEmpty','allActorGone','allClientAdvisoryFlock0','whole187SignedArtifactBytesVerified','ownedExplicitStops','eightTerminalReceipts','nativeMetadataStableTwice','nativePhysicalFiles','startsStopsReloadsSqlWrites'}),
 'nativeCatalog':('pg3630-current-browser-native-catalog-v1/manifest.safe.json',{'all28BeforeCopiesPreserved','oldSourceNativeImported','backupPid1GenerationVerified','inspectorPid1GenerationVerified','currentRootOriginalBudgetPreserved','guestWritesStartsStops0'}),
 'nativeQualification':('pg3632-current-browser-native-qualified-v1/manifest.safe.json',{'manifestSha256'}),
 'retireABI':('pg3664-frozen-v1.safe.json',{'genuineParentBeforeSha256','phases','guestMutations0'}),
 'retire':('pg3666-retire-v1.safe.json',{'sourceQualified','operatorSourceUnchanged','action','privateLogSha256','starts0','oldFailedNormalized'}),
 'retirePost':('pg3668-current-browser-runtime-retirement-post-v1/manifest.safe.json',{'all24UnchangedTwice','allTenUnitsKernelEmpty','allActorGone','allClientAdvisoryFlock0','whole187SignedArtifactBytesVerified','normalCurrentRetirementScopesSealed','exactRuntimeEntryRetired','ownedExplicitStops','nativeMetadataStableTwice','nativePhysicalFiles','startsStopsReloadsSqlWrites'}),
}
CASE_FIELDS=[
 {'readOnlyJcaCredentialQualified','passwordResetIssued'},
 {'realChromiumLogins','adminMenuLiteralOrder','secureHttpOnlyLax'},
 {'maximumActive','oldestFreshRevokedReplaced','revokedBrowserDenied'},
 {'adminRead200','noAccountMutation'},{'missingCsrfHttp'},
 {'newlineHttp','businessRowsCreated','samePendingTokenKept'},
 {'submitHttp','exactBusinessRows','escapedHtml','locatorOnlyThreeFields'},
 {'sameTokenSameInputHttp','duplicateBusinessRows','sameReceipt'},
 {'refreshHttp','updateInboxCountUnchanged'},{'notificationHttp','ownerNotificationCount'},
 {'freshSessionsLogoutRevoked','noAdminReset'},
 {'protectedAccountUnchanged','allPriorFourBusinessTablesUnchanged','businessBeforeSha256','sameSourceBeforeAfter'},
]


def sha(raw):return hashlib.sha256(raw).hexdigest()


def case_projection(value,number):
    common={'testId','status','source','timeUTC','formalAccepted','secretsSaved'}
    if set(value)!=common|CASE_FIELDS[number-1]or value['testId']!=f'PT-NBR-{number:03d}'or value['status']!='PASS'or value['source']!=SOURCE or value['formalAccepted']is not False or value['secretsSaved']is not False:
        raise ValueError('exact safe current Browser case schema required')
    for k in CASE_FIELDS[number-1]:
        v=value[k]
        if type(v)not in (bool,int)and not(k=='businessBeforeSha256'and type(v)is str and re.fullmatch('[0-9a-f]{64}',v)):
            raise ValueError('no raw identity or arbitrary string measurement allowed')
    datetime.datetime.fromisoformat(value['timeUTC'].replace('Z','+00:00'))
    return value


def main():
    outputs={};inputs={}
    for name,(relative,fields)in RECEIPTS.items():
        raw=(W/relative).read_bytes();v=json.loads(raw)
        if type(v['actualExit'])is not int or v['actualExit']!=0 or v.get('productionSource',SOURCE)!=SOURCE:
            raise ValueError('actual current receipt required '+name)
        outputs[name]={k:x for k,x in v.items()if k in COMMON|fields};inputs[name]={'privateLogicalSlot':relative,'sha256':sha(raw)}
    n=json.loads((W/RECEIPTS['nativeQualification'][0]).read_bytes())['result']
    if n['currentNativeStreams']!=18 or n['validatedNativePoints']!=20 or n['classByteMismatch']!=0 or n['productionSource']!=SOURCE or n['historicalSourceNativeImported']is not False:
        raise ValueError('two genuine same-source cohorts, not legacy console constants required')
    outputs['nativeQualification']['technical']={k:n[k]for k in ['currentNativeStreams','validatedNativePoints','classByteMismatch','qualified3412Tests','coverage100','gain','moduleCounters','xmlHashes','eligibleCurrentSourceCohorts','historicalSourceNativeImported','exclusionScope']}
    outputs['nativeQualification']['remaining']={k:sum(v[k]['missed']for v in n['moduleCounters'].values())for k in ['LINE','METHOD','CLASS','BRANCH']}
    cases={}
    for number in range(1,13):
        relative=f'pg3580-current-browser-business-actual-v1/cases/PT-NBR-{number:03d}.safe.json';raw=(W/relative).read_bytes()
        name=f'PT-NBR-{number:03d}';cases[name]=case_projection(json.loads(raw),number);inputs[name]={'privateLogicalSlot':relative,'sha256':sha(raw)}
    PUBLIC.mkdir(parents=True)
    for name,value in {**outputs,**cases}.items():
        with(PUBLIC/(name+'.json')).open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
    files={p.name:sha(p.read_bytes())for p in PUBLIC.iterdir()if p.is_file()}
    manifest={'actualExit':0,'productionSource':SOURCE,'BOM':BOM,'operatorHead':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':inputs,'files':files,'testIds':['PT-PG3582-TERMINAL','PT-PG3584-ROWS','PT-PG3586-ROOT-SEAL','PT-PG3650-COMPOSITE','PT-PG3600-OWNED','PT-NATIVE-3630','PT-NATIVE-3632','PT-PG3662-CONTRACT','PT-PG3666-RETIRE','PT-PG3668-POST',*cases],
              'failed3592And3644Preserved':True,'nativeInitialConsole9_10PreservedAndCorrectedFromActual18_20':True,'rawDB_FD_Native_Session_CredentialExported':False,'formalTests':1964,'formalScopes':53,'individualAccepted':17,'individualTotal':190,'effortCompletionRate':None,'fullCharacterizationGate':False,'QA051final':'HELD','global100':False,'F03Accepted':False,'formalAccepted':False}
    with(PUBLIC/'manifest.json').open('x')as f:json.dump(manifest,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'actualExit':0,'publicManifest':str((PUBLIC/'manifest.json').relative_to(ROOT)),'sha256':sha((PUBLIC/'manifest.json').read_bytes()),'safeFiles':len(files),'formalUpdated':False}));return 0


if __name__=='__main__':raise SystemExit(main())
