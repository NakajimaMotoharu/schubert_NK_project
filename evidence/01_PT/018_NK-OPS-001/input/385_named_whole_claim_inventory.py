"""Finite public named-claim discovery; no execution or qualification transfer from counters/labels alone."""
from pathlib import Path
import datetime,hashlib,json,collections,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';STAGE=R.parent/'PMO/pgpt-completion-stage-20261102';O=B/'evidence/PG23272-named-whole-claim-inventory-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text());blocked=('RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest','SnapshotKeyCloseWitness','pg9892_snapshot_key_close_witness');reads={};cache={}
def public(p):
 p=R/p if not Path(p).is_absolute() else Path(p);assert p.is_relative_to(R) and p.suffix=='.json' and not any(w in str(p) for w in blocked);assert str(p.relative_to(R)).startswith(('documents/400_PGPT/','evidence/01_PT/'));assert not p.is_symlink() and p.stat().st_size<=2*1024*1024
 if str(p) not in cache:cache[str(p)]=load(p);reads[str(p.relative_to(R))]=sha(p)
 return cache[str(p)]
cp=STAGE/'cost-ledger.json';c=load(cp);groups=[g for g in c['ordinaryGroups'] if g.get('wholeSources',0)>0];assert len(groups)==33 and sum(g['wholeSources'] for g in groups)==35;ep=R.parent/'PMO/pgpt-execution-metrics/events.jsonl';eventBytes=ep.read_bytes();es=[json.loads(x) for x in eventBytes.splitlines()];ends=collections.defaultdict(list)
for e in es:
 if e['eventType']=='GROUP_END' or e.get('groupBoundary')=='END':ends[e['groupId']].append(e)
indexp=B/'evidence/PG20458-known-source-evidence-index-legacy-v1/index.json';index=public(indexp);known=[v for v in index['rows'] if v['knownProofs']];assert len(known)==50
candidates={}
def add(n,origin,proofs):
 assert '/src/main/java/' in n and n.endswith('.java') and not any(x in n for x in blocked);p=R/n;assert p.is_file() and not p.is_symlink();row=candidates.setdefault(n,dict(path=n,currentSourceSha256=sha(p),origins=[],proofRefs=[],wholeQualificationTransferred=False));row['origins'].append(origin)
 for ref in proofs:
  if ref not in row['proofRefs']:row['proofRefs'].append(ref)
for row in known:add(row['path'],dict(kind='KNOWN_INDEX_CANDIDATE_NOT_WHOLE_QUALIFICATION',originalSeedStatus=row['originalSeedStatus']),row['knownProofs'])
seedp=R/'documents/400_PGPT/470_PMO/500_SV計画整備_20261104/750_S_POST十一成分再利用・原932と新933・annotation37の分離.json';seed=public(seedp)
for row in seed['componentProofRows']:add(row['path'],dict(kind='SEED750_EXPLICIT_COMPONENT',decision=row['decision']),[dict(manifest=row['proof'],sha256=row['sha256'],source=row['proofSource'])])
# Read only one finite public result-document family; no successful raw Unit logs/index-wide manifest reread.
docroots={}
for p in sorted((R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106').glob('*.json')):
 value=public(p)
 if value.get('groupId') in {g['groupId'] for g in groups} and value.get('endEvent'):docroots.setdefault(value['groupId'],[]).append(dict(path=str(p.relative_to(R)),value=value))
claims=[]
for g in groups:
 events=ends[g['groupId']];assert len(events)==1;e=events[0];t=e.get('technicalMeasurementDelta') or {};named=[x['path'] for x in t.get('coverageBySource',[]) if x.get('path','').endswith('.java')];proofs=list(e.get('sourceEvidenceRefs') or []);docs=docroots.get(g['groupId'],[])
 for d in docs:
  value=d['value']
  if value['endEvent']!=e['eventId']:continue
  for key in ['manifest','post','independentPost']:
   valueRef=value.get(key)
   if isinstance(valueRef,dict) and isinstance(valueRef.get('path'),str):proofs.append(valueRef)
 # Some later explicit group receipts carry only a post ref; discover its exact Main input path.
 if not named:
  for ref in proofs:
   name=ref.get('path')
   if not name or not name.startswith('evidence/01_PT/'):continue
   p=R/name;v=public(p)
   if ref.get('sha256'):assert sha(p)==ref['sha256']
   for key in ['targetSource','mainSource','mainPath','targetPath']:
    z=v.get(key)
    if isinstance(z,str) and '/src/main/java/' in z and z.endswith('.java'):named.append(z)
   for key in ['mainPaths','targetSources']:
    z=v.get(key)
    if isinstance(z,list):named.extend(n for n in z if isinstance(n,str) and '/src/main/java/' in n and n.endswith('.java'))
   iv=v.get('inputProvenance') or {};pins=v.get('inputHashes') or iv.get('inputHashes') or {};mainpins=[n for n in pins if '/src/main/java/' in n and n.endswith('.java')]
   if len(mainpins)==1:named.extend(mainpins)
 named=sorted(set(named));status='EXPLICIT_SOURCE_NAMES_BOUND_CLAIM_ONLY' if len(named)==g['wholeSources'] else 'NAMES_UNRESOLVED_NOT_REEXECUTION_REQUIRED';claim=dict(groupId=g['groupId'],eventId=e['eventId'],declaredWholeSources=g['wholeSources'],explicitSourceNames=named,evidenceRefs=proofs,resultDocumentRefs=[dict(path=x['path'],sha256=reads[x['path']]) for x in docs],status=status)
 if status.startswith('EXPLICIT'):
  for n in named:add(n,dict(kind='LATER_NUMERIC_ADDITION',eventId=e['eventId'],groupId=g['groupId']),proofs)
 claims.append(claim)
assert not O.exists();O.mkdir();rows=sorted(candidates.values(),key=lambda v:v['path']);overlaps=[dict(path=v['path'],origins=v['origins']) for v in rows if any(x['kind']=='SEED750_EXPLICIT_COMPONENT' for x in v['origins']) and any(x['kind']=='LATER_NUMERIC_ADDITION' for x in v['origins'])]
assert any(v['path'].endswith('/ArtifactComparator.java') for v in overlaps)
for name,value in [('candidate-source-rows.json',rows),('addition-claims.json',claims),('public-read-set.json',reads)]: (O/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),legacyAggregate=94,legacyAdditionGroups=33,legacyAdditionClaims=35,knownIndexCandidates=50,seed750ExplicitComponents=11,candidateNamedSources=len(rows),namedAdditionClaims=sum(len(x['explicitSourceNames']) for x in claims if x['status'].startswith('EXPLICIT')),unresolvedAdditionGroups=[x['groupId'] for x in claims if not x['status'].startswith('EXPLICIT')],seedAndLaterClaimOverlaps=overlaps,all94QualifiedOrReconciled=False,wholeQualificationTransferred=False,originalEventBytesSha256=hashlib.sha256(eventBytes).hexdigest(),lastIncludedEventId=es[-1]['eventId'],costLedgerReadSha256=sha(cp),productTestsExecuted=0,newSourceProofs=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,files={n:sha(O/n) for n in ['candidate-source-rows.json','addition-claims.json','public-read-set.json']},verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['actualExit','legacyAdditionGroups','legacyAdditionClaims','candidateNamedSources','namedAdditionClaims','unresolvedAdditionGroups','seedAndLaterClaimOverlaps']}))
