"""Six exact JMS owner transfer contexts; no factory, graph or credential execution."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
OUT = data.BASE/'PG13772-jms-owner-six-contexts-v1'
NORMAL = ('PG13596-lgs-remaining-two-branches-v1','1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12')
MEASURED = ('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
TARGETS = {
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/config/ApiBrokerContexts.java':('af4602cd8c0906045e5985cba6a4e7e32d43b74e59a060f207705b3166f10330','WBS-P005-03',{'sync':'PMD-00156','webLog':'PMD-00157','async':'PMD-00158'}),
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumers.java':('134a6f35746447e6e27020ae8b82da5d67c136f0d20c46e94b41e5b8b81bc47f','WBS-P005-02',{'opened':'PMD-07337','consumer':'PMD-07338'}),
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/WebBrokerContexts.java':('093e19a0dab933309178946242efbd01c3dc4a47c0f97e1cf0fb1d5807be5c1c','WBS-P005-02',{'configured':'PMD-07357'})}
DEPENDENCIES = {}
REASONS = {
 'PMD-00156':'sync factory transfers immediately to pre-sized owners and retainedSync on full construction. List/state/scratch exist before first acquisition; subsequent failure traverses captured owners in reverse. Successful close phases are recorded; UNKNOWN policy must not be treated as returned or successful release.',
 'PMD-00157':'webLog factory is captured into the existing owners list immediately after return inside the protected assembly, then retainedWebLog is assigned only after all profiles exist. It is not a locally disposed temporary; closing it at constructor exit would invalidate the live runtime.',
 'PMD-00158':'async factory is captured into the existing owners list, retainedAsync is then published with the other profiles. No allocation is inserted between final acquisition and simple owner-field assignment. Owner close traverses reverse order and retains unsuccessful phases for later explicit handling.',
 'PMD-07337':'opened is a borrowed alias of the final runtime.context acquired by bind, not a new JMS session. Same lock protects start/close and startAttempted forbids a second start. Static start closes the runtime on failure; bound native caller must capture the owner before instance start. Actual UNKNOWN release is not proved.',
 'PMD-07338':'consumer is created by the retained JMSContext and remains context-owned during registered delivery. Immediate local TWR would remove the listener before normal runtime use. Context close owns its consumers; static startup failure closes the runtime, while explicit bind callers retain partial ownership. No real provider cleanup is qualified.',
 'PMD-07357':'configured returned factory is stored into both final factory and owner fields at the last constructor step. Password port, observer and lock exist before acquire; configureOwned protects setup failure with one close attempt and UNKNOWN observer. Successful runtime close is marked only after owner.close returns.'}
IDS = set(REASONS)

def source_guards(path,text):
    if path.endswith('/ApiBrokerContexts.java'):
        assert text.index('this.owners = new ArrayList<>(3);') < text.index('var sync =')
        assert text.index('this.ownerClosed = new boolean[3];') < text.index('var sync =')
        for field in ['sync','webLog','async']:
            assert text.count('owners.add('+field+');') == 1
            assert 'this.retained'+field[0].upper()+field[1:]+' = '+field+';' in text
        assert 'owners.get(index).close();\\n          ownerClosed[index] = true;' in text
        assert 'if (ownerClosed[index]) continue;' in text
        assert 'if (failure != null) onUnconfirmed.accept(failure);' in text
    elif path.endswith('/ArtemisReplyConsumers.java'):
        assert 'private final JMSContext context;' in text and 'this.context = Objects.requireNonNull(factory.open(), "JMS context");' in text
        assert 'JMSContext opened = context;' in text and 'opened.createConsumer(' in text and 'consumer.setMessageListener(' in text
        assert 'runtime.close();' in text and 'context.close();' in text
        assert text.index('context.close();') < text.index('closed = true;')
        assert 'startAttempted = true;' in text and 'if (stopping || startAttempted)' in text
    else:
        assert 'var configured = newFactory(endpoint, onUnconfirmed);\\n    this.factory = configured;\\n    this.owner = configured;' in text
        assert text.index('this.passwords = Objects.requireNonNull') < text.index('var configured =')
        assert 'var factory = Objects.requireNonNull(acquire.get(), "JMS factory");\\n    try {' in text
        assert 'owner.close();' in text and text.index('owner.close();') < text.index('closed = true;')
        assert 'onUnconfirmed.accept(failure);' in text

def rows():
    normal = data.read_checked(data.BASE/NORMAL[0]/'manifest.json',NORMAL[1]);assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    for path,pin in DEPENDENCIES.items():assert data.sha((data.ROOT/path).read_bytes()) == hashes[path] == pin
    measured = data.read_checked(data.BASE/MEASURED[0]/'manifest.json',MEASURED[1]);assert measured['actualExit'] == 0 and measured['analysisComplete'] and not measured['processingErrors']
    facts = data.read_checked(data.BASE/MEASURED[0]/'findings.json',measured['findingsSha256'])
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    logical = {r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result = []
    for path,(pin,owner,fields) in TARGETS.items():
        text = (data.ROOT/path).read_text();assert data.sha(text.encode()) == hashes[path] == pin;source_guards(path,text)
        ownership = canonical(path,logical);assert ownership['canonicalOwner'] == ownership['canonicalCostOwner'] == owner
        selected = [r for r in facts if r['path'] == path and r['rule'] == 'CloseResource'];assert len(selected) == len(fields)
        for r in selected:
            a = r['attributes'];variable = a['variable'];identity = fields[variable];old, = [v for v in original if v['id'] == identity]
            assert old['path'] == path and old['rule'] == r['rule'] and old['attributes'] == a and old['inputSha256'] == r['sourceSha256'] == pin
            start,end,value = span(text,a);assert value == variable
            result.append(dict(id=identity,path=path,source=SOURCE,sourceSha256=pin,rule=r['rule'],variable=variable,attributes=a,originalRowSha256=old['rowSha256'],spanStart=start,spanEndExclusive=end,spanSha256=data.sha(value.encode()),reason=REASONS[identity],disposition='LONG_LIVED_OWNER_CURRENT_WHOLE_JOIN_PENDING',rawRetained=True,currentWholeJoinPending=True,sourceChanged=False,productTestsExecuted=0,nativeRuntimeProven=False,providerFactoriesQualified=False,graphAlgorithmQualified=False,**ownership))
    assert len(result) == 6 and {r['id'] for r in result} == IDS
    return sorted(result,key=lambda r:r['id'])

if __name__ == '__main__':
    invocation = capture(__file__);assert not OUT.exists();result = rows();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=result,dependencySourceHashes=DEPENDENCIES))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=6,rawRetained=6,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeQualification=False,providerFactoriesQualified=False,graphAlgorithmQualified=False,firstEverReasonCount=None,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
