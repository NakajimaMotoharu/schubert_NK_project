"""Independent immutable XML/ID-domain cardinality correction and negative metadata verification."""
import copy
import xml.etree.ElementTree as ET
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11054_api_request_context import original_match

SOURCE='d8a2b7952b321b75fe7fcc1c8d3acb287faca6ec'
PIN='d2dbc3890af82f6a5dade993e3ee4e18198f303f35951f105d40b22a8c3a9373'
OUT=data.BASE/'PG12274-context-cardinality-post-v1'
EXPECTED={
 'metricCorrection':dict(source='4b5f6faa078be348132a6ece9140b0c1a31d7907',context='PG12201-audit-metric-context-v1',contextPin='12c21f28214a9869f24549a69d8fdf577b12316a0c31b6bc822cd6bcf94a2ee2',static='PG12198-audit-metric-static-v1',staticPin='a10133ca7dedd88083f8f39c8b96b0af1cde5ffc161655dc8feb3591b10d8255',ids={'PMD-04748','PMD-04749','PMD-07954','PMD-07955','PMD-07956'},writer='tools/quality/pg12201_audit_metric_context.py'),
 'checksumCorrection':dict(source=SOURCE,context='PG12231-check-health-context-v1',contextPin='2de10000666b0402a551ee2efb032761c6f3ff654f51aeffccb3222699ea3c86',static='PG12228-check-health-static-v1',staticPin='3f9d9526d41956dae9ea25f17d123f3e1b948768fa06efb3fa65ce07fde40428',ids={'PMD-00994','PMD-00995'},writer='tools/quality/pg12231_check_health_context.py')}

def exact(value,expected):
    if any(value.get(k)!=v for k,v in expected.items()):raise ValueError('independent source/ID scope/count and no-product-credit contract required')

def static_ids(folder,pin,original):
    p=data.BASE/folder;m=data.read_checked(p/'manifest.json',pin);raw=(p/'pmd.xml').read_bytes();assert data.sha(raw)==m['reports']['pmd']['sha256'] and m['reports']['pmd']['processingErrors']==0
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    ids={original_match(path,node,original,actual)['id'] for path,node in actual};assert len(ids)==len(actual)==m['reports']['pmd']['findings']
    return m,ids,data.sha(raw)

