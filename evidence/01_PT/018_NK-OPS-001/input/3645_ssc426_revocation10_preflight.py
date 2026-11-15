"""Adjudicate exact static sites against explicit JDBC ownership and independent original8 oracles."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pp=b/'evidence/PG34076-ssc426-revocation10-prepare-v1/manifest.json';sp=b/'evidence/PG34078-ssc426-revocation10-static-v1/manifest.json';cp=b/'evidence/PG34074-ssc426-source-oracle-inverse-v1/manifest.json';m=ld(pp);st=ld(sp);closure=ld(cp);out=b/'evidence/PG34080-ssc426-revocation10-preflight-v1';assert not out.exists();assert m['actualExit']==st['actualExit']==closure['actualExit']==0 and m['expectedTests']==10 and len(m['apiMainSources'])==17 and len(m['apiTestSources'])==1 and m['MainSafeClosureRebuilt'];assert m['inputHashes']==st['inputHashes'] and all(sha(r/n)==h for n,h in m['inputHashes'].items())
for obj,slot in [(m,pp.parent),(st,sp.parent)]:
 for label,v in obj['stages'].items():
  assert type(v['actualExit']) is int and v['actualExit']=={'pmd':4,'spotbugs':1}.get(label,0) and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert st['processingErrors']==[] and st['checkstyleFindings']==0 and st['spotbugs']['bugs']==2 and st['spotbugs']['errors']==st['spotbugs']['missing']==0
expected={'JdbcResourceCleanup.java':{'AvoidCatchingGenericException':[30,30,42,42,54,54]},'AuthSessionRevocationService.java':{'CloseResource':[75,84,107,117,217,225,245,253,317],'AvoidCatchingGenericException':[88,88,95,95,155,155,162,162,229,229,236,236,257,257,264,264,328,328]},'ContextHash.java':{'AvoidSynchronizedStatement':[55]},'SessionAuditWriter.java':{'CloseResource':[41],'AvoidCatchingGenericException':[59,59]},'SessionRevocationJdbcPortTest.java':{'UseProperClassLoader':[87],'UseConcurrentHashMap':[93,170],'CloseResource':[473,749],'DoNotUseThreads':[749,755,780,781]}};wanted=sorted((n,k,str(x)) for n,v in expected.items() for k,lines in v.items() for x in lines);assert len(wanted)==46 and sorted((Path(x['path']).name,x['rule'],x['line']) for x in st['rawFindings'])==wanted;classified=[]
for x in st['rawFindings']:
 p=Path(x['path']);s=p.read_text();line=s.splitlines()[int(x['line'])-1];name=p.name;rule=x['rule']
 if rule=='AvoidCatchingGenericException':
  assert 'SQLException | RuntimeException | Error failure' in line
  reason='Exact TWR failure preservation: body immediately rethrows identical SQL/runtime/fatal, finally typed cleanup suppresses on original primary or propagates original close failure; no normal conversion or generic Exception catch. Same helper contract separately qualified by direct synthetic SQL/RTE/Error/alias tests.'
 elif rule=='CloseResource' and name in ['AuthSessionRevocationService.java','SessionAuditWriter.java']:
  assert 'JdbcResourceCleanup.closeStatement(' in s and 'requireValue(' in s
  reason='Owned nonnull resource local has explicit immediate primary/finally with typed WillClose closeStatement/closeRows. Each valid resource closes once; null creates no resource, borrowed Connection never closed. PMD lexical TWR recognition lacks this explicit helper model; original8 and newNull2 verify exact resource counts/SQL/TX ownership.'
 elif name=='ContextHash.java':
  assert 'synchronized (stateLock)' in s and 'private final Object stateLock' in s
  reason='Existing private lock is necessary to keep shared digest/format atomic and unexposed to caller monitors; same previously qualified Hash6 source, no change.'
 elif rule=='UseProperClassLoader':
  assert 'type.getClassLoader()' in s
  reason='Only hardcoded JDK Connection/PreparedStatement/ResultSet dynamic proxies use their defining interface loader; no class-name discovery/private reflection/backend driver or held-type replacement.'
 elif rule=='UseConcurrentHashMap':
  assert 'final Map<String, @Nullable Object> fields = new HashMap<>();' in s and 'Map<Integer, Object> bound = new HashMap<>();' in s
  reason='Each distinct worker owns its Fixture fields and statement binding map, parent reads only after bounded Future completion; shared service has no map state. No concurrent mutable-map access exists.'
 elif rule=='CloseResource' and x['line']=='473':
  assert line.strip()=='var c = f.connection();'
  reason='This is an in-memory JDK Connection proxy with no backend/handle/resource; close/commit/rollback are forbidden assertions proving service never owns caller TX. Its fixture owns no actual connection requiring release. Calling close would break the explicit negative ownership oracle.'
 else:
  assert name=='SessionRevocationJdbcPortTest.java' and rule in ['DoNotUseThreads','CloseResource'];assert 'workers.shutdownNow();' in s and 'assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));' in s
  reason='Standalone JUnit, not J2EE. One fixed pool owns 16 independent synthetic calls, each Future.get5 and finally shutdownNow/await10 asserted plus Timeout30. Failed termination cannot pass; no worker releases another worker owned state.'
 classified.append(dict(**x,sourceLine=line,sourceSha256=sha(p),disposition='NOT_APPLICABLE_EXACT_OWNER_OR_FAKE_FIXTURE_CONTRACT',reason=reason))
sb=[];specs={('dev.codex.schubert.nk.api.security.AuthSessionRevocationService','update'):'319',('dev.codex.schubert.nk.api.security.SessionAuditWriter','write'):'43'}
required=r/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/database/RequiredColumn.java';guard=required.read_text();assert 'if (value == null)' in guard and 'throw new SQLDataException' in guard and 'return value;' in guard
for bug in ET.parse(sp.parent/'spotbugs.xml').findall('.//BugInstance'):
 key=(bug.find('Class').get('classname'),bug.find('Method').get('name'));assert key in specs and bug.get('type')=='OBL_UNSATISFIED_OBLIGATION_EXCEPTION_EDGE' and bug.find('SourceLine').get('start')==specs[key];path=r/('src/schubert-nk-api/src/main/java/'+key[0].replace('.','/')+'.java');s=path.read_text();assert 'requireValue(' in s and 'JdbcResourceCleanup.closeStatement(' in s;sb.append(dict(className=key[0],method=key[1],line=specs[key],type=bug.get('type'),source=ref(path),guard=ref(required),disposition='FALSE_POSITIVE_NULL_ONLY_CHECKED_GUARD_EDGE',reason='The only checked exception between prepareStatement result and protected body is requireValue. Its actual source throws only for null, where no acquired resource exists; every nonnull object returns identically without throwing and enters explicit finally. Raw XML retained, no suppression/exclusion. Null X/L cases and original8 close-failure cases verify the two sides independently.'))
assert len(sb)==2 and closure['originalEightAssertionsInverseFormattedExact'];work=r.parent/'pgpt-runs/PG379/pg34076-ssc426-revocation10-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for n in m[key]:policy.relative_name(n)
 assert {n:sha(work/folder/n) for n in m[key]}==m[key]
assert len(m['physicalClassHashes'])==196 and len(m['mainClassHashes'])==20 and {v.replace('.','/')+'.class' for v in st['spotbugs']['classStats']}==set(m['mainClassHashes']);assert all(sha(Path(p))==h for p,h in m['dependencies'].items());v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),static=ref(sp),expectedTests=10,newDefinitions=2,necessaryPriorDefinitions=8,physicalClasses=196,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugsApplicable=0,spotbugsRaw=2,spotbugsConcreteAdjudications=sb,rootNullAwayFresh=True,original8InverseExact=True,sourceInverse=ref(cp),pmdRaw46=46,classified=classified,declaredTargets=closure['targets'],manualSuppressionAdded=False,liveDbSessionDriverOrHeldActions=0,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False);out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=10,pmdRaw=46,spotbugsRaw=2,applicable=0,unclassified=0,physical=196)))
