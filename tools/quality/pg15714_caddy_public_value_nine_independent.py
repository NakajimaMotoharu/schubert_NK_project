"""Independent literal Caddy/inode values and whole-source zero-coverage denominator proof."""
import copy
import ipaddress
import json
import re
import shutil
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
import pg15710_caddy_public_value_nine_pt as original
import pg15713_caddy_public_value_nine_post as post
import pg9666_pagination_static as runner
PIN='a4071f345cd9644059a81c721ada4ab5c4f5f8cc257d690e40a57b1f479990c6'
OUT=data.BASE/'PG15714-caddy-public-value-nine-independent-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg15714-caddy-public-value-nine-independent-v1'
P=original.PREFIX
CLOSURES={P+n:sorted(P+v for v in group) for n,group in original.CLOSURES.items()}
META={P+'file/EnvironmentInodePolicy$Source'}
UNEXECUTED={P+'file/EnvironmentInodePolicy$Snapshot'}
PHYSICAL=set().union(*map(set,CLOSURES.values()))
CODE=PHYSICAL-META
def require(ok,label):
    if not ok:raise ValueError(label)
def wire(v):return json.dumps(v,sort_keys=True)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/raw')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(9,3,9,3),'actual original9/three')
    require(all(type(p[k]) is int and p[k]==0 for k in ['actualExit','failures','errors','skipped','reruns','newTestIds','newAccepted','crcMismatch','actualJdbcMethodsInvoked','actualSqlStatementsPreparedOrExecuted','unselectedOriginalGoldenHelperMethodsExecuted']),'true integer zero roles')
    require(len({(c['classname'],c['name']) for c in p['cases']})==9 and all(c['result']=='PASS' for c in p['cases']),'all actual distinct passes')
    require(p['sessionIdentity']==original.SESSION and p['singleSession'] is True and p['execSha256']==raw['execSha256'],'one original current session')
    require(p['completeSourceUnitClosure']==CLOSURES and set(p['physicalClasses'])==set(p['sourcePhysicalInventory'])==PHYSICAL and set(p['executable'])==CODE and set(p['fullSourceUnits'])==set(CLOSURES),'full physical denominator')
    require(set(p['metadataClasses'])==META and p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'NoCode not exclusion')
    m=p['sourcePhysicalInventory'][next(iter(META))]
    require(m['sha256']=='6eac51c687c3f26434fab657166e47cb63fbb3af7bd280d822c1772439b9b5e2' and m['flags']==1536 and m['methods']==[dict(name=n,descriptor=d,flags=1025,hasCode=False,codeLength=0) for n,d in [('attributes','(Ljava/nio/file/Path;)Ljava/util/Map;'),('filesystem','(Ljava/nio/file/Path;)Ljava/lang/String;')]],'two exact abstract methods')
    totals={k:{r:sum(v['counters'][k][r] for v in p['executable'].values()) for r in ['covered','missed']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={k:dict(covered=c,missed=m) for k,c,m in [('LINE',61,147),('METHOD',11,30),('CLASS',3,1),('BRANCH',64,148)]},'independent whole sums including unexecuted class')
    require(set(p['unexecutedCodeClasses'])==UNEXECUTED and p['unexecutedCodeIncludedInAllDenominators'] is True,'zero Code remains denominator')
    for n in UNEXECUTED:
        require(any(v['hasCode'] for v in p['sourcePhysicalInventory'][n]['methods']) and p['executable'][n]['counters']=={k:dict(covered=0,missed=m) for k,m in [('LINE',11),('METHOD',3),('CLASS',1),('BRANCH',22)]},'actual unexecuted Code not metadata or covered')
    for n,group in CLOSURES.items():
        u=p['fullSourceUnits'][n]
        expected={k:{r:sum(p['executable'][v]['counters'][k][r] for v in group if v in CODE) for r in ['covered','missed']} for k in totals}
        require(u['physical']==group and u['totals']==expected and u['four100'] is False and u['threeCounter100'] is False and u['branchNaturallyZero'] is False,'two honest whole-source gaps')
    require(p['strictFour100GateExit']==1 and p['targetUnitFour100'] is p['allMeasuredApplicableCountersCovered'] is False,'no false four100')
    require(p['onlyReviewedPureValueSuites'] is p['numericIpv6LiteralParsingOnly'] is True and p['onlyPreSqlZeroJdbcCallContracts'] is p['actualDnsRequestsIssued'] is p['actualJdbcBackendConnected'] is p['actualJdbcProxyObjectsConstructed'] is False,'pure literals not permissions or backend')
    require(p['cryptoOperationKind']=='NONE_IN_REVIEWED_DOMAIN_BODY' and all(p[k] is False for k in ['cryptoOrKeyOperationsInvoked','publicSyntheticTestKeysUsed','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','actualPrivateFilesOpened','actualBrokerOrListenerStarted','rootMainInvoked','formalUpdated','whole451Accepted','wholeF03Accepted','oldCoverageTransferred','priorProductResultsReused']),'no live/private/formal transfer')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualServiceActions','actualNetworkActions','actualBrowserActions','actualBoundSockets','actualJmsConnectionsCreated','actualJmsContextsCreated','forbiddenProductProbeHits','productTestsReexecutedByPost']) and p['effortPercent'] is None,'no target operations')
    require(p['unselectedOriginalGoldenHelperMethods']==3 and p['unselectedOriginalGoldenHelperMethodsExecuted']==0 and p['passiveCoverageReaderSourceSha256']=='97cecbbff82e9c93d41f13e94872b792f374f84d34973a930daefb79bb7be260','unchanged Golden compile-only and explicit reader')
    require(len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(v[3]=='0' for v in p['passiveNativeBoundaryAbsence']['rows']) and all(v['actualExit']==0 and not v['timedOut'] for v in p['stages']),'genuine passive results')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    wanted={str(p.relative_to(data.ROOT)) for p in [*original.TESTS.values(),original.GOLDEN_SOURCE]}|{'src/schubert-nk-batch/src/main/java/'+n+'.java' for n in CLOSURES}
    require(set(p['owners'])==wanted and all(row['sha256']==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()) for path,row in p['owners'].items()),'actual owners all six source paths')
    require(sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==2 and sum(v['ownershipStatus']=='UNKNOWN' for v in p['owners'].values())==4,'two Main baseline/four Test UNKNOWN including helper')
