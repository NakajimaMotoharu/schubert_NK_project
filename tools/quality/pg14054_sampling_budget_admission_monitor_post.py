"""Independent XML/private monitor and exact fixed analyzer context, no Product concurrency execution."""
import copy
import json
import re
import zipfile
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg14052_sampling_budget_admission_monitor_contexts as selected

OUT=data.BASE/'PG14054-sampling-budget-admission-monitor-post-v1'
PIN='4d35f74a33d5cf228fa06d4435201c9fd9f5969bcf419fa3262fcb99d98e30c0'
def wire(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def main():
    invocation=capture(__file__);assert not OUT.exists()
    raw=data.read_checked(selected.OUT/'manifest.json',PIN);verify(raw['invocation'])
    review=data.read_checked(selected.OUT/'review.json',raw['reviewSha256']);actual=review['rows']
    assert raw['source']==selected.SOURCE and raw['actualExit']==raw['productTestsExecuted']==0
    assert len(actual)==raw['sourceContexts']==raw['rawRetained']==22 and raw['sourceFiles']==13
    measured=data.read_checked(data.BASE/selected.MEASURED[0]/'manifest.json',selected.MEASURED[1])
    xml=(data.BASE/selected.MEASURED[0]/'pmd.xml').read_bytes();assert data.sha(xml)==measured['reports']['pmd']['sha256']
    catalog=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    normal,_=selected.cfg.normal();hashes=normal['begin']['inputHashes']
    assert {r['id'] for r in actual}==selected.IDS and len({r['id'] for r in actual})==22
    for row in actual:
        pin,owner,identities=selected.TARGETS[row['path']]
        old,=[r for r in catalog if r['id']==row['id']]
        text=(data.ROOT/row['path']).read_text()
        assert row['id'] in identities and row['source']==selected.SOURCE and data.sha(text.encode())==row['sourceSha256']==pin==old['inputSha256']
        assert old['rowSha256']==row['originalRowSha256'] and old['attributes']==row['attributes'] and row['rule']==selected.RULE
        file,=[f for f in ET.fromstring(xml) if f.tag.rpartition('}')[2]=='file' and f.get('name').endswith('/'+row['path'])]
        nodes=[v for v in file if v.attrib==old['attributes']];assert len(nodes)==row['rawDiagnosticMultiplicity']==1
        attr=nodes[0].attrib;lines=text.splitlines(keepends=True)
        assert attr['beginline']==attr['endline']
        line=lines[int(attr['beginline'])-1];a=int(attr['begincolumn'])-1;b=int(attr['endcolumn'])-1
        assert line[:b].isascii() and chr(9) not in line[:b] and line[a:b]==row['typeToken']=='synchronized'
        start=sum(map(len,lines[:int(attr['beginline'])-1]))+a;end=start+len('synchronized')
        assert (start,end,data.sha(b'synchronized'))==(row['spanStart'],row['spanEndExclusive'],row['spanSha256'])
        assert text[end:].startswith(' (lock)') and row['monitor']=='lock' and row['monitorDeclaration']=='private final Object lock = new Object();' and row['monitorDeclaration'] in text
        assert row['canonicalOwner']==row['canonicalCostOwner']==owner
        assert row['reason']==selected.reason(row['path'],attr['method'])
        assert row['rawRetained'] is row['currentWholeJoinPending'] is True and row['sourceChanged'] is row['nativeRuntimeProven'] is row['allJava25MonitorsExempt'] is False
        assert type(row['productTestsExecuted']) is int and row['productTestsExecuted']==0
    for path,scope in review['directNkRelatedSourceScope'].items():
        text=(data.ROOT/path).read_text()
        declared=re.findall(r'^import (?:static )?(dev\.codex\.schubert\.nk\.[A-Za-z0-9_.]+);$',text,re.M)
        assert sorted(declared)==sorted(scope) and path in selected.TARGETS
        for name,binding in scope.items():
            target=binding['path'];assert hashes[target]==binding['sha256']==data.sha((data.ROOT/target).read_bytes())
            typename=target.split('/src/main/java/',1)[1].removesuffix('.java').replace('/','.')
            assert name==typename or name.startswith(typename+'.')
            assert binding['qualification']=='RELATED_SOURCE_HASH_ONLY_NOT_WHOLE_REVIEW_OR_EXECUTION'
    assert data.sha(selected.RULE_JAR.read_bytes())==selected.RULE_JAR_SHA
    with zipfile.ZipFile(selected.RULE_JAR) as z:rulebytes=z.read('category/java/multithreading.xml')
    assert data.sha(rulebytes)==selected.RULE_RESOURCE_SHA
    rule,=[r for r in ET.fromstring(rulebytes) if r.get('name')=='AvoidSynchronizedStatement']
    xp,=[v.text.strip() for v in rule.iter() if v.tag.rpartition('}')[2]=='value' and v.text and 'SynchronizedStatement' in v.text]
    cmd=measured['stages']['pmd']['command'];assert xp=='//SynchronizedStatement' and cmd[cmd.index('--use-version')+1]=='java-25'
    evidence=review['staticRuleEvidence']
    assert evidence==dict(jarSha256=selected.RULE_JAR_SHA,resourceSha256=selected.RULE_RESOURCE_SHA,xpath=xp,analysisLanguage='java-25',originalPmdExit=4,version='7.28.0',allJava25MonitorsExempt=False,newStaticRunExecuted=False)
    expected=wire(actual)
    def assess(v):
        if wire(v)!=expected:raise ValueError('exact typed owner monitor/source contract required')
    labels=[]
    for key,value in [('id','UNKNOWN'),('source','0'*40),('sourceSha256','0'*64),('rule','Unknown'),('spanStart',0),('spanEndExclusive',0),('spanSha256','0'*64),('monitor','this'),('monitorDeclaration','public final Object lock = new Object();'),('rawDiagnosticMultiplicity',2),('rawRetained',False),('rawRetained',0),('sourceChanged',True),('nativeRuntimeProven',True),('allJava25MonitorsExempt',True),('productTestsExecuted',False)]:
        bad=copy.deepcopy(actual);bad[0][key]=value
        try:assess(bad)
        except ValueError:labels.append(key+':'+type(value).__name__)
        else:raise AssertionError('altered lock/quality scope accepted')
    source_rejected=0
    for path in selected.TARGETS:
        text=(data.ROOT/path).read_text();selected.source_guards(path,text)
        phrases=['private final Object lock = new Object();','synchronized (lock)',*selected.GUARDS.get(path.rpartition('/')[2],['detailedMetricsRequested()', 'return Optional'])]
        for phrase in phrases:
            assert phrase in text
            try:selected.source_guards(path,text.replace(phrase,'REMOVED_EXPECTED_OWNER_STATE'))
            except (AssertionError,ValueError):source_rejected+=1
            else:raise AssertionError('changed monitor/state contract accepted')
    assert len(labels)==16 and source_rejected==65
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    verify(raw['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,invocation=invocation,reviewManifestSha256=PIN,reviewSha256=raw['reviewSha256'],sourceContexts=22,sourceFiles=13,rawRetained=22,metadataNegativeVectors=len(labels),labels=labels,sourceGuardNegativeVectors=source_rejected,directImportScopeIndependentlyConfirmed=True,relatedImportsAreNotWholeReviewOrExecution=True,staticRuleEvidence=evidence,allJava25MonitorsExempt=False,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeRuntimeProven=False,newAccepted=0,formalUpdated=False,effortPercent=None,whole451Accepted=False,wholeF03Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
