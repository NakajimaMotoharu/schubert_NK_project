"""Exact80 physical scope and all18 per-site dispositions; zero product replay."""
from collections import Counter
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

r = Path.cwd(); sys.path.insert(0, str(r / 'tools/quality'))
import classfile_code_metadata as code
b = r / 'evidence/01_PT/018_NK-OPS-001/evidence'
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ref = lambda p: dict(path=str(p.relative_to(r)), sha256=sha(p))
mp = b / 'PG36820-storage-main-compile-v1/manifest.json'; m = load(mp)
sp = b / 'PG36822-storage-main-full-static-v1/manifest.json'; s = load(sp)
out = b / 'PG36824-storage-main-independent-v1'; assert not out.exists()
assert m['actualExit'] == s['actualExit'] == 0
assert s['prepare'] == ref(mp) and s['inputHashes'] == m['inputHashes']
assert s['stages']['pmd']['actualExit'] == 4 and s['stages']['spotbugs']['actualExit'] == 0
assert not any(v['timedOut'] for v in s['stages'].values())
for name, stage in s['stages'].items():
    assert sha(sp.parent / (name + '.stdout.log')) == stage['stdoutSha256']
    assert sha(sp.parent / (name + '.stderr.log')) == stage['stderrSha256']
assert not s['summary']['pmd']['processingErrors']
sb = s['summary']['spotbugs']
assert sb['bugs'] == 0 and sb['missingClasses'] == sb['errors'] == []
assert {x.replace('.', '/') + '.class' for x in sb['classStats']} == set(m['physicalClassHashes'])
work = Path(m['cwd']); root = work / 'src/schubert-nk-storage/target/classes'
assert {str(p.relative_to(root)):sha(p) for p in root.rglob('*.class')} == m['physicalClassHashes']
assert len(m['physicalClassHashes']) == 80
inventory = {name:code.decode((root / name).read_bytes(), name) for name in m['physicalClassHashes']}
assert all(sha(r / p) == h == sha(work / p) for p,h in m['inputHashes'].items())
assert all(hashlib.sha256(subprocess.check_output(['git','show',m['sourceCore']+':'+p])).hexdigest()==h
           for p,h in m['inputHashes'].items())
assert not list(work.rglob('surefire-reports'))
oldp = b / 'PG35546-ssc440-namespace39-preflight-v2/manifest.json'; old = load(oldp)
assert old['actualExit'] == old['staticApplicable'] == old['unclassified'] == 0
assert old['inputHashes']['src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java'] == m['inputHashes']['src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java']
raw = load(sp.parent / 'raw-findings.json')
previous = [x for x in old['classified'] if x['path'].endswith('/storage/ResourceScope.java')]
assert len(raw) == len(previous) == 18
key = lambda x: (x['path'],x['rule'],str(x.get('beginline',x.get('line'))),x['message'])
assert Counter(map(key,raw)) == Counter(map(key,previous))
assert all(x['disposition']=='NOT_APPLICABLE' and len(x['reason'])>50 for x in previous)
dispositions=[]
for index,x in enumerate(raw):
    prior=next(y for y in previous if key(y)==key(x))
    dispositions.append(dict(rawFindingIndex=index,raw=x,disposition='NOT_APPLICABLE',
      sourceSha256=m['inputHashes'][x['path']],reason=prior['reason'],
      currentContract='SS333 SSC063/308 explicit close-once, unknown primary identity, known IO versus unknown cleanup precedence, sanitized suppression; never success conversion',
      independentlyReviewedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      originalPerSiteReview=ref(oldp)))
doc='documents/300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md'
approved=subprocess.check_output(['git','show','origin/main:'+doc])
assert all(x.encode() in approved for x in ['SSC308','bodyが未知Runtime/Errorの場合は同じprimaryを保持','closeの元unknownを優先'])
policy=(r/'pom.xml').read_text()
assert all(x in policy for x in ['-Xep:NullAway:ERROR','JSpecifyMode=true','-Werror','--should-stop=ifError=FLOW'])
prior_prepare=load(b/'PG35542-ssc440-namespace39-prepare-v2/manifest.json')
shared={n:h for n,h in prior_prepare['physicalClassHashes'].items() if '/storage/' in n}
assert len(shared)==7 and all(m['physicalClassHashes'].get(n)==h for n,h in shared.items())
quality=ref(b/'PG35568-ssc440-namespace39-quality-join-v2/manifest.json')
format_post=b/'PG36814-six-main-maven-validate-independent-v1/manifest.json'
assert load(format_post)['actualExit']==0 and load(format_post)['source']==m['sourceCore']
out.mkdir()
(out/'pmd18-site-dispositions.json').open('x').write(json.dumps(dispositions,ensure_ascii=False,indent=2)+'\n')
(out/'physical80-code-inventory.json').open('x').write(json.dumps(inventory,indent=2)+'\n')
result=dict(actualExit=0,source=m['sourceCore'],sourceDomain='STORAGE25_MAIN_STATIC_ONLY_NOT_WHOLE_PRODUCT_PT',
 terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),compile=ref(mp),static=ref(sp),
 normalMavenFormat=ref(format_post),mainCount=25,physicalClassStats=80,
 pmdRaw=18,pmdClassified=18,pmdApplicable=0,pmdUnclassified=0,pmdProcessingErrors=0,
 spotbugs=dict(bugs=0,missingClasses=0,errors=0,all80ClassStats=True),
 originalToolInputs=s['toolHashes'],fullOriginalRuleset=s['fullRulesetSha256'],
 approvedDesign=dict(path='origin/main:'+doc,sha256=hashlib.sha256(approved).hexdigest()),
 prior39Reuse=dict(quality=quality,byteIdenticalStoragePhysical=7,old39Replayed=0,
   use='REFERENCE_ONLY_FOR_UNCHANGED_RESOURCE_SCOPE_AND_EXCEPTION_NOT_ALL80_COVERAGE'),
 productTestsExecuted=0,actualNativeDbVmServiceActions=0,heldClassfileActions=0,
 wholeStorageCoverageAccepted=False,wholeF03Accepted=False,newAcceptance=0,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,main=25,allPhysical=80,pmdClassified=18,applicable=0,
 spotbugsIssues=0,newProductTests=0,old39Replay=0)))
