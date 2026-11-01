"""Metadata-only recovery of successful official analysis; no compiler, JVM or Product replay."""
import copy
import g07_host_class_provenance_inputs as data
import jacoco_readonly_exec_subset as execution
from host_tool_invocation import capture,verify
import pg17853_codefree_official_passive54_v2 as prior
SOURCE=prior.SOURCE
OUT=data.BASE/'PG17854-codefree-official-passive54-recovery-v3'
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only metadata recovery')
    diag=data.read_checked(data.BASE/'PG17842-codefree-main-diagnosis-v1/manifest.json',prior.DIAG)
    begin=data.read_checked(prior.SLOT/'begin.safe.json','2cdb3c42cddb1456e90fd8047dee93301efe9c6cc08be3676941f48d96689b36')
    stage=data.read_checked(prior.SLOT/'official-passive-zero-counters-stage.safe.json','bfac08f24a9e3663d271b1ff493362b64aac2f7257d36eca3f252f3cad60d438')
    raw=data.read_checked(prior.RUN/'manifest.safe.json',prior.RAW)
    require(diag['source']==begin['source']==raw['source']==SOURCE and diag['actualExit']==raw['actualExit']==stage['actualExit']==0 and stage['timedOut'] is False,'exact current successful analyzer, not prior failing helper')
    stdout=prior.SLOT/'official-passive-zero-counters.stdout';stderr=prior.SLOT/'official-passive-zero-counters.stderr'
    require(data.sha(stdout.read_bytes())==stage['stdoutSha256'] and data.sha(stderr.read_bytes())==stage['stderrSha256'] and stderr.read_bytes()==b'','genuine immutable successful analyzer output')
    require(data.sha((prior.RUN/'jacoco.exec').read_bytes())==raw['execSha256']==begin['originalExecSha256'],'original one-source exec')
    parsed=execution.decode((prior.RUN/'jacoco.exec').read_bytes(),set());session=parsed['sessions'][0]
    require(session['labelBytesHex']=='PG17816-ADMISSION-REAL-WAIT-JOINT5'.encode().hex(),'original session label')
    all_physical={n:h for unit in diag['newCodefreeCandidates'].values() for n,h in unit['physical'].items()}
    require(begin['physicalClasses']==all_physical and len(all_physical)==54 and all(data.sha((prior.SLOT/'component'/(n+'.class')).read_bytes())==h for n,h in all_physical.items()),'all 54 original bytes retained; no input class exclusion')
    interfaces={n for n in all_physical if not n.endswith('/package-info')};annotations={}
    require(len(interfaces)==17,'actual measured interface denominator')
    for path,unit in diag['newCodefreeCandidates'].items():
        require(data.sha((data.ROOT/path).read_bytes())==unit['sourceSha256'],'same source definition')
        if not path.endswith('/package-info.java'):continue
        require(len(unit['physical'])==1,'one exact annotation definition')
        n=next(iter(unit['physical']));v=unit['metadata'][n]
        require(n.endswith('/package-info') and v==dict(flags=5632,sourceFile='package-info.java',fields=0,methods=[]),'official compiler package metadata, no executable Code')
        annotations[path]=dict(sourceSha256=unit['sourceSha256'],physical=unit['physical'],flags=5632,fields=0,methods=[],modelCounterStatus='OFFICIAL_PACKAGE_INFO_FILTERED_NO_CODE_NO_RUNTIME_COUNTERS',coverageCountersMeasured=False,productCodeExecuted=False)
    require(len(annotations)==37,'37 non-program definitions')
    expected=['METADATA'+chr(9)+n for n in sorted(interfaces)]+['SESSION'+chr(9)+str(session['startMillis'])+chr(9)+str(session['endMillis']),'RESULT'+chr(9)+'0'+chr(9)+'0'+chr(9)+'1']
    def output_contract(lines):require(lines==expected,'exact metadata inventory and separate original SESSION/RESULT schemas')
    lines=stdout.read_text().splitlines();output_contract(lines)
    variants=[('empty',[]),('missing',lines[1:]),('duplicate',[lines[0],*lines]),('same-count-unknown',['METADATA'+chr(9)+'unknown',*lines[1:]]),('session-time',lines[:-2]+['SESSION'+chr(9)+'0'+chr(9)+'0',lines[-1]]),('nonzero-result',lines[:-1]+['RESULT'+chr(9)+'1'+chr(9)+'0'+chr(9)+'1']),('extra-tag',lines+['UNKNOWN']),('footer-order',lines[:-2]+[lines[-1],lines[-2]])]
    checked=[]
    for label,value in variants:
        require(value!=lines,'nondegenerate '+label)
        try:output_contract(value)
        except ValueError:checked.append(label)
        else:raise ValueError('invalid analyzer output accepted '+label)
    counters={k:dict(covered=0,missed=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    units={u['sourceOuter']:dict(path=p,sourceSha256=u['sourceSha256'],physical=sorted(u['physical']),totals=copy.deepcopy(counters),metadataOnly=True,four100=False,branchNaturallyZero=False,threeCounter100=False) for p,u in diag['newCodefreeCandidates'].items() if not p.endswith('/package-info.java')}
    require(len(units)==17 and set(n for u in units.values() for n in u['physical'])==interfaces,'17 complete interface Source scopes, not 54 programs')
    for value in [diag,begin,raw['begin']]:verify(value['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,diagnosisSha256=prior.DIAG,normalManifestSha256=diag['normalManifestSha256'],originalRawSha256=prior.RAW,originalExecSha256=raw['execSha256'],sessionIdentity='PG17816-ADMISSION-REAL-WAIT-JOINT5',recoveredAnalyzerStage=stage,recoveredAnalyzerStageSha256='bfac08f24a9e3663d271b1ff493362b64aac2f7257d36eca3f252f3cad60d438',recoveredBeginSha256='2cdb3c42cddb1456e90fd8047dee93301efe9c6cc08be3676941f48d96689b36',allInputPhysicalClasses=all_physical,physicalClasses={n:all_physical[n] for n in interfaces},fullSourceUnits=units,metadataClasses=sorted(interfaces),officialPackageInfoDefinitions=annotations,officialPackageInfoDefinitionCount=37,interfaceZeroCounterSourceCount=17,officialFiltersUnchanged=True,officialZeroCounterRows=lines[:-2],originalSessionRow=lines[-2],originalResultRow=lines[-1],outputSchemaNegativeVectors=len(checked),outputSchemaNegativeLabels=checked,allFourCounterTotalsZeroVerified=True,executableCounterExclusions=[],applicableCodeCrcClasses=0,noCodeCrcQualification='NOT_APPLICABLE_NO_EXECUTABLE_CODE_BYTE_IDENTITY_BY_NORMAL_JAR_SNAPSHOT_SHA',tests=0,suites=0,newTestIds=0,productClassesLoaded=False,productTestsExecuted=0,productTestsReexecuted=0,compilerCommandsIssued=0,passiveAnalyzerJvmCommandsIssuedByRecovery=0,existingSuccessfulAnalyzerJvmStagesReused=1,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,registryChanged=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
