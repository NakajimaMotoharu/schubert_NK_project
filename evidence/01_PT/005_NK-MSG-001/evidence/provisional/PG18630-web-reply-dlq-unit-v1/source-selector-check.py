from pathlib import Path
import copy,hashlib,json,re,shutil,subprocess
R=Path('/home/mini/codex/project1/work/pgpt-foundation');S=Path(__file__).parent;O=R/'evidence/01_PT/005_NK-MSG-001/evidence/provisional/PG18630-web-reply-dlq-unit-v1';D=R/'documents/400_PGPT/470_PMO/500_SV計画整備_20261104';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();m=json.loads((O/'manifest.json').read_text());before=H(O/'manifest.json');assert before=='290487e3bcbe8d6fdba9ea12e340067d5225f25b817382fa3cd1967780697fdd';path=m['inputProvenance']['testInputPath'];text=(R/path).read_text();assert H(R/path)==m['inputProvenance']['testInputHash'];pkg=re.search(r'^package ([A-Za-z0-9_.]+);',text,re.M).group(1);cls=re.search(r'^final class ([A-Za-z0-9_]+) \{',text,re.M).group(1);name=pkg+'.'+cls;assert subprocess.check_output(['git','show',m['testSource']+':'+path],cwd=R)==text.encode()
def check(value):
 assert '--select-class='+name in value['actualStages'][0]['command']
 assert all(c['classname']==name for c in value['cases'])
 assert len(value['cases'])==8 and value['inputProvenance']['testInputHash']==H(R/path)
check(m);labels=[]
for label,mutation in [('duplicatedPrefix',lambda x:x['cases'][0].update(classname=pkg+'.ArtemisReply'+cls)),('wrongSelector',lambda x:x['actualStages'][0]['command'].__setitem__(-1,'--select-class=UNKNOWN')),('wrongSourceHash',lambda x:x['inputProvenance'].update(testInputHash='0'*64))]:
 bad=copy.deepcopy(m);mutation(bad)
 try:check(bad)
 except AssertionError:labels.append(label)
 else:raise AssertionError(label)
old=[]
for run in ['pg18622-dlq-sender-unit-v1','pg18612-reply-stage-unit-v1']:
 p=S.parent/run/'post.py';body=p.read_text();literal=re.search(r"classname='([^']+)'",body).group(1);raw=json.loads((p.parent/'manifest.safe.json').read_text());t=(R/raw['begin']['testInputPath']).read_text();decl=re.search(r'^package ([A-Za-z0-9_.]+);',t,re.M).group(1)+'.'+re.search(r'^final class ([A-Za-z0-9_]+) \{',t,re.M).group(1);assert literal==decl and '--select-class='+decl in raw['stages'][0]['command'];old.append(dict(run=run,postSha256=H(p),testSource=raw['testSource'],className=decl,reason='No overlapping rename; existingliteral matches frozenSource and ownactualselector',productOrPostReexecuted=False))
assert H(S/'post-attempt1.py')=='cd28b610d2bf1674258cf322d6eefcddfb646b53b69bac78b549c30963105670'
for filename in ['post-attempt1.py','source-selector-check.py']:shutil.copyfile(S/filename,O/filename)
supplement=dict(actualExit=0,source=m['source'],testSource=m['testSource'],sourceDeclaredClass=name,sourceGitByteMatch=True,originalFailure='73cd40/1 beforepublicwrites',originalQualifiedManifestBeforeSupplement=before,negativeLabels=labels,oldPostNonapplicability=old,productTestsOrOldPostsReexecuted=0,fixBug='BUG2262',horizontal='YKT2007',checkerSha256=H(__file__))
m['sourceSelectorSupplement']=supplement
for filename in ['post-attempt1.py','source-selector-check.py']:m['files'][filename]=H(O/filename)
(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');p=next(D.glob('685_*.json'));d=json.loads(p.read_text());d['publicManifestSha256']=H(O/'manifest.json');d['sourceEvidenceRefs'][0]['sha256']=H(O/'manifest.json');d['sourceSelectorSupplement']=supplement;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,newManifestSha256=H(O/'manifest.json'),negativeLabels=labels,oldPostsNonapplicable=len(old),productTestsReexecuted=0),ensure_ascii=False))
