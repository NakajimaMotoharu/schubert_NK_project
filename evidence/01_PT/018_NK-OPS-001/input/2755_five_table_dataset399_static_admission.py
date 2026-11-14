"""Exact old157 same-byte static sites plus eight new memory/finite-worker sites, no tool filter changes."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2754_five_table_dataset399_immutable_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);assert len(s['spotbugs']['classStats'])==35 and len(s['rawFindings'])==165
prior={}
for name in ['2743_scenario_generated129_static_admission.json','2731_generated_contract170_static_admission.json','2653_audio_dataset120_static_admission.json','2722_asset_staging68_static_admission.json']:
 a=load(i/name);p=r/a['static']['path'];assert sha(p)==a['static']['sha256'];old=load(p)
 for row in a['sourceAnchors']:
  key=(row['path'],row['rule'],row['sourceLine'],row['sourceAnchor'],row['message']);assert sha(r/row['path'])==old['inputHashes'][row['path']];prior[key]=row
assert len(prior)==157;new=next(x['path'] for x in pf['testSources'] if x['path'].endswith('/MigrationCopyDatasetTest.java'));text=(r/new).read_text();assert 'private static final class MemorySink extends OutputStream' in text and 'private final ByteArrayOutputStream output = new ByteArrayOutputStream();' in text;assert all(x not in text for x in ['java.net.','java.nio.file.','DriverManager','DataSource','ProcessBuilder','FileOutputStream'])
assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','Executors.newFixedThreadPool(WORKERS)','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
rows=[];seen=set();newcounts=collections.Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path!=new:
  assert key in prior and key not in seen;seen.add(key);rows.append(prior[key]);continue
 if raw['rule']=='CloseResource' and 'executor' not in anchor:
  assert anchor=='for (var sink : sinks) {' or anchor.startswith('var faulty = new MemorySink(')
  reason='Exact memory-only final MemorySink owns only ByteArrayOutputStream, a synthetic IOException and integer flags/shared per-test trace list. It acquires no external file/socket/FD/database handle. The loop checks deliberately zero close/flush counts; failing sink tests assert prefix and original IOException, and closing a borrowed sink would change the contract under test.';newcounts['memory']+=1
 else:
  assert raw['rule'] in ['CloseResource','DoNotUseThreads'];reason='Exact host standalone JUnit-owned executor uses eight workers/64 independent in-memory five-stream copies; all Futures join5 and finally shutdownNow plus asserted awaitTermination10 run on every path. No J2EE managed executor, real IO, DB, native, Root, remote, permission or deployment action. Implicit close omits the finite cleanup postcondition.';newcounts['worker']+=1
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert seen==set(prior) and newcounts==dict(memory=3,worker=5)
p=i/'2755_five_table_dataset399_static_admission.json';p.open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,oldExactByteSites=157,memorySites=3,finiteWorkerSites=5,rawPmd=165,rawSpotbugs=0,applicable=0,unclassified=0)))
