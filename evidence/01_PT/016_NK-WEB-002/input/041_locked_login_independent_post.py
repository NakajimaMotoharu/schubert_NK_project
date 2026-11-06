"""Independent original-artifact/source/HTML comparison; no Java or business operation."""
from pathlib import Path
from html.parser import HTMLParser
import json,hashlib,re,subprocess,zipfile,datetime
import xml.etree.ElementTree as E
r=Path.cwd();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text());source='a777b0d1aebf0f35ea8f8b488a379316586e44f1';core='4217e14083c6ecac116216e08d57f4361eb2f12d'
pub=Path('evidence/01_PT/016_NK-WEB-002/evidence/PG21044-locked-login-display-resource-four-v1');m=load(pub/'manifest.json');assert sha(pub/'manifest.json')=='49348869da807cfb0a97c9241f1a8584c7a675fb59662bf213e8f8711b678ba0';assert m['source']==source and m['productionCoreMain']==core and m['tests']==4 and all(m[k]==0 for k in ['failures','errors','skipped','aborted']);assert m['productionJavaClasspath'] is False and m['javaCoverage'] is None and m['applicationInitializations']==[]
for name,h in m['files'].items():assert '..' not in Path(name).parts and sha(pub/name)==h
for name,h in m['inputHashes'].items():assert sha(name)==h==hashlib.sha256(subprocess.check_output(['git','show',source+':'+name])).hexdigest()
slot=Path(m['originalManifest']['path']).parent;raw=load(slot/'manifest.json');assert raw['actualExit']==0 and sha(slot/'manifest.json')==m['originalManifest']['sha256'];assert raw['stage']['actualExit']==0 and not raw['stage']['timedOut']
for suffix in ['stdout','stderr']:assert sha(slot/('unit.'+suffix))==raw['stage'][suffix+'Sha256']
cases=[]
for path,h in m['originalXmlPins'].items():
 assert sha(path)==h;tree=E.parse(path).getroot();assert all(int(tree.get(k,'0'))==0 for k in ['failures','errors','skipped'])
 for case in tree.findall('testcase'):
  assert not any(case.findall(x) for x in ['failure','error','skipped']);cases.append(case.get('name').removesuffix('()'))
assert sorted(cases)==m['testMethods'] and len(cases)==len(set(cases))==4
spec=Path('evidence/01_PT/016_NK-WEB-002/151_QA055固定locked画面単体仕様.md').read_text();pairs=re.findall(r'\|(PT-LOCK-DOM\d{3})\|(\w+)\|',spec);assert len(pairs)==4 and {n for _,n in pairs}==set(cases)
oracle=Path('evidence/01_PT/016_NK-WEB-002/input/040_locked_login_approved_oracle.json');o=load(oracle);assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+str(oracle)])).hexdigest()==sha(oracle);doc=o['design'];approved=subprocess.check_output(['git','show',o['canonicalDesignSource']+':'+doc['path']]);assert hashlib.sha256(approved).hexdigest()==doc['sha256'] and o['lockedMessage'] in approved.decode() and o['newDif'] is False and o['currentBaselineChanged'] is False
normal=load(r.parent/'pgpt-runs/PG379/pg20990-outbox-required-six-main-compile-v1/manifest.safe.json');assert normal['source']==core and normal['actualExit']==0;web=normal['jars']['web'];assert sha(web['path'])==web['sha256']==m['normalWebJarSha256']
with zipfile.ZipFile(web['path']) as z:
 for name,h in m['resourceHashes'].items():assert hashlib.sha256(z.read(name)).hexdigest()==h==sha('src/schubert-nk-web/src/main/resources/'+name)
class Messages(HTMLParser):
 def __init__(self):super().__init__();self.current=None;self.messages=[]
 def handle_starttag(self,tag,attrs):
  if tag=='p' and 'login-message' in dict(attrs).get('class','').split():self.current=[]
 def handle_data(self,text):
  if self.current is not None:self.current.append(text)
 def handle_endtag(self,tag):
  if tag=='p' and self.current is not None:self.messages.append(''.join(self.current).strip());self.current=None
locked=o['lockedMessage'];error='ユーザー名またはパスワードが正しくありません。';logout='ログアウトしました。';outputs=[]
for p in sorted((pub/'output').glob('*.html')):
 parser=Messages();text=p.read_text();parser.feed(text);match=re.fullmatch(r'LOCKDOM(\d{3})-(\d+)\.html',p.name);assert match;group,index=map(int,match.groups())
 if group==1:expected=[locked];assert 0<=index<3
 elif group==2:expected=([error] if index&1 else [])+[locked]+([logout] if index&2 else []);assert 0<=index<4
 elif group==3:expected=[locked];assert 0<=index<6
 else:assert group==4 and 0<=index<8;expected=[locked] if index%2==0 else []
 assert parser.messages==expected and 'public-unissued-fixture-marker' not in text and 'onerror=' not in text;outputs.append(dict(path=str(p),sha256=sha(p),expectedMessages=expected,actualMessages=parser.messages))
assert len(outputs)==m['snapshotCount']==o['expectedSnapshots']==21
static=Path('evidence/01_PT/016_NK-WEB-002/evidence/PG21038-locked-login-display-static-v1/manifest.json');s=load(static);assert s['pmdRaw']==2 and s['applicableViolations']==s['checkstyle']==s['processingErrors']==0 and s['inputHashes']==m['inputHashes'];assert all(row['rule']=='DoNotUseThreads' and row['applicable'] is False for row in s['classification'])
init=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));assert not any(n.startswith('dev/codex/schubert/nk/') and not n.startswith('dev/codex/schubert/nk/web/view/LockedLoginDisplayResourcePortTest') for n in init)
out=Path('evidence/01_PT/016_NK-WEB-002/evidence/PG21048-locked-login-independent-post-v1');assert not out.exists();out.mkdir();value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=source,productionCoreMain=core,originalPost=dict(path=str(pub/'manifest.json'),sha256=sha(pub/'manifest.json')),tests=4,testMethods=cases,sourceTestIds=pairs,snapshots=outputs,approvedOracle=dict(path=str(oracle),sha256=sha(oracle)),staticPost=dict(path=str(static),sha256=sha(static)),originalInitializationHash=sha(slot/'class-init.log'),checkerSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),checkerSha256=sha(__file__),productTestsReexecuted=0,productionJavaClasspath=False,javaCoverage=None,actualAuthenticationOrBrowser=False,headerBoundaryAccepted=False,newAcceptance=0,formalUpdated=False,effortRate=None);(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=4,snapshots=21,testsReexecuted=0,manifestSha256=sha(out/'manifest.json'))))
