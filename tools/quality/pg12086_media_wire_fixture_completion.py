"""Bind actual24, ten measured Main, inverse55, current raw12/context and canonical trace."""
from pathlib import Path
import datetime as dt
import platform
import re
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
from pg9978_plain_core_quality_post import test_classes
from pg9906_user_query_oracle_source_post import jar_classes
from pg11929_storage_fixture_class_metadata import parts,selftest
SOURCE='977214e4409e70bcf7c38dfd34bbaa384fc14c9b'
OUT=data.BASE/'PG12086-media-wire-fixture-completion-v1'
PINS={
 'normal':('PG12074-media-wire-fixture-six-compile-v1','2a15c3279d00cd2509f156e85442ae46124a3f1c5e8ea1b6b9ed0c82e29e81b0'),
 'host':('PG12076-media-wire-fixture-host-v1','1152f7f83f1bd58ef9cabdc8c804ad117241f7ecaa45662c9a17fe4698d3cc2a'),
 'post':('PG12080-media-wire-fixture-post-v1','4cde61f14a32beb2bf8c532ce39c3abfa6b831e64269bf0731254ba0637357cf'),
 'context':('PG12081-media-wire-fixture-context-v1','63dc90ee9d828ff192ca1214fe783fdcab704eae6d7abb3551870f05df532367'),
 'contextPost':('PG12085-media-wire-fixture-context-post-v2','a17a38c49c556574f71ae795b045d7298cda814ecc536ed9017386610106bec0'),
 'trace':('PG12082-media-wire-fixture-trace-v1','d7b6a369b579683c9f0d942978940e375a07703154473aefd346292f3a1132fe'),
 'tracePost':('PG12084-media-wire-fixture-trace-post-v1','fc75550e40e05731e1080aea4e127c1389159bb6e4c49a0774833257c07fce93')}
def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions']==24 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    previous=data.read_checked(data.BASE/'PG12044-api-web-scrape-fixture-six-compile-v1/manifest.json','fe989f6495c165f388cd4cc916da0ea8ed6901420c61d7ada7e2a742f8e6b672')
    assert jar_classes(previous)==jar_classes(normal) and len(jar_classes(normal))==1843
    old,new=test_classes(previous),test_classes(normal);assert set(old)==set(new) and len(new)==1962
    changed=[key for key in old if old[key]!=new[key]];assert len(changed)==7;details=[]
    for role,entry in changed:
        a=parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        b=parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        details.append(dict(module=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    assert {r['sourceFile'] for r in details}=={'ScenarioWireClientTest.java','AnimationWireClientTest.java','MusicWireClientTest.java'}
    vectors=selftest();measure=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])['web']
    counts={kind:dict(missed=sum(u['counters'][kind]['missed'] for u in measure['selectedValueMain'].values()),covered=sum(u['counters'][kind]['covered'] for u in measure['selectedValueMain'].values())) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    assert measure['selectedValueFourCounters100'] and not measure['wholeArtifactCoverage100'] and {k:v['covered'] for k,v in counts.items()}==dict(LINE=120,METHOD=27,CLASS=10,BRANCH=26) and all(c['missed']==0 for c in counts.values())
    static=data.read_checked(data.BASE/'PG12078-media-wire-fixture-static-v1/manifest.json','9677642afbb43a6c36d4a5b8582343054217b99dcfaee948520bc51edbc13e9e');assert static['actualExit']==1 and static['reports']['pmd']['findings']==12
    failed=data.ROOT/'tools/quality/pg12083_media_wire_fixture_context_post.py';assert data.sha(failed.read_bytes())=='683b388c9b68e32ed39f9f6661e0092b1ae38187cdf994472479792b210e4662'
    failure=data.BASE/PINS['contextPost'][0]/'prior-failure.safe.json';f=json.loads(failure.read_bytes());assert f['priorTool']['bodyExit']==1 and not f['platformRefusal'] and f['productTestsReexecuted']==0
    assert v['contextPost']['metadataNegativeVectors']==8 and v['context']['sourceContexts']==12
    inverse=data.read_checked(data.BASE/'PG12072-media-wire-fixture-source-post-v1/manifest.json','30fab96517cd83b06d43ce0eba8f41b5414299198d63c4b01467f9523ed8df8d');assert inverse['metadataNegativeVectors']==55
    run=Path(host['begin']['testCwd']).parent;loadedraw=(run/'classload-metadata.log').read_bytes();assert data.sha(loadedraw)==host['classloadSha256']
    loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',loadedraw.decode()));assert not any(n.startswith(('org.postgresql.','dev.codex.schubert.nk.api.','dev.codex.schubert.nk.web.bootstrap.')) or 'ConnectionFactory' in n for n in loaded)
    assert not list(Path(host['begin']['testCwd']).iterdir());closure=host['begin']['eligibilityClosureSourceHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items())
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2293_三wire二十三是正_製造単体仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2294_三wire二十三是正_製造単体結果.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'code-debug.json',dict(source=SOURCE,rows=details,structuralReaderVectors=vectors,meaningProof='strict original raw inverse55 vectors plus actual24; opaque CP index representation is not standalone semantic proof'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1943','BUG-1944'],relatedYkt=['YKT-1692','YKT-1693'],implementationDecision='PG-D725',tests=host['begin']['cases'],actual=dict(tests=24,suites=3,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainMeasuredCounters=counts,defaultJacocoFilters=True,zeroBranchCountersAreNA=True,noManualExclusions=True,eligibilityClosureSourceHashes=closure,codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),priorToolFailureRecordSha256=data.sha(failure.read_bytes()),failedToolEntryUnchanged=True,allMainClassesUnchanged=1843,otherTestClassesUnchanged=1955,testClassesChanged=7,stringConstants=23,referencesReplaced=213,rawStaticBefore=35,rawStatic=12,rawStaticGateExit=1,actualSecretCount=None,fullArtifactsCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
