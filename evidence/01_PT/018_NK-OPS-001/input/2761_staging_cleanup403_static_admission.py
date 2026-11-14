"""Review explicit primary-preserving JDBC cleanup, retaining all tool findings and old Test prefixes."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2760_staging_cleanup403_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);assert len(s['rawFindings'])==185 and len(s['spotbugs']['classStats'])==35
oldad=load(i/'2755_five_table_dataset399_static_admission.json');oldstatic=load(r/oldad['static']['path']);prior={(x['path'],x['rule'],x['sourceLine'],x['sourceAnchor'],x['message']):x for x in oldad['sourceAnchors'] if '/test/' in x['path']};assert len(prior)==163
proof=b/'evidence/PG31558-staging-nonnull-cleanup-four-source-v1';changed={}
for name in ['ScenarioStagingTables','AssetStagingTables']:
 path='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/'+name+'Test.java';old=(proof/(name+'Test.before.txt')).read_text();assert (r/path).read_text().startswith(old[:-2]);assert hashlib.sha256(old.encode()).hexdigest()==oldstatic['inputHashes'][path];changed[path]=old
rows=[];seen=set();counts=collections.Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));text=(r/path).read_text();lines=text.splitlines();line=int(raw['line']);anchor=lines[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if '/test/' in path:
  if path not in changed:assert sha(r/path)==oldstatic['inputHashes'][path]
  else:assert line<=len(changed[path].splitlines())-1
  assert key in prior and key not in seen;seen.add(key);rows.append(prior[key]);continue
 assert path.endswith(('/ScenarioStagingTables.java','/AssetStagingTables.java'))
 assert text.count('finally {')==3 and text.count('closeStatement(statement, primary);')==2 and text.count('closeResult(result, primary);')==1
 if raw['rule']=='AvoidCatchingGenericException':
  tail='\n'.join(lines[line-1:line+4]);assert raw['message'] in ['Avoid catching RuntimeException in try-catch block','Avoid catching Error in try-catch block']
  if ' failure)' in anchor:
   assert 'primary = failure;' in tail and 'throw failure;' in tail and 'finally {' in tail
   reason='Exact SSC366 resource-ownership catch preserves the same SQL/runtime/Error instance only to record the primary before its finally cleanup; it immediately rethrows and never logs, normalizes, retries, commits or returns success. This explicitly implements the Java TWR primary/suppressed contract for a nonnull owned JDBC Statement/ResultSet. All legal unchecked failures, including NPE, remain failures; independent body/cleanup dual-fault tests and whole scope verify identity and one close.';counts['primary']+=1
  else:
   assert ' cleanup)' in anchor and 'primary.addSuppressed(cleanup);' in tail
   reason='Exact private typed cleanup helper is reached only from one of the six owned-resource finally blocks with a nonnull original primary already being rethrown. It catches cleanup SQL/runtime/Error only to attach the identical instance as suppressed, preserving Java TWR order and the original failure; standalone cleanup failures propagate directly. It does not swallow application errors into normal execution, and independent Result-then-Statement dual-fault assertions verify both instances and close counts.';counts['cleanup']+=1
 else:
  assert raw['rule']=='CloseResource' and anchor=='@Nullable Statement created = connection.createStatement();'
  assert 'if (created == null) throw invalid();' in text and text.count('Statement statement = created;')==2
  reason='Exact nullable JDBC acquisition is checked immediately: null creates no ownership and fails; nonnull is aliased once to statement and enclosed by a finally calling closeStatement(statement, primary). Both normal and all SQL/runtime/Error body exits close that same Statement exactly once with primary/suppressed preservation; connection is borrowed and never closed. The intraprocedural rule does not follow this private typed close helper; whole SQL/fault fixtures and four added dual-fault cases verify the resource postcondition.';counts['resource']+=1
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert seen==set(prior) and counts==dict(primary=12,cleanup=8,resource=2)
p=i/'2761_staging_cleanup403_static_admission.json';p.open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,priorExactTestSites=163,explicitPrimaryCatchSites=12,suppressedCleanupCatchSites=8,privateFinallyCloseSites=2,rawPmd=185,applicable=0,unclassified=0,rawSpotbugs=0)))
