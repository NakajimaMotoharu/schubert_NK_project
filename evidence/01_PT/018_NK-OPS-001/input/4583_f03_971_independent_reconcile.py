"""Independently join original PMD XML, all606 dispositions, remaining365 and immutable hash errata."""
from pathlib import Path
import datetime
import hashlib
import json
import xml.etree.ElementTree as ET

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
original=b/'evidence/PG36960-current287-root-pmd-v1';root=load(original/'manifest.json');xml=original/'pmd.xml';assert sha(xml)==root['files']['pmd.xml'] and root['rawFindings']==971 and root['actualToolExit']==4
raw=[]
for f in ET.parse(xml).getroot():
 if f.tag.rsplit('}',1)[-1]!='file':continue
 path=Path(f.get('name'));relative=str(path.relative_to(r)) if path.is_absolute() else str(path)
 assert relative in root['sourceInputs']
 for item in f:
  if item.tag.rsplit('}',1)[-1]!='violation':continue
  raw.append(dict(path=relative,rule=item.get('rule'),line=int(item.get('beginline')),column=int(item.get('begincolumn'))))
assert len(raw)==971 and all(sha(r/path)==h for path,h in root['sourceInputs'].items())
allrows=load(b/'evidence/PG36968-current287-pmd971-candidates-v2/all-site-candidates.json');assert len(allrows)==971
for i,x in enumerate(allrows):assert x['rawFindingIndex']==i and raw[i]==dict(path=x['raw']['path'],rule=x['raw']['rule'],line=int(x['raw']['beginline']),column=int(x['raw']['begincolumn']))
prefixes=['PG37038','PG37040','PG37046','PG37048','PG37050','PG37052','PG37054'];decisions={};refs=[]
for prefix in prefixes:
 folder=next((b/'evidence').glob(prefix+'*'));p=load(folder/'manifest.json');assert p['actualExit']==0 and p['sourceCore']==root['sourceCore']
 refs.append(ref(folder/'manifest.json'))
 for x in load(folder/'site-decisions.json'):
  i=x['rawFindingIndex'];assert i not in decisions and 0<=i<971 and raw[i]=={k:x[k] for k in ['path','rule','line','column']}
  assert sha(r/x['path'])==x['sourceSha256'] and x['decision'].startswith('NOT_APPLICABLE')
  assert any(x.get(k,'').strip() for k in ['reason','currentReview'])
  decisions[i]=x
remaining=load(b/'evidence/PG37048-f03-retention-erasure24-applicability-v1/remaining-unmatched.json');unknown={x['rawFindingIndex'] for x in remaining};assert len(decisions)==606 and len(unknown)==365 and not set(decisions)&unknown and set(decisions)|unknown==set(range(971))
errata=b/'evidence/PG37058-manifest-integrity-errata-v1';ep=load(errata/'manifest.json');assert ep['actualExit']==0 and ep['currentCohortChecked']==144 and ep['currentCohortDefects']==2 and ep['referencedHistoricalProfilesChecked']==57
for x in load(errata/'corrections.json'):
 p=r/x['originalManifest']['path'];assert sha(p)==x['originalManifest']['sha256']
 assert p.name not in x['correctedFileInventory'] and all(sha(p.parent/name)==h for name,h in x['correctedFileInventory'].items())
 assert load(p)['files'][p.name]!=sha(p)
for repair in ep['futureProducerSourceRepairs']:
 assert sha(r/repair['original']['path'])==repair['original']['sha256'] and sha(r/repair['futureSource']['path'])==repair['futureSource']['sha256'] and repair['producerExecuted'] is False
out=b/'evidence/PG37060-f03-971-independent-reconcile-v1';assert not out.exists();out.mkdir()
(out/'all-current-dispositions.json').write_text(json.dumps([decisions[i] for i in sorted(decisions)],ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=root['sourceCore'],originalPmdRaw=971,originalPmdToolExit=4,independentlyXmlMatched=971,sourceMainInputsVerified=287,finalNotApplicable=606,unclassified=365,unconfirmedReuseCandidates=0,allDistinctIndicesReconciled=True,producerProofs=refs,rawXml=ref(xml),dispositions=ref(out/'all-current-dispositions.json'),remaining=ref(b/'evidence/PG37048-f03-retention-erasure24-applicability-v1/remaining-unmatched.json'),metadataErrata=ref(errata/'manifest.json'),originalSelfHashEntriesInvalidAndRetained=2,correctedNonselfInventoryVerified=True,affectedFutureSourceRepairs=2,toolCasesObservedOnly=9,toolTestStartTimeMissingExplicit=True,actualProductOrStaticReruns=0,sourceRuleSuppressionChanges=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,rawXml971=True,sourceInputs287=True,finalNA606=True,remaining365=True,unconfirmedCandidates=0,metadataErrataVerified=True,newAcceptance=0)))
