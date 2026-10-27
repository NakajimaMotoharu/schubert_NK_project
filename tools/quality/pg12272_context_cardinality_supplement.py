"""Additive auxiliary-count correction from immutable public static/review evidence; no product rerun."""
import ast
import xml.etree.ElementTree as ET
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11054_api_request_context import original_match

SOURCE='d8a2b7952b321b75fe7fcc1c8d3acb287faca6ec'
OUT=data.BASE/'PG12272-context-cardinality-supplement-v1'
FAMILY={
 'authz':('PG12111-authz-fixture-context-v1','6a121b49363d0e06818a1444a0938477220d6ae9b23e8588d739d748978a5a22','PG12109-authz-fixture-static-v2','debf7b4ce804a32e6b5c797e4fc5b1a2c129bf7caa065a1891487e50fa31ff6b'),
 'batch':('PG12141-batch-value-fixture-context-v1','f7de8c789c6e84d9663b892c5646561e981b3cdda626321565f45b994f684da6','PG12139-batch-value-fixture-static-v2','5511be09a7cb8e0f986d5a510a428a93d0b66d8bad813bb75d5b7193513a6a18'),
 'auditSubset':('PG12175-audit-fixture-context-v2','6c4c5b7032d4c2bd6e103900648521ee961a816a184d89215ed46d50d5ab036e','PG12168-audit-fixture-static-v1','7782fd394e8f7972e0dfc878264791ce2f6540da31574f8a0eb7dfbdc0840845'),
 'metricCorrection':('PG12201-audit-metric-context-v1','12c21f28214a9869f24549a69d8fdf577b12316a0c31b6bc822cd6bcf94a2ee2','PG12198-audit-metric-static-v1','a10133ca7dedd88083f8f39c8b96b0af1cde5ffc161655dc8feb3591b10d8255'),
 'checksumCorrection':('PG12231-check-health-context-v1','2de10000666b0402a551ee2efb032761c6f3ff654f51aeffccb3222699ea3c86','PG12228-check-health-static-v1','3f9d9526d41956dae9ea25f17d123f3e1b948768fa06efb3fa65ce07fde40428'),
 'mainLocal':('PG12246-main-local-maps-context-v1','1481093beb6c7d9642959dcd0b4b956236fda824f2df97379cbaf5ec23d7948e',None,None),
 'bundle':('PG12260-bundle-maps-context-v1','8afbd022d68c9437ef6854aa51c69a705a456d2311f76946f52d0a10011b6a05',None,None)}
TARGETS={
 'metricCorrection':('4b5f6faa078be348132a6ece9140b0c1a31d7907',{'PMD-04748','PMD-04749','PMD-07954','PMD-07955','PMD-07956'},'tools/quality/pg12201_audit_metric_context.py'),
 'checksumCorrection':(SOURCE,{'PMD-00994','PMD-00995'},'tools/quality/pg12231_check_health_context.py')}
CONSUMERS={
 'metricCorrection':[
 ('PG12203-audit-metric-context-post-v1','f7b5d181661634f8cfff2aade0bbf30eefc7d22ae0942cfac58d529b64ca9e07','tools/quality/pg12203_audit_metric_context_post.py','CONTEXT_POST'),
 ('PG12206-audit-metric-completion-v1','c92bdb845774f87dc2692941101db7db040563b09f8c111bb3c3f364e8580b1f','tools/quality/pg12206_audit_metric_completion.py','COMPLETION'),
 ('PG12202-audit-metric-trace-v1','b0a68a0a64aaf11d2b0abdd94814207edd67e9391e36f49354e254979e2d55be','tools/quality/pg12202_audit_metric_trace.py','TRACE'),
 ('PG12210-current-audit-metric-delta-v1','01e517af4382b5508ded3b11775223d7c7ca555325399e2aff59d0880dbce767','tools/quality/pg12210_current_audit_metric_delta.py','SET')],
 'checksumCorrection':[
 ('PG12233-check-health-context-post-v1','bd3fe22d3fb448259d10d4b7afad63b976c1692816258e93e5131b49c60e7cdf','tools/quality/pg12233_check_health_context_post.py','CONTEXT_POST'),
 ('PG12236-check-health-completion-v1','213fd201799e3ffd9ce9abbf04efb6ffb40179635dcff77f8fde4f63a02b9756','tools/quality/pg12236_check_health_completion.py','COMPLETION'),
 ('PG12232-check-health-trace-v1','090aeb1ffbd30cc6ff65a03d9b437580cd30ece93292cde31e765471e863221b','tools/quality/pg12232_check_health_trace.py','TRACE'),
 ('PG12240-current-check-health-delta-v1','9f37c0d8983be65a362088e8adbf47c021199824d3055baf86ef36a73167a70a','tools/quality/pg12240_current_check_health_delta.py','SET')]}

