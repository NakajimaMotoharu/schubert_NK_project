"""Review fourteen saved current diagnostics by exact source, not runtime qualification/waiver."""
from collections import defaultdict
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg13132_main_literal_preflight import signature
from pg13144_main_literal_trace_v2 import state_after as previous_state
from quality_scope_dimensions import count

SOURCE = '44afb0a1ecddabfebe577b2037aabdc6fb31d1e3'
MAIN = 'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/LinuxSystemdSession.java'
SHA = 'c931c6ee998ba8e9b1e982d569f7f5ca79f083a0c2cfb36600e5862134518cc9'
OUT = data.BASE/'PG13148-systemd-source-context-v1'
POST = data.BASE/'PG13149-systemd-source-context-post-v1'

def current_ids():
    p = data.read_checked(data.BASE/'PG13132-main-literal-preflight-v1/manifest.json','4367bdd95cd9f8f503855250edb1b9104ad2bd2edf146018912596973ed8f9c0')
    raw = (data.BASE/'PG10690-current-global-static-post-v1/findings.json').read_bytes()
    ids,_,_ = previous_state()
    rows = [r for r in json.loads(raw) if r['path'] == MAIN and r['id'] in ids]
    assert len(rows) == 14 and p['candidateSourceHashes'][MAIN] == SHA
    return p,rows

def state_after():
    ids,refs,pending = previous_state();_,rows = current_ids();wanted = {r['id'] for r in rows}
    assert len(wanted&refs) == 2 and len(wanted-refs) == 12 and wanted&refs <= pending
    return ids,refs|wanted,pending|wanted