def main():
    global raw
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG15710-caddy-public-value-nine-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    old=data.read_checked(data.BASE/'PG15701-current1995-media-scenario-registry-v2/manifest.json','27a79dcda15f57f41c45673c203a6e3127547a4b1be72d3d1058843ce71bf5d0')
    require(not set(CLOSURES)&set(old['fullSourceUnits']),'new two Source, no old reacceptance')
    expected=set()
    for name,path in original.TESTS.items():
        text=path.read_text();methods=re.findall(r'(?m)^  void ([A-Za-z0-9_]+)\(',text);require(len(methods)==original.COUNTS[name],'whole originals')
        expected.update(('dev.codex.schubert.nk.batch.file.'+name,v) for v in methods)
        require(not any(v in text for v in ['Files.','ProcessBuilder','RootStartupContext','FixedServiceIdentity','LinuxHostDirectoryCalls','SSLContext','KeyStore','CertificateFactory','DriverManager','getConnection(','HttpClient','Runtime.getRuntime','System.getenv(']),'no live/authority call in selected originals')
    require(expected=={(c['classname'],c['name']) for c in p['cases']} and not expected&{(c['classname'],c['name']) for c in old['cases']},'all9 new and no original Golden3 execution')
    texts={name:path.read_text() for name,path in original.TESTS.items()}
    require(all(v in texts['CaddyPublicCaMetadataTest'] for v in ['0100600, 0100640, 0100644','1, 631, 65536','0, 040700, 0120600, 0100400','65537','Long.MAX_VALUE','requireFileMetadata(null']),'independent CA boundary matrix')
    require(all(v in texts['CaddyPublicMetadataTest'] for v in ['040700, 040750, 040755','Long.MAX_VALUE, Long.MAX_VALUE','requireNoAccessAcl(null)','assertArrayEquals(new byte[] {1, 2, 3}, acl)']),'independent directory/identity/ACL matrix')
    uri={v:'https://'+('['+v+']' if ':' in v else v)+':55160/login' for v in ['0.0.0.0','::']}
    require(str(ipaddress.ip_address('0.0.0.0'))=='0.0.0.0' and str(ipaddress.ip_address('::'))=='::' and all(v in texts['CaddyAddressBoundaryTest'] for v in uri.values()),'independent numeric IP URI values')
    for mode in [0o100600,0o100640,0o100644]:
        require(mode&0o170000==0o100000 and mode&0o777 in [0o600,0o640,0o644],'POSIX independent regular file mode')
    design='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'
    design_bytes=(data.ROOT/design).read_bytes();require(design_bytes==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved SS exact')
    require(all(v in design_bytes.decode() for v in ['root:caddy0640','directory0700/0750/0755','証明書0600/0640/0644・single-link・上限64KiB','literal IPv4又はbracket付きIPv6','55160']),'approved independent mode/IP profile')
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('tests','tests',10),('suites','suites',2),('cases','cases',[]),('units','fullSourceUnits',{}),('physical','physicalClasses',{}),('metadata','metadataClasses',[]),('executable','executable',{}),('totals','totals',{}),('unexecuted','unexecutedCodeClasses',[]),('zero-denominator','unexecutedCodeIncludedInAllDenominators',False),('exclude','manualCounterExclusions',['X']),('filter','officialGeneratedFiltersUnchanged',False),('crc','crcMismatch',1),('session','sessionIdentity','OLD'),('single','singleSession',False),('strict','strictFour100GateExit',0),('four','targetUnitFour100',True),('crypto','cryptoOrKeyOperationsInvoked',True),('keys','actualSecretKeysLoaded',True),('credential','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('files','actualFilesOpenedByProduct',True),('dns','actualDnsRequestsIssued',True),('jdbc','actualJdbcMethodsInvoked',1),('root','rootMainInvoked',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('union','oldCoverageTransferred',True),('accepted','newAccepted',1),('bool-zero','newAccepted',False),('effort','effortPercent',100),('helper-exec','unselectedOriginalGoldenHelperMethodsExecuted',1),('owners','owners',{}),('reader','passiveCoverageReaderSourceSha256','0'*64),('helper-count','unselectedOriginalGoldenHelperMethods',2)]
    labels=[]
    for label,key,value in vectors:
        require(wire(p[key])!=wire(value),'nondegenerate '+label);bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false Caddy qualification '+label)
    SLOT.mkdir();runner.SLOT=SLOT
    coverage=next(v for v in p['stages'] if 'WholeSourceCoverageMeasureV1' in v['command']);base=coverage['command'];declarations=base[6:]
    require(base[3]=='WholeSourceCoverageMeasureV1' and len(declarations)==5,'exact passive reader argv')
    variants={
      'undeclared-unexecuted':([v.replace('--unexecuted=','') for v in declarations],'undeclared unexecuted Code class'),
      'executed-as-unexecuted':([('--unexecuted='+v if v==P+'file/CaddyPublicConfiguration' else v) for v in declarations],'observed class declared unexecuted'),
      'code-as-metadata':([v.replace('--unexecuted=','--metadata=') for v in declarations],'executable declared as metadata'),
      'duplicate-declaration':([*declarations,declarations[0]],'duplicate expected class or metadata')}
    stages=[]
    for label,(args,needle) in variants.items():
        stage=runner.step(label,[*base[:6],*args],SLOT,timeout=120);require(stage['actualExit']==1 and not stage['timedOut'] and needle in (SLOT/(label+'.stderr')).read_text(),'specific reader rejection '+label);stages.append(stage)
    crc=SLOT/'crc-fixture';shutil.copytree(post.SLOT/'component',crc)
    path=crc/(P+'file/CaddyPublicConfiguration.class');content=path.read_bytes();old_text=b'Caddy TLS admission unavailable';require(content.count(old_text)==1,'one passive CRC literal');path.write_bytes(content.replace(old_text,b'Caddy TLS admission unavailablE'))
    command=[*base[:5],str(crc),*declarations]
    stage=runner.step('crc-mismatch',command,SLOT,timeout=120);require(stage['actualExit']==1 and not stage['timedOut'] and 'CRC mismatch' in (SLOT/'crc-mismatch.stderr').read_text(),'true mutated class CRC rejection');stages.append(stage)
    require(all(data.sha((post.SLOT/'diagnostic-classes'/n).read_bytes())==h for n,h in [('WholeSourceCoverageMeasureV1.class',p['passiveCoverageReaderClassSha256'])]),'reader class unchanged')
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=9,suites=3,sourcePrograms=2,newSourcePrograms=2,physicalClasses=5,executablePhysicalClasses=4,metadataPhysicalClasses=1,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=2,baselineMainOwnerRows=2,unknownTestOwnerRows=4,semanticNegativeVectors=len(labels),negativeLabels=labels,passiveReaderNegativeChecks=len(stages),passiveReaderNegativeStages=stages,unexecutedCodeClasses=sorted(UNEXECUTED),unexecutedCodeIncludedInAllDenominators=True,unselectedOriginalHelperMethods=3,unselectedOriginalHelperMethodsExecuted=0,independentIpValues=uri,approvedDesignHashes={design:data.sha(design_bytes)},cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,actualDnsRequestsIssued=False,actualJdbcMethodsInvoked=0,actualSqlStatementsPreparedOrExecuted=0,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,semanticNegativeVectors=len(labels),passiveReaderNegativeChecks=len(stages),productTestsExecuted=0)))
if __name__=='__main__':main()