def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG12272-context-cardinality-supplement-v1';m=data.read_checked(p/'manifest.json',PIN);c=data.read_checked(p/'corrections.json',m['correctionsSha256']);audit=data.read_checked(p/'family-and-consumers.json',m['familyAndConsumersSha256'])
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert c['executingSource']==SOURCE and c['sourceDomainsNonAdditive'] is True and len(c['corrections'])==len(EXPECTED) and {r['name'] for r in c['corrections']}==set(EXPECTED)
    expected_rows={};domains=[]
    for row in c['corrections']:
        e=EXPECTED[row['name']];ctx=data.read_checked(data.BASE/e['context']/'manifest.json',e['contextPin']);review=data.read_checked(data.BASE/e['context']/'review.json',ctx['reviewSha256']);ids={r['id'] for r in review['rows']};st,xml_ids,xml_sha=static_ids(e['static'],e['staticPin'],original)
        assert ids==xml_ids==e['ids'] and ctx['source']==st['source']==e['source'] and ctx['rawRetained']==3 and len(review['rows'])==ctx['sourceContexts']==len(ids)
        expected=dict(source=e['source'],originalManifestPath=str((data.BASE/e['context']/'manifest.json').relative_to(data.ROOT)),originalManifestSha256=e['contextPin'],reviewSha256=ctx['reviewSha256'],affectedField='rawRetained',observedValue=3,correctedValue=len(ids),selectedRetainedFindingIds=sorted(ids),rawRetainedDefinition='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',wholePinnedStaticRawCount=len(xml_ids),scopeCoversWholePinnedStaticWarningSet=True,staticManifestPath=str((data.BASE/e['static']/'manifest.json').relative_to(data.ROOT)),staticManifestSha256=e['staticPin'],staticReportSha256=xml_sha,writerPath=e['writer'],writerSha256=data.sha((data.ROOT/e['writer']).read_bytes()),cause='COPIED_LITERAL_3_NOT_DERIVED_FROM_SELECTED_ID_SET',legacySourceContextsUnchanged=len(ids),oldExitCodeNotReclassified=True,originalManifestRewritten=False,newProductTestsExecuted=0,newRawCorrections=0,newAccepted=0)
        exact(row,expected);expected_rows[row['name']]=expected;domains.append(dict(name=row['name'],source=e['source'],retainedCount=len(ids),ids=sorted(ids),oldManifestHashUnchanged=e['contextPin']))
    assert len(audit['family'])==7 and len(audit['consumers'])==8
    for row in audit['family']:
        ctx=data.read_checked(data.ROOT/row['originalManifestPath'],row['originalManifestSha256']);directory=(data.ROOT/row['originalManifestPath']).parent;review=data.read_checked(directory/'review.json',ctx['reviewSha256']);ids={r['id'] for r in review['rows']}
        assert len(ids)==len(review['rows'])==ctx['sourceContexts']==row['selectedRetainedCount'] and row['selectedRetainedFindingIds']==sorted(ids) and row['declaredRawRetained']==ctx['rawRetained']
        if row['name'] in EXPECTED:assert ctx['rawRetained']!=len(ids) and row['disposition']=='CORRECTION_REQUIRED'
        else:assert ctx['rawRetained']==len(ids) and row['disposition']=='NO_COUNT_CORRECTION_SELECTED_SCOPE_EXPLICIT'
        if row['staticManifestPath']:
            folder=Path(row['staticManifestPath']).parent.name;st,all_ids,_=static_ids(folder,row['staticManifestSha256'],original)
            assert st['source']==ctx['source'] and ids<=all_ids and row['wholePinnedStaticRawCount']==len(all_ids) and row['isProperSubsetOfPinnedStatic']==(ids<all_ids)
        else:assert row['wholePinnedStaticRawCount'] is None and row['wholePinnedStaticFindingIds'] is None
    subset=next(r for r in audit['family'] if r['name']=='auditSubset');assert subset['selectedRetainedCount']==3 and subset['wholePinnedStaticRawCount']==5 and subset['isProperSubsetOfPinnedStatic']
    for row in audit['consumers']:
        cm=data.read_checked(data.ROOT/row['manifest'],row['manifestSha256']);assert cm['actualExit']==0 and cm['source']==row['source']==EXPECTED[row['domain']]['source'] and not row['directRawRetainedReadLines'] and row['newProductTestsExecuted']==0
        assert data.sha((data.ROOT/row['entrypoint']).read_bytes())==row['entrypointSha256']
    negatives=[]
    for row in c['corrections']:
        ids=row['selectedRetainedFindingIds'];cases=[('source','source','0'*40),('field','affectedField','rawStatic'),('oldValue','observedValue',None),('oldCopied3','correctedValue',3),('missingIds','selectedRetainedFindingIds',[]),('duplicateIds','selectedRetainedFindingIds',[*ids,ids[0]]),('scope','scopeCoversWholePinnedStaticWarningSet',False),('staticHash','staticManifestSha256','0'*64),('oldExit','oldExitCodeNotReclassified',False),('overwrite','originalManifestRewritten',True),('product','newProductTestsExecuted',1),('rawCredit','newRawCorrections',1),('accept','newAccepted',1),('oldContext3','legacySourceContextsUnchanged',3),('denominator','rawRetainedDefinition','WHOLE_CURRENT_PROJECT_RAW'),('whole3','wholePinnedStaticRawCount',3),('originalHash','originalManifestSha256','0'*64),('writerHash','writerSha256','0'*64),('reviewHash','reviewSha256','0'*64)]
        for label,field,value in cases:
            bad=copy.deepcopy(row);bad[field]=value
            try:exact(bad,expected_rows[row['name']])
            except ValueError:negatives.append(row['name']+'.'+label)
            else:raise AssertionError('incorrect cardinality supplement accepted')
    expected_manifest=dict(actualExit=0,source=SOURCE,qualification='MULTI_SOURCE_AUXILIARY_CARDINALITY_CORRECTION_NO_NEW_PRODUCT_RESULT',sourceDomainsNonAdditive=True,correctedMetadataFields=len(EXPECTED),familyContextsAudited=7,directConsumerEntriesAudited=8,originalManifestsRewritten=0,sourceCorrections=0,productTestsExecuted=0,normalBuildsExecuted=0,staticAnalyzerRuns=0,nativeOperationsExecuted=0,currentSourceDerivedRaw=8597,currentCorrectionsTotal=820,currentJoinedContexts=3114,currentWholePendingContexts=660,coverage=None,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None)
    exact(m,expected_manifest)
    for field,value in [('currentSourceDerivedRaw',8596),('currentCorrectionsTotal',821),('currentJoinedContexts',3115),('currentWholePendingContexts',661),('sourceCorrections',2),('productTestsExecuted',27),('qualification','PRODUCT_PASS'),('sourceDomainsNonAdditive',False),('newAccepted',2),('formalUpdated',True),('coverage',{'line':100})]:
        bad=dict(m);bad[field]=value
        try:exact(bad,expected_manifest)
        except ValueError:negatives.append('manifest.'+field)
        else:raise AssertionError('global qualification/credit corruption accepted')
    assert len(negatives)==len(set(negatives)) and len(negatives)==len(EXPECTED)*19+11
    assert all(data.sha((data.ROOT/path).read_bytes())==pin for path,pin in audit['preservedOriginalManifestHashes'].items())
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,supplementManifestSha256=PIN,sourceDomainsNonAdditive=True,domains=domains,correctedMetadataFields=len(domains),familyContextsAudited=7,directConsumersAudited=8,metadataNegativeVectors=len(negatives),metadataNegativeLabels=negatives,oldManifestsUnchanged=True,sourceCorrections=0,productTestsExecuted=0,normalBuildsExecuted=0,staticAnalyzerRuns=0,nativeOperationsExecuted=0,currentSourceDerivedRaw=8597,currentCorrectionsTotal=820,currentJoinedContexts=3114,currentWholePendingContexts=660,coverage=None,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
