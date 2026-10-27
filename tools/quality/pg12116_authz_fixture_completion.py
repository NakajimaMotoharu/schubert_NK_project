"""Bind actual4 MockServlet, measured factory branch0 NA, inverse24, current raw3/context and canonical trace."""
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
SOURCE='ee82637a750105243ddeac665c61d27a781e5cf1'
OUT=data.BASE/'PG12116-authz-fixture-completion-v1'
PINS={'normal': ('PG12104-authz-fixture-six-compile-v1', '1cffddad23dd78451013a1bb325a7e84682d733fb80d57f3205279d12d9774f9'), 'host': ('PG12107-authz-fixture-host-v2', '4f764569dc6164b941b9b1e211578d47f6384cd2c0509862c0b6dba45ef0fefc'), 'post': ('PG12110-authz-fixture-post-v1', '633bd25ec34b7ba5bd4549445856dd8653fbae1c4e6c16d30125b87441515760'), 'context': ('PG12111-authz-fixture-context-v1', '6a121b49363d0e06818a1444a0938477220d6ae9b23e8588d739d748978a5a22'), 'contextPost': ('PG12113-authz-fixture-context-post-v1', '59fa4f28c7d477a4b920f17edb772d16447dc3145220aa36cb2ffc60dd334158'), 'trace': ('PG12112-authz-fixture-trace-v1', '951a1f1c17f35efe7b51e0a4fa55451959726f3ead61201c1687d924d369f015'), 'tracePost': ('PG12114-authz-fixture-trace-post-v1', '21cff7fc4e5932f657a657a46865d076a06fd3c954a641deb508db188e3f0804')}
def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions']==4 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    previous=data.read_checked(data.BASE/'PG12074-media-wire-fixture-six-compile-v1/manifest.json','2a15c3279d00cd2509f156e85442ae46124a3f1c5e8ea1b6b9ed0c82e29e81b0')
    assert jar_classes(previous)==jar_classes(normal) and len(jar_classes(normal))==1843
    old,new=test_classes(previous),test_classes(normal);assert set(old)==set(new) and len(new)==1962
    changed=[key for key in old if old[key]!=new[key]];assert len(changed)==1;details=[]
    for role,entry in changed:
        a=parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        b=parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        details.append(dict(module=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    assert {r['sourceFile'] for r in details}=={'WebAuthorizationFilterTest.java'}
    vectors=selftest();measure=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])['web']
    counts={kind:dict(missed=sum(u['counters'][kind]['missed'] for u in measure['selectedValueMain'].values()),covered=sum(u['counters'][kind]['covered'] for u in measure['selectedValueMain'].values())) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    assert not measure['selectedValueFourCounters100'] and not measure['wholeArtifactCoverage100'] and {k:v['covered'] for k,v in counts.items()}==dict(LINE=21,METHOD=3,CLASS=1,BRANCH=0) and all(c['missed']==0 for c in counts.values())
    static=data.read_checked(data.BASE/'PG12109-authz-fixture-static-v2/manifest.json','debf7b4ce804a32e6b5c797e4fc5b1a2c129bf7caa065a1891487e50fa31ff6b');assert static['actualExit']==1 and static['reports']['pmd']['findings']==3
    failure=data.BASE/PINS['host'][0]/'prior-failure.safe.json';f=json.loads(failure.read_bytes());assert len(f['failedTools'])==2 and all(t['bodyExit']==1 and t['productTestsExecuted']==0 and not t['outputCreated'] and data.sha((data.ROOT/t['entry']).read_bytes())==t['entrySha256'] for t in f['failedTools']) and not f['platformRefusal'] and f['productTestsReexecuted']==0
    assert {t['entrySha256'] for t in f['failedTools']}=={'74e0b70b025d2cffb2acd011ac24ffa0d8722041ca7c752cd7e5493b2d4ae17a','47a30972f6217217b091abd50f55ea66f940f6474a361c129f940d762cb9bd93'}
    assert host['typeOnlyReferenceGuardVectors']==dict(positive=1,negative=4) and post['metadataNegativeVectors']==6
    assert v['contextPost']['metadataNegativeVectors']==8 and v['context']['sourceContexts']==3
    inverse=data.read_checked(data.BASE/'PG12102-authz-fixture-source-post-v1/manifest.json','63817adf704ab9db4c1d7b8cff0baa0609590f26bb8b4eeadf7425cd9ef8da7a');assert inverse['metadataNegativeVectors']==24
    run=Path(host['begin']['testCwd']).parent;loadedraw=(run/'classload-metadata.log').read_bytes();assert data.sha(loadedraw)==host['classloadSha256']
    loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',loadedraw.decode()));assert not any(n.startswith(('org.postgresql.','dev.codex.schubert.nk.api.','dev.codex.schubert.nk.web.bootstrap.')) or 'ConnectionFactory' in n for n in loaded)
    assert not list(Path(host['begin']['testCwd']).iterdir());closure=host['begin']['eligibilityClosureSourceHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items())
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2296_Mock権限表十是正_製造単体仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2297_Mock権限表十是正_製造単体結果.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'code-debug.json',dict(source=SOURCE,rows=details,structuralReaderVectors=vectors,meaningProof='strict original raw inverse24 vectors plus actual4; opaque CP index representation is not standalone semantic proof'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1945','BUG-1946','BUG-1947'],relatedYkt=['YKT-1694','YKT-1695','YKT-1696'],implementationDecision='PG-D726',tests=host['begin']['cases'],actual=dict(tests=4,suites=1,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainMeasuredCounters=counts,defaultJacocoFilters=True,zeroBranchCountersAreNA=True,noManualExclusions=True,eligibilityClosureSourceHashes=closure,codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),priorToolFailureRecordSha256=data.sha(failure.read_bytes()),failedToolEntryUnchanged=True,allMainClassesUnchanged=1843,otherTestClassesUnchanged=1961,testClassesChanged=1,stringConstants=10,referencesReplaced=63,rawStaticBefore=13,rawStatic=3,rawStaticGateExit=1,actualSecretCount=None,fullArtifactsCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
