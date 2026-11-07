"""Independently bind each type judgement to original parsed declarations and current source witnesses."""
from pathlib import Path
import collections,datetime,hashlib,json,re,subprocess,copy
R=Path(__file__).resolve().parents[4];P=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22568-wait83-type-contracts-v1';OLD=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22502-test-wait85-source-inventory-v1';OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22570-wait83-type-contracts-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def valid(row):
 typ=row['type'];s=row['site'];ev=row['witnesses'];text='\n'.join(x.get('text','') for x in ev)
 if typ=='UNKNOWN':return row['classification']=='UNKNOWN'
 if not ev:return False
 if typ=='java.util.concurrent.Future':return row['classification']=='FUTURE_FIXED_AND_WHOLE58_REQUALIFIED' and 'java.util.concurrent.Future<' in text and any(x.get('tests')==58 for x in ev)
 if typ=='org.springframework.security.core.context.DeferredSecurityContext':return 'loadDeferredContext(HttpServletRequest request)' in text and 'implements DeferredSecurityContext' in text and row['classification']=='DEFERRED_LOCKING_GET_NOT_FUTURE_LIVENESS_NOT_INFERRED'
 if typ.endswith('ApiOutboxObservationSource'):return 'ApiOutboxObservationSource source(String mode)' in text and 'return current.get().observation;' in text and 'implements Supplier<Optional<Snapshot>>' in text
 short=typ.rsplit('.',1)[-1]
 if short not in ['AtomicInteger','AtomicLong','AtomicReference','Optional','ThreadLocal']:return False
 return short in text

def main():
 assert not OUT.exists();m=load(P/'manifest.json');assert m['actualExit']==0 and m['productTestsExecuted']==0;old=load(OLD/'manifest.json');assert sha(OLD/'manifest.json')==m['originalInventory']['sha256'];q=load(R/m['futureRequalification']['path']);assert sha(R/m['futureRequalification']['path'])==m['futureRequalification']['sha256'] and q['actualExit']==0 and q['tests']==58
 for n,h in m['inputHashes'].items():assert '/src/test/java/' in n and not any(x in n for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']);assert sha(R/n)==h
 for n,h in m['sourceWitnessHashes'].items():assert not any(x in n for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']);assert sha(R/n)==h
 for n,h in m['files'].items():assert sha(P/n)==h
 sites=load(P/'sites.json');want=[s for s in load(OLD/'sites.json') if s['kind']=='REF' or s['arity']==0];key=lambda s:(s['path'],s['owner'],s['method'],s['line'],s['columnUtf16'],s['kind']);assert len(sites)==len(want)==83 and {key(x['site']) for x in sites}=={key(x) for x in want};assert sum(x['site']['kind']=='REF' for x in sites)==2
 vars=[s.split('\t') for s in (OLD/'parse.stdout').read_text().splitlines() if s.startswith('VAR\t')];localbinds=0
 for row in sites:
  s=row['site'];assert row['currentSourceSha256']==m['inputHashes'][s['path']] and row['nonblockingGuarantee'] is False and row['wholeTestAccepted'] is False;assert valid(row)
  for w in row['witnesses']:
   assert sha(R/w['path'])==w['sha256']
   if 'text' in w:
    t=(R/w['path']).read_text();assert w['text'] in t and t[:t.index(w['text'])].count('\n')+1==w['line']
  if row['type']=='UNKNOWN':continue
  recv=s['receiver'];locals_=[v for v in vars if v[1]==s['path'] and v[2]==s['owner'] and v[3]==s['method'] and v[4]==recv]
  if locals_ and row['type']!='java.util.concurrent.Future':
   assert len(locals_)==1;v=locals_[0];hint=v[5]+' '+v[6];typ=row['type'].rsplit('.',1)[-1]
   assert typ in hint or typ=='ThreadLocal' and 'ThreadLocal.withInitial' in hint or typ=='DeferredSecurityContext' and 'repository.loadDeferredContext' in hint or typ=='ApiOutboxObservationSource' and 'CALL:source' in hint
   localbinds+=1
  elif recv!='EXPR' and '.' in recv and not recv=='f.security.f.live':
   leaf=recv.rsplit('.',1)[-1];fields=[v for v in vars if v[1]==s['path'] and v[3]=='<field>' and v[4]==leaf];assert len(fields)==1 and row['type'].rsplit('.',1)[-1] in fields[0][5]
 # Every original Future site is one of the exact fixed patch locations, independently specified in040.
 cfg=load(R/'evidence/01_PT/015_NK-WEB-001/input/040_seven_security_port_future_requalification.json');fixed={(x['path'],p['originalLine']) for x in cfg['testClasses'] for p in x['patches']};future=[x for x in sites if x['type']=='java.util.concurrent.Future'];assert len(future)==8 and {(x['site']['path'],x['site']['line']) for x in future}==fixed
 sign=(P/'jdk-sdk-signatures.stdout').read_text();assert 'DeferredSecurityContext extends java.util.function.Supplier<org.springframework.security.core.context.SecurityContext>' in sign;assert m['signatures']['actualExit']==0 and not m['signatures']['timedOut'];assert m['signatures']['command'][0].endswith('/javap') and not any('dev.codex' in a for a in m['signatures']['command']);assert all('java.util.concurrent.Future' not in line for line in sign.splitlines() if ' class ' in line or ' interface ' in line)
 sample=next(x for x in sites if x['type']=='java.util.concurrent.atomic.AtomicInteger');bad=copy.deepcopy(sample);bad['type']='java.util.concurrent.Future';assert not valid(bad);bad=copy.deepcopy(sample);bad['witnesses']=[];assert not valid(bad);bad=copy.deepcopy(sample);bad['type']='Unrecognized';assert not valid(bad)
 OUT.mkdir();result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],manifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),verifiedCandidates=83,originalZeroArgCalls=81,originalReferences=2,futureSitesFixedAndRequalified=8,nonFutureTypeOnly=sum(x['type'] not in ['UNKNOWN','java.util.concurrent.Future'] for x in sites),unknownCount=m['unknownCount'],classificationCounts=m['classificationCounts'],receiverTypeCounts=m['receiverTypeCounts'],independentLocalAstBindings=localbinds,negativeGuards=['mislabelAtomicAsFuture','missingWitness','unknownType'],productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,effortRate=None,nonblockingOrWholeLivenessAccepted=False,questionDynamicHold=True,ykt2177Closed=False,wholeF03Accepted=False,whole451Accepted=False,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,verified=83,nonFuture=result['nonFutureTypeOnly'],unknown=m['unknownCount'])))
if __name__=='__main__':main()
