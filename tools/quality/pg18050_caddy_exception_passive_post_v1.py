"""Measure one complete fixed exception Source from qualified existing exec; never load Product."""
import json
import os
import shutil
import zipfile
from pathlib import Path
import g07_host_class_provenance_inputs as data
import pg9666_pagination_static as runner
import classfile_code_metadata as code
import jacoco_readonly_exec_subset as execution
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
NAME='dev/codex/schubert/nk/web/security/CaddyRequestRejectedException'
PATH='src/schubert-nk-web/src/main/java/'+NAME+'.java'
PIN='d6c50441cde4887be9a0d9585bb41512ee5228042419b78d48437a1f88620967'
RAW=('PG17880-caddy-address-boundary-six-pt-v1','f4c4d89053c402a449304b947428e2f9203bc86453c90c2db39688f3094c6605')
POST=('PG17882-caddy-address-boundary-six-post-v1','22f6c56e81a6194651e054694fb881c17da3857840e4db491f570d429e5851bb')
INDEPENDENT=('PG17884-caddy-address-boundary-six-independent-v1','2594c867ee5d542223d53feaa3c2caaf0ab99bc378f50f1b67fbb9a9c0f9e51a')
NORMAL=('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg17880-caddy-address-boundary-six-pt-v1'
COMPILE=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1'
OUT=data.BASE/'PG18050-caddy-exception-passive-post-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg18050-caddy-exception-passive-post-v1'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);assert not OUT.exists() and not SLOT.exists()
    raw,p,q,normal=[read(pair) for pair in [RAW,POST,INDEPENDENT,NORMAL]]
    assert all(v['source']==SOURCE and v['actualExit']==0 for v in [raw,p,q,normal])
    assert p['originalManifestSha256']==RAW[1] and q['postSha256']==POST[1]
    assert (p['tests'],p['suites'],p['failures'],p['errors'],p['skipped'])==(6,1,0,0,0)
    assert p['singleSession'] is True and p['crcMismatch']==p['forbiddenProductProbeHits']==0 and all(v[3]=='0' for v in p['passiveNativeBoundaryAbsence']['rows'])
    assert p['execSha256']==raw['execSha256']==data.sha((RUN/'jacoco.exec').read_bytes())
    assert data.sha((RUN/'manifest.safe.json').read_bytes())==RAW[1]
    for file,pin in p['xmlHashes'].items():assert data.sha((data.BASE/POST[0]/file).read_bytes())==pin==data.sha((RUN/'xml'/file).read_bytes())
    test=data.ROOT/'tools/quality/architecture/CaddyAddressBoundaryContractTest.java'
    assert data.sha(test.read_bytes())=='f0612ddb3090a317163f1793408c724796c1ab818fde23b0942192283178c6c0'
    text=test.read_text()
    assert all(s in text for s in ['assertThrows(CaddyRequestRejectedException.class','assertEquals("request proxy is invalid", failure.getMessage())','assertNull(failure.getCause())','assertEquals(0, failure.getSuppressed().length)'])
    assert normal['begin']['inputHashes'][PATH]==PIN==data.sha((data.ROOT/PATH).read_bytes())==data.sha((COMPILE/'snapshot'/PATH).read_bytes())
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        assert {n[:-6] for n in jar.namelist() if n==NAME+'.class' or n.startswith(NAME+'$') and n.endswith('.class')}=={NAME}
        blob=jar.read(NAME+'.class')
    binary=COMPILE/'snapshot/src/schubert-nk-web/target/classes'/(NAME+'.class')
    assert binary.read_bytes()==blob
    decoded=code.decode(blob,NAME+'.class');assert decoded['sourceFile']=='CaddyRequestRejectedException.java' and sum(m['hasCode'] for m in decoded['methods'])==1
    parsed=execution.decode((RUN/'jacoco.exec').read_bytes(),{NAME})
    assert len(parsed['sessions'])==1 and parsed['sessions'][0]['labelBytesHex']==p['sessionIdentity'].encode().hex()
    runtime=read(('PG13378-db-duration-eight-post-recovery-v3','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882'))
    assert all(data.sha(Path(path).read_bytes())==pin for path,pin in runtime['toolAndDependencyHashes'].items())
    receipt=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1/session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    reader=data.ROOT.parent/'pgpt-runs/PG379/pg15713-caddy-public-value-nine-post-v2/diagnostic-classes'
    assert data.sha((reader/'WholeSourceCoverageMeasureV1.class').read_bytes())=='9977e1c733e40e4752261c38e6a679a91cf2d33b6d2be72180e1f67af01a94a3'
    assert data.sha((data.ROOT/'tools/quality/architecture/WholeSourceCoverageMeasureV1.java').read_bytes())=='97cecbbff82e9c93d41f13e94872b792f374f84d34973a930daefb79bb7be260'
    qual=read(('PG15714-caddy-public-value-nine-independent-v1','d3900d79c6dc63338d18804f0b4aaa05fc00e1f88dcbe54451aba898cc565242'))
    assert qual['actualExit']==0 and qual['passiveReaderNegativeChecks']==5
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'component';target=component/(NAME+'.class');target.parent.mkdir(parents=True);shutil.copyfile(binary,target)
    assert data.sha(target.read_bytes())==data.sha(blob)
    stage=runner.step('passive-complete-source',[str(runner.TC/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+receipt['command'][2],'WholeSourceCoverageMeasureV1',str(RUN/'jacoco.exec'),str(component),NAME],SLOT,timeout=120)
    assert stage['actualExit']==0 and not stage['timedOut']
    lines=(SLOT/'passive-complete-source.stdout').read_text().splitlines()
    rows=[line.split(chr(9)) for line in lines if line.startswith('CLASS'+chr(9))]
    assert len(rows)==1 and rows[0][1]==NAME and 'RESULT\t1\t0\t1' in lines
    counters={v.split(':')[0]:dict(missed=int(v.split(':')[1]),covered=int(v.split(':')[2])) for v in rows[0][3:]}
    assert set(counters)=={'LINE','METHOD','CLASS','BRANCH'}
    assert counters['BRANCH']==dict(missed=0,covered=0)
    assert all(counters[k]['covered']>0 and counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS'])
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    owner=dict(sha256=PIN,**canonical(PATH,logical));assert owner['canonicalOwner']==owner['canonicalCostOwner']=='WBS-P015-02'
    assert data.sha((RUN/'jacoco.exec').read_bytes())==p['execSha256'] and data.sha((data.ROOT/PATH).read_bytes())==PIN
    for v in [raw,p,q,normal]:verify(v['invocation'] if 'invocation' in v else v['begin']['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,originalRawReference=list(RAW),originalPostReference=list(POST),originalIndependentReference=list(INDEPENDENT),normalManifestSha256=NORMAL[1],sourceInputSha256=PIN,targetSourceUnits=1,physicalClasses={NAME:data.sha(blob)},sourcePhysicalInventory={NAME:decoded},fullSourceUnits={NAME:dict(physical=[NAME],totals=counters,four100=False,metadataOnly=False,branchNaturallyZero=True,threeCounter100=True)},owners={PATH:owner},execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],crc64=rows[0][2],singleSession=True,crcMismatch=0,allMeasuredApplicableCountersCovered=True,targetUnitFour100=False,strictFour100GateExit=1,productTestsExecuted=0,productTestsReexecuted=0,newTestIds=0,newJunitExecutions=0,newOrdinaryMethods=0,newQualityMethods=0,newProductionFiles=0,priorSourceTransferred=False,coverageExecUnion=False,manualCounterExclusions=[],officialGeneratedFiltersUnchanged=True,forbiddenProductProbeHits=0,originalHeldNativeAuditUnchanged=True,productClassesLoaded=False,productMethodsInvoked=False,passiveCoverageStage=stage,reportedOriginalEnvironment=p['reportedEnvironment'],xmlHashes=p['xmlHashes'],existingOracleTestSha256=data.sha(test.read_bytes()),actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(counters))
if __name__=='__main__':main()
