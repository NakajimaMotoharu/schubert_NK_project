"""Bind current-source diagnostics by immutable occurrence identity; run no analysis engine."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
r = Path.cwd()
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
base = r/'evidence/01_PT/018_NK-OPS-001/evidence'
rawp = base/'PG20150-current-d8-six-main-static-v1/manifest.json'
reviewp = base/'PG20154-current-d8-context-requalification-v1/review.json'
priorp = base/'PG21706-current4217-main-style-binding-v1/manifest.json'
newp = r/'evidence/01_PT/005_NK-MSG-001/evidence/PG21930-consumer-stop-static-independent-post-v1/manifest.json'
assert sha(rawp) == 'b620e4b78eb7919c1ab38cc0e6da7a8ed992bb0e38800dd2924297b29e52d580'
assert sha(reviewp) == 'febfa0189b50c4263ee55ecab82e6d3edf3eadd4cd2a9e5a33a2f3b3a7d6bcd2'
assert sha(newp) == 'a7f4de3a2de800464ecddc23c208d04ed021b3ee43f7d1010bdd2e4aa94ffc7e'
raw, review, prior, new = [load(p) for p in [rawp,reviewp,priorp,newp]]
normalp = r.parent/'pgpt-runs/PG379/pg21922-consumer-stop-six-main-compile-v1/manifest.safe.json'
oldnormalp = r.parent/'pgpt-runs/PG379/pg20990-outbox-required-six-main-compile-v1/manifest.safe.json'
assert sha(normalp) == 'e925b4c24e0eff9e70f7b3fad0b595d80e90f1a444c87329215d6e4b3d5d8d1f'
assert sha(oldnormalp) == '1db34d8f2ccee9fc90244bea86c3e446be0c0e010c66516a1e25c92df3426618'
normal, oldnormal = load(normalp), load(oldnormalp)
assert normal['source'] == new['productionCoreMain'] == '56720d75714f60d7e31da59c3da8c02baf05de52'
inputs = {n:h for n,h in normal['begin']['inputHashes'].items() if '/src/main/java/' in n and n.endswith('.java')}
assert len(inputs) == 967 and len(raw['sourceInputHashes']) == 966 and raw['rawCounts'] == {'pmd':1494,'checkstyle':0}
assert all(sha(r/n) == h for n,h in inputs.items())
added = set(inputs)-set(raw['sourceInputHashes'])
interface = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/InboundConsumerGroup.java'
assert added == {interface} and not set(raw['sourceInputHashes'])-set(inputs)
changed = {n for n,h in raw['sourceInputHashes'].items() if inputs[n] != h}
outbox = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/JdbcOutboxRepository.java'
consumers = {'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/'+n+'.java'
             for n in ['ApiMessagingRuntime','SyncRequestConsumers','WebLogConsumers','QuestionWorkConsumers']}
assert changed == consumers|{outbox}
assert prior['actualExit'] == 0 and prior['originalRaw'] == 1494 and prior['applicableViolations'] == prior['unclassified'] == 0
assert inputs[outbox] == oldnormal['begin']['inputHashes'][outbox]
key = 'api:dev/codex/schubert/nk/api/messaging/outbound/JdbcOutboxRepository.class'
assert normal['normalPhysicalClassHashes'][key] == oldnormal['normalPhysicalClassHashes'][key]
stylep = newp.parent/'style-applicability.json'
assert sha(stylep) == new['files']['style-applicability.json']
style = load(stylep)
assert style['rawFindings'] == 101 and style['rawPmdExit'] == 4 and style['applicableViolations'] == 0 and not style['suppressionsAdded']
oldrows = review['classified']
assert len(oldrows) == 1494 and len({x['id'] for x in oldrows}) == 1494
oldconsumers = {x['id'] for x in oldrows if x['rawFinding']['path'] in consumers}
assert len(oldconsumers) == 101
assigned = {}
for index,row in enumerate(style['judgments']):
    available = [n for n in row['priorMatches'] if n not in assigned]
    assert available
    selected = available[0]
    assert selected in oldconsumers
    assigned[selected] = dict(currentOccurrence=index,currentFinding=row)
assert set(assigned) == oldconsumers and len({x['currentOccurrence'] for x in assigned.values()}) == 101
projected = []
for old in oldrows:
    finding = old['rawFinding']
    n = finding['path']
    assert old['classification'] == 'CONTEXTUAL_NONAPPLICABLE' and old['actualViolation'] is False
    assert finding['sourceSha256'] == raw['sourceInputHashes'][n]
    if n in consumers:
        current = assigned[old['id']]['currentFinding']
        assert current['path'] == n and current['attributes']['rule'] == finding['rule'] and current['message'] == finding['message']
        assert old['reason'] in current['reasons']
        value = dict(path=n,attributes=current['attributes'],message=current['message'])
        evidence = 'CURRENT21926_RAW_AND21930_INDIVIDUAL_ANCHOR_REVIEW'
    else:
        assert n not in changed
        value = dict(path=n,attributes=finding['attributes'],message=finding['message'])
        evidence = 'EXACT_SOURCE_BYTE_UNCHANGED_FROM20150'
    projected.append(dict(originalOrdinal=old['rawOrdinal'],originalId=old['id'],
        currentSourceSha256=inputs[n],finding=value,classification='CONTEXTUAL_NONAPPLICABLE',
        actualViolation=False,reason=old['reason'],basis=evidence,
        currentConsumerOccurrence=assigned.get(old['id'],{}).get('currentOccurrence')))
beginp = newp.parent/'style-begin.safe.json'
assert sha(beginp) == new['files'][beginp.name]
stylebegin = load(beginp)
assert set(stylebegin['inputHashes']) == consumers|{interface}
assert all(h == inputs[n] for n,h in stylebegin['inputHashes'].items())
spec = r/'evidence/01_PT/018_NK-OPS-001/3624_現56720Main967_F03個別判断対応仕様.md'
head = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
for p in [spec,Path(__file__)]:
    assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(p.relative_to(r))])).hexdigest() == sha(p)
out = base/'PG21976-current56720-main-style-projection-v1'
assert not out.exists()
out.mkdir()
write = lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
write(out/'current-occurrences.json',projected)
value = dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=head,
    productionMainSource=normal['source'],mainSources=967,unchangedFromOriginalSources=961,
    currentConsumerSources=4,outboxPriorChangeAlreadyBound=True,addedMainInterface=1,
    rawPmdOccurrences=1494,currentConsumerOccurrences=101,unmodifiedSourceOccurrences=1393,
    checkstyleIssues=0,applicableViolations=0,unclassified=0,rawGateExitPreserved=raw['rawGateExit'],
    rawMultiplicityPreserved=True,refs=[dict(path=str(p.relative_to(r)),sha256=sha(p)) for p in [rawp,reviewp,priorp,newp,stylep]],
    currentMainInputHashes=inputs,occurrences=dict(path='current-occurrences.json',sha256=sha(out/'current-occurrences.json')),
    duplicateCanonicalGroupsOriginal=review['duplicateGroups'],
    productTestsExecuted=0,enginesReplayed=0,coverage=None,newSourceProofs=0,newAcceptance=0,
    wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortRate=None)
write(out/'manifest.json',value)
print(json.dumps(dict(actualExit=0,mainSources=967,rawOccurrences=1494,currentRebound=101,
                     unclassified=0,manifestSha256=sha(out/'manifest.json'))))
