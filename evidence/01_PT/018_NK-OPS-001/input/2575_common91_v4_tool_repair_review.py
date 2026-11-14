"""BUG2880/2881 regression of bounded collector and immutable payload metadata, not product PT."""
from pathlib import Path
import ast,datetime,hashlib,importlib.util,io,json,subprocess,sys,tarfile
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input'
w=r.parent/'pgpt-runs/PG379/pg30740-v4-tool-review';e=b/'evidence/PG30740-common91-v4-tool-repair-review-v1'
assert not w.exists() and not e.exists();w.mkdir(mode=0o700);e.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=[i/'2564_haruka_common60_remote.py',i/'2565_haruka_common60_controller.py']
for p in paths:compile(p.read_text(),str(p),'exec')
controller=ast.parse(paths[1].read_text());boot=[n.value.value for n in ast.walk(controller) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='bootstrap' for x in n.targets)][0]
compile(boot,'<v4-bootstrap>','exec')
timestamp=int(subprocess.check_output(['git','show','-s','--format=%ct','f9f9d28f23833257be991d142e105ec4533f7be8'],text=True));assert timestamp>0
blob=io.BytesIO()
with tarfile.open(fileobj=blob,mode='w') as t:
 info=tarfile.TarInfo('public.json');info.size=2;info.mode=0o600;info.mtime=timestamp;t.addfile(info,io.BytesIO(b'{}'))
blob.seek(0)
with tarfile.open(fileobj=blob) as t:
 t.extractall(w/'epoch-positive',filter='data')
assert int((w/'epoch-positive/public.json').stat().st_mtime)==timestamp
spec=importlib.util.spec_from_file_location('collector_regression',paths[0]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
fake=w/'incomplete-own-terminal';fake.mkdir();(fake/'unit-result.json').write_text('{"actualExit":1}');(fake/'stage.json').write_text('{"sourceCommit":"synthetic-independent-collector-fixture"}')
target=fake/'payload/source/program/characterization/target/classes/dev/codex/schubert/characterization';target.mkdir(parents=True)
(target/'unexpected-name-only.class').symlink_to('/do-not-open-unknown-class')
output=io.BytesIO();original=sys.stdout
class Capture:
 buffer=output
try:
 m.RUN=fake;sys.stdout=Capture();m.collect()
finally:sys.stdout=original
output.seek(0)
with tarfile.open(fileobj=output) as t:
 names=t.getnames();report=json.load(t.extractfile('collection-manifest.json'))
assert 'payload/source/program/characterization/target/site/jacoco/jacoco.xml' in report['missing']
assert any(n.endswith('TEST-dev.codex.schubert.characterization.GateCliTest.xml') for n in report['missing'])
assert report['unexpectedClassNames']==['payload/source/program/characterization/target/classes/dev/codex/schubert/characterization/unexpected-name-only.class']
assert not any('unexpected-name-only' in n for n in names) and report['collectionIsNotUnitAcceptance'] is True
closure=json.loads((b/'evidence/PG30718-common91-whole-source-closure-and-independent-inverses-v1/manifest.json').read_text())
same=[]
for name in closure['allSelectedMainPaths']+closure['allSelectedTestPaths']+[closure['fullTestHelperPath'],'pom.xml','program/characterization/pom.xml']:
 fixed=subprocess.check_output(['git','show','f9f9d28f23833257be991d142e105ec4533f7be8:'+name]);assert fixed==(r/name).read_bytes();same.append(dict(path=name,sha256=sha(r/name)))
result=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),bugs=['BUG-2880','BUG-2881'],syntheticToolRegressions=['positive-fixed-archive-mtime-retained','missing-coverage-and-XML-collected-as-missing','unknown-class-symlink-name-recorded-without-open'],sourceSyntaxAndBootstrapValid=True,unchangedJavaAndPoms=same,toolHashes={str(p.relative_to(r)):sha(p) for p in paths},standardMavenResourceGateBeforeUnit=True,productTestsExecuted=0,remoteConnections=0,formalAccepted=False,originalFailed91Retained=True,actualV4QualificationPending=True)
(e/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
for ledger,heading,note in [('915_障害表.md','## BUG-2881','原因確定: custom TarInfo.mtime既定0。maven-filtering3.3.1は欠落dest.lastModified0 >= source0でcopyをskip。PG30738 vendor独立再現でepoch0欠落/正timestamp bytecopyを実証。v4はGit固定positive commit timestampを全headerに設定/展開後照合、標準process-test-resources出力7hashをUnit前検査。POM/loader/oracle/Main変更0。PG30740工具回帰0、実v4再試験未のためOPEN。'),('916_横展開管理台帳.md','## YKT-2414','対象全7JSONに同じ正immutable metadataと標準copy後hash gateを適用。PG30738原因再現/PG30740 header境界確認、実Maven全7copy/原91再試験/独立post未でOPEN。'),('915_障害表.md','## BUG-2880','PG30734 readonly保存で元91/F0E29S0/真正Maven1を回収、v4 collectorは欠落reportをmanifestへ明示し残る元XMLを保持。PG30740 missing coverage/XML+未知class symlink非読取の独立negative確認0。実v4 collector未、当障害OPEN。')]:
 p=r/'documents/900_OTHER/910_台帳'/ledger;text=p.read_text();at=text.index(heading);end=text.find('\n## ',at+1);end=len(text) if end<0 else end;text=text[:end]+'\n\n2026-11-14追記: '+note+'\n'+text[end:];p.write_text(text)
print(json.dumps(dict(actualExit=0,toolRegressionConditions=3,unchangedJavaAndPoms=len(same),productTestsExecuted=0,normalV4Pending=True)))
