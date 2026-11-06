"""Export completed compile/static evidence only; no Java invocation, application or test execution."""
from pathlib import Path
import json,hashlib,shutil,xml.etree.ElementTree as E,collections,subprocess
R=Path.cwd();W=R.parent/'pgpt-runs/PG379';O=R/'evidence/01_PT/016_NK-WEB-002/evidence';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name,file,out in [('pg20592-question-return-green-static-v1','manifest.json','PG20592-question-return-green-static-v1'),('pg20589-question-menu-legacy-test-static-v1','manifest.safe.json','PG20589-legacy-sdk-original-failure-v1'),('pg20593-question-menu-legacy-test-corrected-static-v1','manifest.safe.json','PG20593-legacy-sdk-secondary-failure-v1'),('pg20594-question-menu-legacy-complete-sdk-static-v1','manifest.safe.json','PG20594-legacy-source-closure-failure-v1'),('pg20595-question-menu-legacy-closed-source-static-v1','manifest.safe.json','PG20595-legacy-source-closed-static-v1')]:
 s=W/name;d=O/out;assert not d.exists();m=json.loads((s/file).read_text());d.mkdir();files={}
 for p in s.iterdir():
  if p.name in {file,'pmd.xml','checkstyle.xml'} or p.name.endswith(('.safe.json','.stdout','.stderr')):
   assert p.is_file() and not p.is_symlink();q=d/('original-manifest.json' if p.name==file else p.name);shutil.copyfile(p,q);files[q.name]=sha(q)
 raw=[dict(rule=x.get('rule'),line=int(x.get('beginline')),method=x.get('method')) for x in E.parse(s/'pmd.xml').getroot().iter() if x.tag.endswith('violation')];counts=dict(collections.Counter(x['rule'] for x in raw));review=[]
 if name.startswith('pg20592'):
  assert counts=={'DoNotUseThreads':2}
  for x in raw:review.append(dict(**x,applicable=False,basis='Owned bounded two-worker JUnit concurrency rendering fixture; shutdown via try-with-resources; webapp thread prohibition does not apply to standalone Test.'))
 elif name.startswith('pg20595'):
  assert m['stages']['compile']['actualExit']==m['stages']['format']['actualExit']==m['checkstyleErrors']==0 and len(m['inputHashes'])==9
  assert counts=={'DoNotUseThreads':4,'UseProperClassLoader':3,'AvoidUsingVolatile':12,'CloseResource':1}
  why={'DoNotUseThreads':'Owned bounded JUnit concurrency fixture, not a container application worker. Dynamic fixture is HOLD, not executed here.', 'UseProperClassLoader':'JDK DataSource/Connection proxy must use the defining interface loader for assignability; no application class loading or deployment.', 'AvoidUsingVolatile':'Twelve fixture scalar/reference visibility cells only; compound counters use AtomicLong/AtomicInteger, buffers CopyOnWriteArrayList. Not a volatile replacement for atomic read-modify-write.', 'CloseResource':'Line1828 borrowed alias assigned from ownedForm within JLS try-with-resources. Owner closes on assertion failure as well. Alias is retained solely for explicit post-close rejection assertion; no resource escapes the method.'}
  review=[dict(**x,applicable=False,basis=why[x['rule']]) for x in raw]
 assert len(list(E.parse(s/'checkstyle.xml').getroot().iter('error')))==0
 result=dict(actualExit=0,originalCompileExit=m.get('stages',{}).get('compile',{}).get('actualExit'),files=files,rawPmd=raw,rawCounts=counts,individualApplicability=review,applicableViolations=0 if review else None,checkstyleErrors=0,testsExecuted=False,testStatus='NOT_RUN_STATIC_ONLY_NO_PASS',productionMainArtifactSource='70fb6768e76564022901874e294a659e2fe1506f',testSource='WORKTREE_INPUT_HASHES_PENDING_GIT_BYTE_POST',inputHashes=m['inputHashes'],originalSourceLabelCoversMainArtifactsOnly=True,noFailureConvertedToPass=True)
 (d/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(out,sha(d/'manifest.json'))
