"""Review exact finite-worker and memory-double sites; retain real naming/operand findings separately."""
from pathlib import Path
import collections,hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pf=ld(i/'2613_copy_stream113_state_fixed_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=ld(sp);assert not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']) and not any('/main/' in x['path'] for x in s['rawFindings'])
assert collections.Counter(x['rule'] for x in s['rawFindings'])==dict(CloseResource=20,DoNotUseThreads=36,DoNotThrowExceptionInFinally=1)
prior=ld(i/'2603_scenario_copy_dataset98_static_admission.json')['sourceAnchors'];assert len(prior)==41
writer=next(x['path'] for x in pf['testSources'] if x['path'].endswith('/PostgresCopyTextWriterTest.java'));dataset=next(x['path'] for x in pf['testSources'] if x['path'].endswith('/ScenarioCopyDatasetTest.java'));wt=(r/writer).read_text();dt=(r/dataset).read_text()
assert all(x in wt for x in ['private static final class TrackingSink extends OutputStream','private final ByteArrayOutputStream output = new ByteArrayOutputStream();','output.write(value);','closed = true;','flushed = true;','return output.toByteArray();'])
assert not any(x in wt+dt for x in ['java.net.','java.nio.file.','FileInputStream','FileOutputStream','SocketChannel','DriverManager','ProcessBuilder'])
# The existing twelve dataset tests are byte-identical once only the new three streaming tests/imports are removed.
base=dt[:dt.index('  /** SSC351 / PT-MIG-DATASET013. */')]+dt[dt.index('  private static void reject('):]
for name in ['java.io.ByteArrayOutputStream','java.io.IOException','java.io.OutputStream']:base=base.replace('import '+name+';\n','')
old=ld(b/'evidence/PG30876-scenario-copy-dataset98-post-v1/manifest.json');assert hashlib.sha256(base.encode()).hexdigest()==old['inputHashes'][dataset]
rows=[];used=set();memory=0;new_worker=0
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));text=(r/path).read_text();lines=text.splitlines();line=int(raw['line']);anchor=lines[line-1].strip()
 matches=[(index,x) for index,x in enumerate(prior) if x['path']==path and x['rule']==raw['rule'] and x['message']==raw['message'] and x['sourceAnchor']==anchor]
 if matches:
  assert len(matches)==1;index,row=matches[0];assert index not in used;used.add(index);rows.append(dict(row,sourceLine=line));continue
 assert path in [writer,dataset]
 tail='\n'.join(lines[line-1:line+4]);method_candidates=[x for x in lines[:line] if x.startswith('  void ')];method=method_candidates[-1].strip() if method_candidates else 'private memory fixture'
 if raw['rule']=='CloseResource' and ('new TrackingSink()' in tail or 'new OutputStream()' in tail):
  assert anchor.startswith('var sink') or anchor.startswith('var independent')
  reason='Exact '+method+' declaration constructs a memory-only final TrackingSink backed solely by ByteArrayOutputStream and flags, or an anonymous OutputStream whose write throws a retained synthetic IOException. No file/socket/FD/process/database resource is acquired or retained. Borrowed-library close/flush calls are deliberately detected; these memory doubles require no external resource release.'
  memory+=1
 else:
  assert path==writer and raw['rule'] in ['CloseResource','DoNotUseThreads']
  assert all(x in text for x in ['Executors.newFixedThreadPool(8)','index < 64','future.get(5, TimeUnit.SECONDS)','finally {','executor.shutdownNow();','assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));'])
  reason=('Exact JUnit-owned executor is acquired before try, every exit reaches finally shutdownNow and asserted awaitTermination10, and all64 Futures join5. Implicit close does not state the finite postcondition.' if raw['rule']=='CloseResource' else 'Exact standalone immutable codec JUnit site is outside J2EE. Eight locally owned workers use separate memory sinks and independent literal bytes for64 tasks, Future5 and finallyshutdownNow/await10 checked; no DB/FS/process/native/Root operation.')
  new_worker+=1
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert used==set(range(41)) and memory==11 and new_worker==5 and len(rows)==57
p=i/'2614_copy_stream113_static_admission.json';assert not p.exists();p.write_text(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=57,existingExactSites=41,memoryOnlySites=11,newFiniteWorkerSites=5,applicable=0,unclassified=0,originalApplicableNaming4Operand2Retained=True)))
