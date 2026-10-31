"""Independent whole33 source/oracle join; distinguish injected cycle from actual Root recovery."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16618_morning_pure_data_original_33_pt as original
POST=('PG16620-morning-pure-data-original-33-post-v1','a878d423f42737c284f3f7aa6cea59619e0da023340a532f5d3f24e93f3e2424')
RAW=('PG16618-morning-pure-data-original-33-pt-v1','08cd21226f463fd65536544f19ab0a1d07d8ec567c3b1a6001368454215f2665')
PREV=('PG16608-current2282-application-unit-registry-v1','2474e9273df26df9b0d3af9822dbe6ebb927429ef9e1f0b72b9543b2d6b9576e')
PLAN=('PG16617-morning-static-review-equivalence-v1','b7589a46ea931fd4ad14e553453d8501eb8d5a790ececcfe31f74761bd124d15')
OUT=data.BASE/'PG16622-morning-pure-data-original-33-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old,plan=[read(v) for v in [POST,RAW,PREV,PLAN]]
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old,plan]),'same genuine current source')
    require(plan['reuseKind']=='UNCHANGED_STATIC_REVIEW_INPUTS_NOT_RUNTIME_RESULTS' and plan['priorProductResultsTransferred'] is False and len(plan['changedPathsOutsideReviewedBatchCallTree'])==3,'reuse only unchanged static review')
    expected=set();texts={}
    for name,path in original.TESTS.items():
        blob=path.read_bytes();text=blob.decode();texts[name]=text
        require(data.sha(blob)==original.PINS[name]==raw['begin']['testSourceHashes'][str(path)],'whole original Test pin')
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==original.COUNTS[name],'all original whole methods')
        expected.update(('dev.codex.schubert.nk.batch.file.'+name,m) for m in methods)
    require(len(expected)==33 and not expected&{(v['classname'],v['name']) for v in old['cases']},'33 fresh unique current methods')
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    names={v[0] for v in expected};require(expected=={(v['className'],v['method']) for v in bindings if v['className'] in names},'all normal ordinary declarations')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML hash');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==33 and set(actual)==expected,'all 33 actual original cases')
    oracle_groups={
      'MorningPrestartEvidenceTest':['assertArrayEquals(golden, encoded.getBytes(StandardCharsets.US_ASCII))','issuer-prestart-','expected = stream.readAllBytes()','issstep006DigestNullAndUnknownFailureNeverBecomeGateSuccess'],
      'MorningCompletionEvidenceTest':['parent455001BackupFailureIsWarningNotAnAbsoluteGate','parent540001BackupOutcomeRequiresTheActualStatusAndFixedFailureReason','parent540004ExpiryMustBelongToTheSameRunEvenWhenAllTerminalValuesAreValid','MorningCompletionEvidence[actual=<redacted>]'],
      'StoppedBackupCompletionTest':['stopcomp003CompletedCycleAndExactReceiptCannotBeSubstituted','assertSame(stopped.cycle, f.backupCycle())','assertSame(stopped.receipt, f.backupReceipt())','"stopped-readback"'],
      'MorningCompletionChecksTest':['assertEquals(4, txCalls.get())','assertEquals(22, peers.get())','assertEquals(52, local.get())','assertSame(failure, assertThrows(IOException.class, owner::check))'],
      'MorningBackupObservedCompletionTest':['assertEquals(1, archive.get())','assertEquals(0, db.calls)','"2026-09-30T03:30:01.123456Z"','mmain010NullClockReverseIoAndUnknownCannotBecomeSuccessfulCompletion'],
      'MorningCompletionRetirementTest':['assertEquals(EXPECTED, events)','"unlink:CADDY"','"unlink:WEB"','"unlink:API"','"api-held"','before.verify()','after.verify()']}
    require(all(all(token in texts[name] for token in tokens) for name,tokens in oracle_groups.items()),'independent full-byte/typed rows/identity/TX/event/time oracles')
    require(all(not any(token in t for token in ['new BatchDatabaseFixture','DriverManager','ProcessBuilder','MorningProcessMain.main(','MorningProcessMain.runCompleted(','RootFailedStartRecovery']) for t in texts.values()),'only original injected memory ports, no Root/main/backend operation')
    root='dev/codex/schubert/nk/batch/file/'
    def counter(m,c):return dict(missed=m,covered=c)
    def counts(l,m,c,b):return {k:counter(*v) for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],[l,m,c,b])}
    totals=counts((381,330),(38,41),(1,6),(84,156))
    units={
      root+'MorningPrestartEvidence':counts((0,166),(0,12),(0,1),(0,66)),
      root+'MorningCompletionEvidence':counts((0,97),(0,15),(0,1),(0,86)),
      root+'MorningCompletionChecks':counts((0,14),(0,5),(0,1),(0,0)),
      root+'MorningStartupLaunchOwner':counts((381,53),(38,9),(1,3),(84,4))}
    fields=dict(actualExit=0,source=original.SOURCE,originalManifestSha256=RAW[1],tests=33,suites=6,newTestIds=0,cases=raw['cases'],targetSourceUnits=4,completeSourceUnitClosure={n:sorted(v) for n,v in original.CLOSURES.items()},metadataClasses=sorted(original.METADATA),unexecutedCodeClasses=[root+'MorningStartupLaunchOwner$Started'],totals=totals,strictFour100GateExit=1,targetUnitFour100=False,allMeasuredApplicableCountersCovered=False,singleSession=True,crcMismatch=0,manualCounterExclusions=[],cryptoOrKeyOperationsInvoked=True,publicDigestOnly=True,actualSecretKeysLoaded=False,actualJdbcBackendConnected=False,actualSqlStatementsPreparedOrExecuted=0,actualJmsConnectionsCreated=0,actualRootRecoveryOperations=0,actualFilesOpenedByProduct=False,actualPermitIssueSignPublishOrRetire=False,wholePrior27AbsenceClaimed=False,approvedInjectedBackupCycleOnly=True,syntheticArchiveAndRetirementCallbacksInvoked=True,formalUpdated=False,whole451Accepted=False,oldCoverageTransferred=False,effortPercent=None)
    physical=set().union(*[set(v) for v in original.CLOSURES.values()])
    def contract(v):
        require(all(k in v and type(v[k]) is type(expected_value) and v[k]==expected_value for k,expected_value in fields.items()),'independent typed source/run/counter/effect contract')
        require(set(v['physicalClasses'])==physical and set(v['executable'])==physical-original.METADATA and set(v['fullSourceUnits'])==set(units),'all physical/Source denominators')
        require(all(v['fullSourceUnits'][n]['totals']==expected_counts for n,expected_counts in units.items()),'exact independent unit counters including parent misses')
        require(sum(u['four100'] for u in v['fullSourceUnits'].values())==2 and sum(u['branchNaturallyZero'] and u['threeCounter100'] for u in v['fullSourceUnits'].values())==1,'two four100 and one natural-zero not four')
        failed=v['rootRecoveryProbeAudit'];require(len(failed)==5 and all(n.startswith(root+'RootFailedStartRecovery') and not r['recordPresent'] and r['trueProbeHits']==0 for n,r in failed.items()),'all five actual recovery class records absent')
        cycle=v['syntheticBackupCycleProbeAudit'];require(len(cycle)==23 and any(r['trueProbeHits']>0 for r in cycle.values()) and all(n.startswith('dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle') for n in cycle),'disclose allowed injected cycle, no false global absence')
        inactive=v['reviewedInactiveBoundaryAudit'];require(len(inactive)==5 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in inactive.values()),'DB fixture/native/root outer unexecuted')
        native=v['passiveNativeBoundaryAbsence'];require('rows' in native and len(native['rows'])==6 and all(row[3]=='0' for row in native['rows']) and v['forbiddenProductProbeHits']==0,'held/native probes absent')
    contract(p);labels=[]
    for key,value in fields.items():
        bad=copy.deepcopy(p)
        if type(value) is bool:bad[key]=not value
        elif type(value) is int:bad[key]=value+1
        elif isinstance(value,str):bad[key]='BAD'
        elif value is None:bad[key]=100
        elif isinstance(value,list):bad[key]=['BAD']
        else:bad[key]={}
        require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false claim accepted '+key)
    for key in ['physicalClasses','executable','fullSourceUnits','rootRecoveryProbeAudit','syntheticBackupCycleProbeAudit','reviewedInactiveBoundaryAudit','passiveNativeBoundaryAbsence']:
        bad=copy.deepcopy(p);bad[key]={}
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('erased physical or boundary metadata accepted')
    design={}
    for number in ['341','342','343']:
        paths=list((data.ROOT/'documents/300_SS').glob('*/'+number+'_*.md'));require(len(paths)==1,'unique approved SS')
        relative=str(paths[0].relative_to(data.ROOT));blob=paths[0].read_bytes();require(blob==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved SS bytes');design[relative]=data.sha(blob)
    for path,pin in original.FIXTURES.items():require(data.sha((data.ROOT/path).read_bytes())==pin,'independent fixed golden file bytes')
    for row in [p,old,plan]:verify(row['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],staticReviewEquivalenceSha256=PLAN[1],tests=33,suites=6,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(oracle_groups),independentOracleGroups=oracle_groups,approvedDesignHashes=design,independentGoldenFileHashes=original.FIXTURES,newSourcePrograms=4,newPhysicalClasses=13,metadataPhysicalClasses=6,four100SourceProgramsMeasured=2,naturalZeroBranchSourceProgramsMeasured=1,partialSourceProgramsMeasured=1,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('negative',len(labels),'oracle',len(oracle_groups))
if __name__=='__main__':main()
