"""Independent immutable-output/source/type-name/purpose review, not Product PT or a rerun."""
import copy
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg13026_http_route_name_context import state_after as before_state
from pg9954_pure_query_registry_metadata import INV
import trace_owner_join as ownership

SOURCE = '2f4290e7e511ea30224d087f78d44964d3488919'
OUT = data.BASE/'PG13038-throwable-identity-post-v1'
TYPED = data.BASE/'PG13036-throwable-identity-types-v3'
POSITIVE = set('PMD-00077 PMD-00121 PMD-00163 PMD-00185 PMD-00190 PMD-00195 PMD-00197 PMD-00199 PMD-00217 PMD-00222 PMD-00245 PMD-00250 PMD-00254 PMD-00274 PMD-00279 PMD-00307 PMD-00308 PMD-07216 PMD-07235 PMD-07278 PMD-07290 PMD-07316 PMD-07326 PMD-07328 PMD-07335 PMD-07415 PMD-07440 PMD-07443'.split())

def state_after():
    ids,refs,pending = before_state(); assert POSITIVE <= ids-refs and not POSITIVE & pending
    return ids,refs|POSITIVE,pending|POSITIVE

def type_name(value):
    return re.sub(r'@org\.jspecify\.annotations\.Nullable\s*','',value).replace(' ','')

def expected():
    m = data.read_checked(TYPED/'manifest.json','da05a736e3d76741d04e8de8b14188a5428c0ba24ecd856e242fc6b9f8c60a4d')
    value = data.read_checked(TYPED/'types.json',m['typesSha256'])
    assert m['source'] == value['source'] == SOURCE and m['actualExit'] == 0 and m['staticOnly'] and not m['productCodeChanged']
    assert m['productTestsExecuted'] == m['productClassesLoaded'] == m['newProductClassFiles'] == 0
    assert m['observedRows'] == len(value['observed']) == 56 and m['unresolvedRows'] == len(value['unresolved']) == 0 and m['bothThrowableTypeCandidates'] == 28
    begin = m['begin']; slot = data.ROOT.parent/'pgpt-runs/PG379/pg13036-throwable-identity-types-v3'
    assert all(stage['actualExit'] == 0 and not stage['timedOut'] for stage in m['stages'])
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in {**begin['dependencyHashes'],**begin['classpathFiles']}.items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in begin['sourceHashes'].items())
    assert data.sha(Path(begin['helperPath']).read_bytes()) == begin['helperSha256']
    log = (slot/'classload-metadata.log').read_bytes(); assert data.sha(log) == m['classloadSha256']
    assert not re.findall(r'\[class,load\]\s+(dev\.codex\.schubert\.nk\.\S+)\s+source:',log.decode())
    physical = {str(path.relative_to(slot)):data.sha(path.read_bytes()) for path in slot.rglob('*.class')}
    assert physical == m['helperClassHashes'] and all(path.startswith('helper/ThrowableIdentityTypeInspection') for path in physical)
    assert not list((slot/'empty-processor-path').iterdir())
    stdout = (slot/'inspect-static-types.stdout').read_text().splitlines()
    assert stdout[:2] == ['DIAGNOSTIC_ERRORS\t0','STATIC_ONLY_NO_GENERATE\ttrue'] and len(stdout[2:]) == 56
    observed = {row['id']:row for row in value['observed']}; raw = {row['id']:row for row in begin['originalDiagnostics']}
    assert len(observed) == len(raw) == 56 and set(observed) == set(raw)
    for line in stdout[2:]:
        parts = line.split('\t'); assert parts[0] == 'TYPE' and len(parts) == 12
        row = observed[parts[1]]
        assert [row['path'],str(row['astLine']),str(row['astColumn']),row['operator'],row['leftType'],row['rightType'],row['leftThrowable'],row['rightThrowable'],row['enclosingClass'],row['enclosingMethod']] == parts[2:]
    logical_raw = (data.ROOT/INV).read_bytes(); assert data.sha(logical_raw) == begin['logicalInventorySha256']
    logical = {row['path']:row for row in json.loads(logical_raw)['artifacts']}
    paths = list(dict.fromkeys(row['path'] for row in begin['originalDiagnostics']))
    initial = [dict(path=path,sha256=begin['sourceHashes'][path],owner=logical.get(path,{}).get('owner')) for path in paths]
    ownership.validate(begin['sourceOwnerRows'],initial,logical,begin['sourceHashes'],'WBS-F03')
    registry = data.read_checked(data.BASE/'PG13028-http-route-name-trace-v1/manifest.json','8cc4b73e1470a67b8e458abb89afb2284cc34fe8c5a3660f57dd16e339e41637')
    registered = {row['path']:row for row in registry['sourceRows']}
    for row in begin['sourceOwnerRows']:
        if row['path'] in registered:
            prior = registered[row['path']]
            assert (row['canonicalOwner'],row['canonicalCostOwner'],row['sha256']) == (prior['canonicalOwner'],prior['canonicalCostOwner'],prior['sha256'])
    p = data.ROOT/'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/codec/PermanentProtocolException.java'
    assert 'final class PermanentProtocolException extends RuntimeException' in p.read_text()
    known_throwables = {'java.lang.Throwable','java.lang.Exception','java.lang.RuntimeException','java.lang.Error','dev.codex.schubert.nk.protocol.codec.PermanentProtocolException'}
    candidates = {identifier for identifier,row in observed.items() if type_name(row['leftType']) in known_throwables and type_name(row['rightType']) in known_throwables}
    assert candidates == POSITIVE and {identifier for identifier,row in observed.items() if row['leftThrowable'] == row['rightThrowable'] == 'YES'} == POSITIVE
    reviews = []
    for identifier in sorted(POSITIVE):
        row = copy.deepcopy(observed[identifier]); original = raw[identifier]
        assert row['sourceSha256'] == original['inputSha256'] == begin['sourceHashes'][row['path']]
        assert row['originalLine'] == original['line'] and row['originalColumn'] == int(original['attributes']['begincolumn'])
        assert row['operator'] in ['EQUAL_TO','NOT_EQUAL_TO'] and row['astLine'] <= row['originalLine']
        lines = (data.ROOT/row['path']).read_text().splitlines(); line = row['originalLine']
        window = lines[line-1:line+4]
        assert row['sourceSnippet'] == lines[line-1].strip() and any('addSuppressed' in item for item in window)
        reason = 'Same physical primary/secondary must not self-suppress; distinct failure/Error preserves original identity under SS312 owned-close/rollback rules'
        category = 'SELF_SUPPRESSION_PHYSICAL_OBJECT'
        if identifier in {'PMD-00077','PMD-07235'}:
            category = 'CLOSE_DIAGNOSTIC_PHYSICAL_FAILURE_DEDUP'; reason = 'Compare actual closing frame with primary before adding fixed cleanup diagnostic; identity prevents duplicate causal report, not a value/message comparison'
        elif identifier == 'PMD-00308':
            category = 'ALREADY_ATTACHED_CAUSE_ALIAS'; reason = 'Do not reattach the identical existing OutboxSendException cause; compare physical Throwable, not provider-defined equals'
        row.update(manualPurposeReviewComplete=True,status='STATIC_DIAGNOSTIC_CONTEXT_REVIEWED_DYNAMIC_HOLD',purposeCategory=category,reason=reason,
            sourceContext=[item.strip() for item in window],designReference='origin/main8b91944df/SS312 first identity and owned transaction notes',
            actualViolation=None,dynamicExecutionQualificationInferred=False,actualAllocatedPp=None,additionalSharedCostPp=0)
        reviews.append(row)
    ids,refs,pending = state_after(); assert [len(ids),len(refs),len(pending),len(ids-refs)] == [8472,3231,913,5241]
    for name,sha in [('PG13034-throwable-identity-types-v1','7096efbbf13ba77ed99f1f4de20dab4efc103f92972401c2f14ac5250812edf1'),('PG13035-throwable-identity-types-v2','d0940bda234aeb6c23ffca465a863b6e8fc0a05f15448da47fe115576a333b9e')]:
        failed = json.loads((data.BASE/name/'failure.safe.json').read_bytes())
        assert failed['actualExit'] == 1 and not failed['javaHelperStarted'] and data.sha((data.ROOT/failed['entry']).read_bytes()) == sha
    return dict(source=SOURCE,reviewedRows=reviews,typedNonThrowableUnclassified=[observed[key] for key in sorted(set(raw)-POSITIVE)],
        reviewedThrowableRows=28,typedRows=56,sourceFiles=36,unresolvedAstRows=0,nonThrowablePurposeReviewPending=28,
        sourceDerivedRaw=8472,mainRaw=1504,testRaw=6968,totalPriorCorrections=953,globalRawCorrectionsAdded=0,
        joinedContextWarnings=3231,sourceReboundCurrentWholePending=913,noCurrentReferenceInThisJoin=5241,
        newlyReviewedContextIds=sorted(POSITIVE),actualViolationCount=None,productTestsExecuted=0,productClassesLoaded=0,newProductClassFiles=0,
        sourceCodeChanged=False,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None,
        scopeLimit='Start coordinates exported; enclosing-range match enforced in immutable original Java entry. No AST run replay or fabricated end-coordinate export.',
        expectedMeaning='Static identity intent only; not runtime fatal/cleanup/ownership correctness or PT execution exemption')

