"""Review every raw site; no PMD suppression, source exclusion or automatic name-based waiver."""
from pathlib import Path
import json,hashlib
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pf=ld(i/'2553_entry_copy_batch72_fixed_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=ld(sp);assert not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);assert not any('/src/main/' in x['path'] for x in s['rawFindings'])
anchors=ld(i/'2508_entry_file_closed36_static_admission.json')['sourceAnchors']+ld(i/'2534_scenario_copy_row24_static_admission.json')['sourceAnchors'];assert len(anchors)==26
test=pf['testSources'][0]['path'];source=(r/test).read_text();assert 'Executors.newFixedThreadPool(8)' in source and 'index < 64' in source and 'future.get(5, TimeUnit.SECONDS)' in source and 'finally {' in source and 'executor.shutdownNow();' in source and 'assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));' in source
raw=[x for x in s['rawFindings'] if x['path']==str(r/test)];assert len(raw)==5 and sorted(x['rule'] for x in raw)==['CloseResource']+['DoNotUseThreads']*4
for x in raw:
 line=int(x['line']);anchor=source.splitlines()[line-1].strip();assert anchor and source.count(anchor)==1
 reason=('This exact private executor is acquired before try and every exit executes finally shutdownNow/awaitTermination10 with failing assertion. All64 Futures join5; implicitclose has no explicit finite termination postcondition.' if x['rule']=='CloseResource' else 'This exact pure immutable mapping-row JUnit site is not a J2EE-managed webapp. Eight owned workers execute64 fixed independent golden byte assertions; each Future5 and finallyshutdownNow/await10 is checked. No DB/FS/process/native/Root/service use.')
 anchors.append(dict(path=test,rule=x['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=x['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert len(anchors)==len(s['rawFindings'])==31
for a in anchors:
 text=(r/a['path']).read_text();assert text.count(a['sourceAnchor'])==a['occurrences']
out=i/'2554_entry_copy_batch72_static_admission.json';assert not out.exists();out.write_text(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=anchors),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=31,mainApplicable=0,perSiteSourceAnchors=31,unclassified=0,suppressionOrExclusions=0)))