def collect():
    proof = data.read_checked(data.BASE/'PG13140-main-literal-post-v2/manifest.json','72128b769a31f41388d6ac2c8f25e5976ac36b479c2de561d22e370d9581c608')
    registry = data.read_checked(data.BASE/'PG13144-main-literal-trace-v1/manifest.json','0fb281be83adb94b0ead9ee71731ab6fe03cebbc3a9e9b64f1fdd530424f3124')
    p,old = current_ids();raw = (data.ROOT/MAIN).read_bytes();assert data.sha(raw) == SHA and proof['source'] == registry['source'] == SOURCE
    text = raw.decode();lines = text.splitlines();xml = data.BASE/'PG13132-main-literal-preflight-v1/pmd.xml'
    assert data.sha(xml.read_bytes()) == p['reports']['pmd']
    buckets = defaultdict(list)
    for row in sorted(old,key=lambda r:(r['line'],int(r['attributes']['begincolumn']))):
        buckets[signature(row['attributes'],row['message'])].append(row)
    result = []
    purpose = {
        'call':'Mark native-call uncertainty before rethrowing the same IOException/RuntimeException/Error object; no normal-close assertion',
        'releaseOutput':'Keep output slot in unconfirmed release state and mark uncertain on native release failure before rethrow; no retry here',
        'start':'A returned C output already exists in an owned slot; a Java pointer read failure becomes uncertain and is rethrown',
        'close':'Set retainedClosed only after arena.close returns; failure marks uncertain and rethrows, not normal completion',
        'invoke':'Direct RuntimeException/Error is rethrown; other Throwable is converted to fixed unavailable. Nested fatal preservation is NOT established here',
    }
    for file in ET.parse(xml).getroot():
        if file.tag.rpartition('}')[2] != 'file' or file.get('name') != str(data.ROOT/MAIN):continue
        for node in sorted(file,key=lambda n:(int(n.get('beginline')),int(n.get('begincolumn')))):
            attrs = dict(node.attrib);key = signature(attrs,node.text.strip());before = buckets[key].pop(0)
            assert before['attributes']['begincolumn'] == attrs['begincolumn'] and before['attributes']['endcolumn'] == attrs['endcolumn']
            line = int(attrs['beginline']);snippet = lines[line-1].strip();rule = attrs['rule'];method = attrs.get('method')
            if rule == 'DoNotUseThreads':
                assert 'Thread.currentThread().threadId()' in snippet and 'new Thread(' not in text
                category = 'CURRENT_THREAD_IDENTITY_OBSERVATION';reason = 'Capture and compare current Java owner thread id, not creating or starting a Thread'
            elif rule == 'AssignmentInOperand':
                assert method == 'decode' and snippet == 'bytes[end++] = octet;' and 'while (end < bytes.length)' in text
                category = 'BOUNDED_DECODE_CURSOR';reason = 'Copy one non-NUL octet then advance the bounded cursor; full UTF8/native correctness is not established by this syntax review'
            else:
                assert rule == 'AvoidCatchingGenericException' and method in purpose and '} catch (' in snippet
                category = 'NATIVE_BOUNDARY_EXCEPTION_SYNTAX';reason = purpose[method]
            result.append(dict(id=before['id'],path=MAIN,source=SOURCE,sourceSha256=SHA,originalSourceSha256=before['inputSha256'],
                originalLine=before['line'],currentLine=line,attributes=attrs,message=node.text.strip(),sourceSnippet=snippet,
                sourceContext=lines[max(0,line-3):line+4],purposeCategory=category,reason=reason,
                status='STATIC_SOURCE_PURPOSE_REVIEWED_DYNAMIC_HOLD',manualPurposeReviewComplete=True,actualViolation=None,
                dynamicExecutionQualificationInferred=False,ptExecutionExempt=False,canonicalOwner='WBS-P018-03',canonicalCostOwner='WBS-P018-03',
                actualAllocatedPp=None,additionalSharedCostPp=0))
    assert all(not rows for rows in buckets.values()) and len(result) == len({r['id'] for r in result}) == 14
    ids,refs,pending = state_after();before_ids,before_refs,before_pending = previous_state()
    assert ids == before_ids and len(refs-before_refs) == len(pending-before_pending) == 12
    assert [len(ids),len(refs),len(pending),len(ids-refs)] == [8459,3271,975,5188]
    assert [(r['canonicalOwner'],r['canonicalCostOwner']) for r in registry['sourceRows'] if r['path'] == MAIN] == [('WBS-P018-03','WBS-P018-03')]
    return dict(source=SOURCE,rows=result,reviewedRows=14,newPurposeReferences=12,existingReferences=2,sourceDerivedRaw=8459,totalPriorCorrections=966,
        joinedContextWarnings=3271,sourceReboundCurrentWholePending=975,noCurrentReferenceInThisJoin=5188,
        productTestsExecuted=0,sourceChanges=0,newAccepted=0,actualViolationCount=None,dynamicCorrectnessUnknown=True,
        ptExecutionExempt=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None,
        currentPmdXmlSha256=p['reports']['pmd'],sourceSha256=SHA,unresolved='Native/FFM/ownership/close/fatal graph execution remains HOLD; source purpose is not defect exemption')

def validate(value,reference):
    assert value == reference
    assert count(value['reviewedRows'],'reviewed') == 14 and count(value['newPurposeReferences'],'new') == 12
    assert count(value['productTestsExecuted'],'PT') == count(value['newAccepted'],'accepted') == 0
    assert value['actualViolationCount'] is None and value['dynamicCorrectnessUnknown'] is True and value['ptExecutionExempt'] is False

def main():
    invocation = capture(__file__);assert not OUT.exists();reference = collect();validate(reference,reference);labels = []
    for key,bad_value in [('source','0'*40),('reviewedRows',28),('newPurposeReferences',14),('sourceDerivedRaw',8445),('actualViolationCount',0),('productTestsExecuted',14),('newAccepted',1),('dynamicCorrectnessUnknown',False),('ptExecutionExempt',True),('wholeF03Accepted',True)]:
        bad = copy.deepcopy(reference);bad[key] = bad_value;assert json.dumps(bad,sort_keys=True) != json.dumps(reference,sort_keys=True)
        try:validate(bad,reference)
        except (AssertionError,ValueError):labels.append(key)
        else:raise AssertionError('false static-purpose qualification accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',reference)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),
        reviewedRows=14,newPurposeReferences=12,metadataNegativeVectors=len(labels),nonVacuousLabels=labels,
        sourceDerivedRaw=8459,totalPriorCorrections=966,joinedContextWarnings=3271,sourceReboundCurrentWholePending=975,
        sourceChanges=0,productTestsExecuted=0,newAccepted=0,actualViolationCount=None,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