def require(value,reference):
    assert value == reference
    assert value['reviewedThrowableRows'] == 28 and len(value['newlyReviewedContextIds']) == 28 and value['nonThrowablePurposeReviewPending'] == 28
    assert value['productTestsExecuted'] == value['productClassesLoaded'] == value['newProductClassFiles'] == 0 and value['actualViolationCount'] is None and value['newAccepted'] == 0

def main():
    invocation = capture(__file__); assert not OUT.exists(); reference = expected(); require(reference,reference)
    labels = []
    for key,bad_value in [('source','0'*40),('sourceDerivedRaw',8444),('reviewedThrowableRows',56),('nonThrowablePurposeReviewPending',0),('actualViolationCount',0),('productTestsExecuted',56),('newProductClassFiles',1),('newAccepted',1),('wholeF03Accepted',True)]:
        bad = copy.deepcopy(reference); assert bad[key] != bad_value; bad[key] = bad_value
        try: require(bad,reference)
        except AssertionError: labels.append(key)
        else: raise AssertionError('misstated analysis/qualification accepted')
    verify(invocation); OUT.mkdir(); data.write(OUT/'review.json',reference)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        typedManifestSha256='da05a736e3d76741d04e8de8b14188a5428c0ba24ecd856e242fc6b9f8c60a4d',reviewSha256=data.sha((OUT/'review.json').read_bytes()),
        reviewedThrowableRows=28,nonThrowablePurposeReviewPending=28,metadataNegativeVectors=len(labels),nonVacuousLabels=labels,
        sourceDerivedRaw=8472,totalPriorCorrections=953,joinedContextWarnings=3231,sourceReboundCurrentWholePending=913,
        productTestsExecuted=0,productClassesLoaded=0,newProductClassFiles=0,actualViolationCount=None,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
