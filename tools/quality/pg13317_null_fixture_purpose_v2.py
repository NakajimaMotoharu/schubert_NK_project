"""Four saved static diagnostics: deliberate equals(null) oracle and nested fixture namespaces, no target calls."""
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from f03_literal_batch_diagnostic_v3 import signature
from pg13312_web_business_trace_v2 import state_after as previous_state
from public_java_digest_provenance import LEX,close

OUT = data.BASE/'PG13317-null-fixture-purpose-v2'
IDS = {'PMD-02148','PMD-05293','PMD-06238','PMD-06249'}
OWNERS = {'DbQueryDurationMetricCollectorTest':'WBS-P018-09','InspectorUnitProbeFixture':'WBS-P004-04','InspectorCredentialLoaderTest':'WBS-P018-01'}

def fragment(text,name):
    tokens = [(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
    starts = [i for i,t in enumerate(tokens[:-1]) if t[0] == 'class' and tokens[i+1][0] == name];assert len(starts) == 1
    start = starts[0];brace = next(i for i in range(start+1,len(tokens)) if tokens[i][0] == '{');end = close(tokens,brace,'{','}')
    return text[tokens[start][1]:tokens[end][1]+1],[t[0] for t in tokens[brace+1:end]]

def expected():
    ids,refs,pending = previous_state();assert [len(x) for x in [ids,refs,pending]] == [7747,3345,1366] and IDS <= ids-refs
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    selected = [r for r in original if r['id'] in IDS];assert len(selected) == 4
    n = data.read_checked(data.BASE/'PG13306-web-business-literal-v2-v1/manifest.json','54547059dfcc03323666371126747e3503b35373bae18cc6b49de23d13854cea')
    gm = data.read_checked(data.BASE/'PG13253-current-all-java-static-v2/manifest.json','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
    actual = data.read_checked(data.BASE/'PG13253-current-all-java-static-v2/findings.json',gm['findingsSha256'])
    registry = data.read_checked(data.BASE/'PG13312-web-business-literal-v2-v1/manifest.json','7443c34223aeec8eb18fdf870c68bf1dccd170d5c31f226c997d12e6ad6faaaa')
    rows = []
    for r in selected:
        path = r['path'];text = (data.ROOT/path).read_text();sha = data.sha(text.encode());assert sha == n['begin']['inputHashes'][path]
        a = [x for x in actual if x['path'] == path and signature(x['attributes'],x['message']) == signature(r['attributes'],r['message'])];assert len(a) == 1 and a[0]['sourceSha256'] == sha
        reg = [x for x in registry['sourceRows'] if x['path'] == path];assert len(reg) == 1 and reg[0]['sha256'] == sha
        owner = OWNERS[Path(path).stem];assert reg[0]['canonicalOwner'] == reg[0]['canonicalCostOwner'] == owner
        if r['id'] == 'PMD-02148':
            evidence = 'assertFalse(first.equals(null));';assert evidence in text and 'assertFalse(first.equals("unknown"));' in text and 'var first = new Observation(Outcome.SUCCESS, 1);' in text
            classification = 'DELIBERATE_RECORD_EQUALS_NULL_NEGATIVE_ORACLE'
            purpose = 'Existing dbConn005 deliberately invokes equals(null) and independently expects false, beside wrong-type/unequal/record value contracts; replacing with reference-null comparison would stop testing equals.'
            risk = 'Source expectation only: no current Test run, no generated-record method coverage/whole collector/concurrency success or PT exemption inferred.'
        elif r['id'] == 'PMD-05293':
            evidence,_ = fragment(text,'InspectorUnitProbeFixture');assert 'private InspectorUnitProbeFixture() {}' in evidence
            assert all('static final class '+s in evidence for s in ['Script','Child'])
            child,_ = fragment(text,'Child')
            assert all('final class '+s in child and 'static final class '+s not in child for s in ['ReadStream','WriteStream'])
            classification = 'NAMESPACE_FOR_STATIC_NESTED_FIXTURE_TYPES'
            purpose = 'Private outer constructor prevents meaningless namespace instances; outer static Script/Child types provide reader/process ports, while Child owns its nonstatic ReadStream/WriteStream inner types, not outer static methods or fields.'
            risk = 'Only source/type purpose, not permission to invoke fixture/process methods or original Unit/service tests; no real process/Unit/owner state was observed.'
        else:
            name = 'TestIo' if r['id'] == 'PMD-06238' else 'TestSecurity';evidence,tokens = fragment(text,name)
            assert not any(tokens[i:i+2] == ['@','Test'] for i in range(len(tokens)))
            assert 'new '+name+'(' in text and ('implements InspectorCredentialLoader.Io' if name == 'TestIo' else 'implements InodeSecurityCalls') in evidence
            classification = 'NESTED_IO_FAULT_PORT_NOT_JUNIT_TEST_CLASS'
            purpose = 'Nested '+name+' implements the parent credential Test fault port and is constructed by existing outer tests; Test prefix is fixture naming, not an unannotated JUnit case.'
            risk = 'TestIo wraps actual NioIo and TestSecurity calls Files/native-facing ports; whole credential Test remains HOLD. No class load, instance, FS/security/credential access or extracted harness.'
        line = int(a[0]['attributes']['beginline'])
        rows.append(dict(id=r['id'],path=path,sourceSha256=sha,originalInputSha256=r['inputSha256'],originalAttributes=r['attributes'],currentAttributes=a[0]['attributes'],message=r['message'],
            sourceLine=text.splitlines()[line-1],evidence=evidence,evidenceSha256=data.sha(evidence.encode()),classification=classification,purpose=purpose,residualRisk=risk,
            canonicalOwner=owner,canonicalCostOwner=owner,manualPurposeReviewComplete=True,actualViolation=None,ptExecutionExempt=False,productTestsExecuted=0,status='SOURCE_PURPOSE_REVIEWED_NOT_DYNAMIC_ACCEPTED'))
    return dict(source=n['source'],rows=rows,scopeCount=4,purposeReferencesBefore=3345,purposeReferencesAfter=3349,pendingAfter=1370,noReferenceAfter=4398,
        rawDiagnostics=7747,originalCorrections=1694,newCorrections=0,sourceChanged=False,newTestIds=0,productTestsExecuted=0,coverage=None,newAccepted=0,actualViolationCount=None,qualityGateExit=1,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False)

def validate(value):assert json.dumps(value,sort_keys=True) == json.dumps(expected(),sort_keys=True)

def main():
    invocation = capture(__file__);assert not OUT.exists();v = expected();validate(v);verify(invocation);OUT.mkdir();data.write(OUT/'review.json',v)
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,source=v['source'],reviewSha256=data.sha((OUT/'review.json').read_bytes()),newPurposeReferences=4,newCorrections=0,productTestsExecuted=0,
        sourceOrTestChanged=False,newAccepted=0,coverage=None,actualViolationCount=None,qualityGateExit=1,wholeF03Accepted=False,whole451Accepted=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
