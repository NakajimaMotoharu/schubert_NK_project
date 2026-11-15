"""Exact current manual cleanup and whole independent host test applicability, no rule suppression."""
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,re
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest());pf=load(i/'3345_admin_encoding29_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp)
assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
old=load(i/'3320_admin_boundary27_static_admission.json');by=defaultdict(list)
for x in old['sourceAnchors']:by[(x['path'],x['rule'],x['sourceAnchor'],x['message'])].append(x)
main='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/admin/BootstrapAdminService.java';code=(r/main).read_text();rows=[];counts=Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();rule=raw['rule'];key=(path,rule,anchor,raw['message'])
 if path==main:
  if rule=='AvoidCatchingGenericException':
   assert anchor=='} catch (SQLException | RuntimeException | Error failure) {'
   before='\n'.join(code.splitlines()[:line]);matches=list(re.finditer(r'^  (?:public|private) (?:static )?[^\n]*\b(\w+)\([^;\n]*',before,re.M));method=matches[-1].group(1);assert method in ['create','query','read','lockMembership','audit','closeStatement','closeResult']
   reason='SSC412 explicitly requires exact SQL/Runtime/Error primary preservation across the owned Statement/ResultSet cleanup scope '+method+'. Catch body stores and rethrows the identical primary; finally attempts the already-held resource once. Close helpers rethrow standalone close failure, or attach only a distinct secondary while the outer primary remains pending. They never convert failure into normal completion or catalog, catch NPE for success, retry or assume caller TX ownership. All3 types/normal-close/secondary/self are independently exercised in wholeBOOTBOUND014..016; narrower SQL-only capture would omit primary ownership on Runtime/Error.';counts['requiredCleanupCatch']+=1
  else:
   assert rule=='CompareObjectsWithEquals' and anchor=='if (primary != failure) primary.addSuppressed(failure);'
   reason='Required Throwable identity comparison for JDK addSuppressed self guard. Same object must not self-suppress; distinct objects must be retained even if a Throwable subclass overrides value equals. Calling equals would conflate independent failures and violate SSC412 primary/secondary ownership. Both equal-identity and distinct cases are observed for SQL/Runtime/Error with separate Statement/ResultSet scopes.';counts['throwableIdentity']+=1
  x=dict(path=path,rule=rule,sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE')
 else:
  assert by[key],key;x=dict(by[key].pop(0));x['sourceLine']=line;x['reason']+=' Re-reviewed current SSC412 source: this exact original statement remains unchanged; current17 non-composite Boundary bodies and finite-worker/Port ownership remain byte-identical. Manual cleanup affects only SUT failure handling, not fixture sharing or JDK-interface loader policy.';counts['unchangedHostTestSites']+=1
 rows.append(x)
assert all(not v for v in by.values()) and len(rows)==29 and counts==Counter(requiredCleanupCatch=14,throwableIdentity=2,unchangedHostTestSites=13)
(i/'3346_admin_encoding29_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,raw=29,counts=dict(counts),applicable=0,unclassified=0))