def raw_field_reads(tree):
    result=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Subscript) and isinstance(node.slice,ast.Constant) and node.slice.value=='rawRetained':result.append(node.lineno)
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in ('get','pop','setdefault') and node.args and isinstance(node.args[0],ast.Constant) and node.args[0].value=='rawRetained':result.append(node.lineno)
    return sorted(result)

def main():
    invocation=capture(__file__);assert not OUT.exists()
    root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    family=[];corrections=[];consumers=[];preserved={}
    for name,(folder,pin,static_folder,static_pin) in FAMILY.items():
        path=data.BASE/folder/'manifest.json';m=data.read_checked(path,pin);preserved[str(path.relative_to(data.ROOT))]=pin
        review=data.read_checked(path.parent/'review.json',m['reviewSha256']);rows=review['rows'];ids={r['id'] for r in rows}
        assert m['actualExit']==0 and type(m['sourceContexts']) is int and type(m['rawRetained']) is int and len(ids)==len(rows)==m['sourceContexts'] and rows and all(r['source']==m['source'] for r in rows)
        whole_ids=None;static_report_sha=None
        if static_folder:
            sp=data.BASE/static_folder;st=data.read_checked(sp/'manifest.json',static_pin);assert st['source']==m['source'] and st['actualExit']==1 and st['reports']['pmd']['processingErrors']==0
            raw=(sp/'pmd.xml').read_bytes();static_report_sha=data.sha(raw);assert static_report_sha==st['reports']['pmd']['sha256']
            actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
            whole_ids={original_match(p,n,root,actual)['id'] for p,n in actual};assert len(whole_ids)==len(actual)==st['reports']['pmd']['findings'] and ids<=whole_ids
        mismatch=m['rawRetained']!=len(ids);assert mismatch==(name in TARGETS)
        row=dict(name=name,source=m['source'],originalManifestPath=str(path.relative_to(data.ROOT)),originalManifestSha256=pin,reviewSha256=m['reviewSha256'],declaredSourceContexts=m['sourceContexts'],declaredRawRetained=m['rawRetained'],selectedRetainedFindingIds=sorted(ids),selectedRetainedCount=len(ids),rawRetainedDefinition='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',wholePinnedStaticFindingIds=sorted(whole_ids) if whole_ids is not None else None,wholePinnedStaticRawCount=len(whole_ids) if whole_ids is not None else None,isProperSubsetOfPinnedStatic=ids<whole_ids if whole_ids is not None else None,wholeCurrentAnalyzerReissued=False,disposition='CORRECTION_REQUIRED' if mismatch else 'NO_COUNT_CORRECTION_SELECTED_SCOPE_EXPLICIT',staticManifestPath=str((data.BASE/static_folder/'manifest.json').relative_to(data.ROOT)) if static_folder else None,staticManifestSha256=static_pin,staticReportSha256=static_report_sha,newProductTestsExecuted=0)
        family.append(row)
        if mismatch:
            source,expected_ids,writer=TARGETS[name];assert m['source']==source and ids==whole_ids==expected_ids and m['rawRetained']==3
            writer_bytes=(data.ROOT/writer).read_bytes();tree=ast.parse(writer_bytes);literals=[n.value.value for n in ast.walk(tree) if isinstance(n,ast.keyword) and n.arg=='rawRetained' and isinstance(n.value,ast.Constant)];assert literals==[3]
            corrections.append(dict(name=name,source=source,originalManifestPath=row['originalManifestPath'],originalManifestSha256=pin,reviewSha256=m['reviewSha256'],affectedField='rawRetained',observedValue=m['rawRetained'],correctedValue=len(ids),selectedRetainedFindingIds=sorted(ids),rawRetainedDefinition=row['rawRetainedDefinition'],wholePinnedStaticRawCount=len(whole_ids),scopeCoversWholePinnedStaticWarningSet=True,staticManifestPath=row['staticManifestPath'],staticManifestSha256=static_pin,staticReportSha256=static_report_sha,writerPath=writer,writerSha256=data.sha(writer_bytes),cause='COPIED_LITERAL_3_NOT_DERIVED_FROM_SELECTED_ID_SET',legacySourceContextsUnchanged=m['sourceContexts'],oldExitCodeNotReclassified=True,originalManifestRewritten=False,newProductTestsExecuted=0,newRawCorrections=0,newAccepted=0))
            for cf,cpin,entry,kind in CONSUMERS[name]:
                cm=data.read_checked(data.BASE/cf/'manifest.json',cpin);assert cm['source']==source and cm['actualExit']==0
                code=(data.ROOT/entry).read_bytes();reads=raw_field_reads(ast.parse(code));assert not reads
                if kind=='CONTEXT_POST':assert cm['sourceContexts']==len(ids)
                if kind=='COMPLETION':assert cm['rawStatic']==len(ids) and cm['actual']['tests']==(19 if name=='metricCorrection' else 8)
                if kind=='TRACE':
                    key='currentAuditMetricFixtureRuntimeQualification' if name=='metricCorrection' else 'currentCheckHealthFixtureRuntimeQualification';q=cm[key];assert q['rawStatic']==q['sourceLocalContexts']==len(ids)
                if kind=='SET':assert cm['sourceDerivedRaw']==(8608 if name=='metricCorrection' else 8597)
                consumers.append(dict(domain=name,source=source,kind=kind,manifest=str((data.BASE/cf/'manifest.json').relative_to(data.ROOT)),manifestSha256=cpin,entrypoint=entry,entrypointSha256=data.sha(code),directRawRetainedReadLines=reads,declaredPostMissingAuxiliaryCountGuard=kind=='CONTEXT_POST',numericResultUsesIndependentRowsOrStatic=True,originalReferencePreservedSupplementRequired=True,newProductTestsExecuted=0))
    assert len(family)==7 and len(corrections)==2 and len(consumers)==8
    assert next(r for r in family if r['name']=='auditSubset')['isProperSubsetOfPinnedStatic'] and next(r for r in family if r['name']=='auditSubset')['selectedRetainedCount']==3
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in preserved.items())
    verify(invocation);OUT.mkdir();data.write(OUT/'corrections.json',dict(executingSource=SOURCE,sourceDomainsNonAdditive=True,corrections=corrections));data.write(OUT/'family-and-consumers.json',dict(family=family,consumers=consumers,preservedOriginalManifestHashes=preserved,scope='SEVEN_DIRECT_ANCESTOR_OR_DESCENDANT_CONTEXT_FAMILIES_AND_EIGHT_DIRECT_CONSUMER_ENTRIES_NOT_GLOBAL_ALL_TOOLS'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,qualification='MULTI_SOURCE_AUXILIARY_CARDINALITY_CORRECTION_NO_NEW_PRODUCT_RESULT',invocation=invocation,relatedBug='BUG-1958',relatedYkt='YKT-1707',sourceDomainsNonAdditive=True,correctionsSha256=data.sha((OUT/'corrections.json').read_bytes()),familyAndConsumersSha256=data.sha((OUT/'family-and-consumers.json').read_bytes()),correctedMetadataFields=2,familyContextsAudited=7,directConsumerEntriesAudited=8,originalManifestsRewritten=0,sourceCorrections=0,productTestsExecuted=0,normalBuildsExecuted=0,staticAnalyzerRuns=0,nativeOperationsExecuted=0,currentSourceDerivedRaw=8597,currentCorrectionsTotal=820,currentJoinedContexts=3114,currentWholePendingContexts=660,coverage=None,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
