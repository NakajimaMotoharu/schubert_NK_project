"""Fresh Main/whole11/static closure; exact old8 prefix and all24 source dispositions."""
from pathlib import Path
import hashlib,json,subprocess
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG33824-ssc422-auth11-prepare-v1/manifest.json';sp=b/'evidence/PG33826-ssc422-auth11-static-v1/manifest.json';m=ld(pp);st=ld(sp);out=b/'evidence/PG33828-ssc422-auth11-preflight-v1';assert not out.exists()
assert m['actualExit']==st['actualExit']==0 and m['expectedTests']==11 and m['MainSafeClosureRebuilt'] and len(m['apiMainSources'])==5 and len(m['apiTestSources'])==1
assert m['inputHashes']==st['inputHashes'] and all(sha(r/n)==h for n,h in m['inputHashes'].items())
for obj,slot in [(m,pp.parent),(st,sp.parent)]:
 for label,v in obj['stages'].items():
  assert type(v['actualExit']) is int and v['actualExit']==(4 if label=='pmd' else 0) and v['timedOut'] is False
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert st['processingErrors']==[] and st['checkstyleFindings']==0 and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
test=m['apiTestSources'][0];old=subprocess.check_output(['git','show','f2339838dfeaa10644ffd1e19d52ea690512002a:'+test],text=True);text=(r/test).read_text();assert text[:text.index('  /** AUTHCTX-FACT001/SSC422:')].rstrip()==old.rsplit('}',1)[0].rstrip()
source=r/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthContextCodec.java';code=source.read_text();assert 'private static final EnvelopeFactory STANDARD_ENVELOPE = EncryptedAuthContext::new;' in code and code.count('public AuthContextCodec(')==1 and 'interface EnvelopeFactory {' in code and '@Nullable EncryptedAuthContext create(String version, byte[] ciphertext);' in code
assert code.index('this.envelopes = Objects.requireNonNull')<code.index('Map<String, byte[]> copies')<code.index('currentKey.clone()')
assert all(marker not in code for marker in ['Class.forName','ServiceLoader','System.getProperty','System.getenv','java.lang.reflect'])
allowed={'AuthContextCodec.java':{'UseConcurrentHashMap':[82]},'AuthContextCodecTest.java':{'CloseResource':[43,257,365,456],'DoNotUseThreads':[43,46,59,60,257,261,271,272,365,372,383,384,456,470,480,481],'AvoidSynchronizedStatement':[45],'AvoidLiteralsInIfCondition':[357,449]}}
expected={(name,rule,str(line)) for name,rules in allowed.items() for rule,lines in rules.items() for line in lines};actual={(Path(v['path']).name,v['rule'],v['line']) for v in st['rawFindings']};assert actual==expected and len(st['rawFindings'])==len(expected)==24
old_admission=ld(b/'evidence/PG33808-ssc421-authctx8-preflight-v1/manifest.json');assert old_admission['actualExit']==0
legacy={(Path(v['path']).name,v['rule'],v['sourceLine'].strip()):v['reason'] for v in old_admission['classified']};classified=[]
for finding in st['rawFindings']:
 path=Path(finding['path']);text=path.read_text();line=text.splitlines()[int(finding['line'])-1];key=(path.name,finding['rule'],line.strip())
 if key in legacy:reason=legacy[key]
 elif finding['rule']=='AvoidLiteralsInIfCondition':
  assert finding['line']=='449' and line.strip()=='if (calls.incrementAndGet() == 1) {'
  reason='First of exactly two independent construction attempts injects directError/RTE/null; second other-worker attempt must equal independent public JCA envelope. Literal1 selects a closed fixture phase, not any production threshold.'
 else:
  assert finding['rule'] in ['CloseResource','DoNotUseThreads'] and finding['line'] in ['456','470','480','481']
  reason='The single worker is owned by this complete value-construction fixture. Futureget5s, unconditional shutdownNow/assert await10 before codec.close, exact2 attempts, ciphertext erasure and independently calculated envelope are required. Lists are used sequentially and Future.get establishes publication; no real key, backend or managed application worker.'
 if finding['rule']=='UseConcurrentHashMap':
  assert 'keys = Map.copyOf(copies);' in code and 'copies' not in code[code.index('  public EncryptedAuthContext encrypt'):]
  reason+=' New factory is only stored, not invoked in the constructor, so the constructor-local map still never escapes and nullable factory is rejected before copying.'
 classified.append(dict(**finding,sourceLine=line,sourceSha256=sha(path),reason=reason,disposition='NOT_APPLICABLE_EXACT_CONFINEMENT_OR_FINITE_STANDALONE_FIXTURE'))
work=r.parent/'pgpt-runs/PG379/pg33824-ssc422-auth11-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for name in m[key]:policy.relative_name(name)
 assert {name:sha(work/folder/name) for name in m[key]}==m[key]
assert len(m['physicalClassHashes'])==183 and len(m['mainClassHashes'])==7
v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),static=ref(sp),expectedTests=11,newDefinitions=3,necessaryPriorDefinitions=8,physicalClasses=183,sourceMain5=5,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,rootNullAwayFresh=True,old8SourcePrefixExact=True,defaultFactoryOriginalRecordConstructorFixed=True,nullableFactoryRejectedBeforeSecretCopy=True,internalFactoryTakesOnlyVersionAndCiphertext=True,pmdRaw24=24,classified=classified,declaredTargets=['dev/codex/schubert/nk/api/security/AuthContextCodec'],naturalAbstractFactoryExpectedCode0=True,manualSuppressionAdded=False,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False)
out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,wholeTests=11,rawSites=24,applicable=0,unclassified=0,old8PrefixExact=True)))
