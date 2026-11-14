"""Preserve this known pure-JUnit run's terminal artifacts; never restarts a test or touches old Root cohorts."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,re,tarfile,xml.etree.ElementTree as ET
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';l=r/'documents/900_OTHER/910_台帳';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
controller=i/'2565_haruka_common60_controller.py';spec=importlib.util.spec_from_file_location('pinned_common91_transport',controller);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
unit=b/'evidence/PG30730-haruka-common91-unit-raw-terminal-v3/manifest.json';u=json.loads(unit.read_text());assert u['sourceCommit']=='f9f9d28f23833257be991d142e105ec4533f7be8' and u['actualExit']==1 and u['ownedProcessGroupAbsent'] is True
collect=json.loads((m.W/'collect-local-terminal.json').read_text());assert collect['actualExit']==1
p=l/'915_障害表.md';assert max(map(int,re.findall(r'^## BUG-(\d+)\b',p.read_text(),re.M)))==2879
p.write_text(p.read_text()+'''\n\n## BUG-2880 PT 2026-11-14 new common91 tool collect / failed ordinary Maven terminal artifacts

重要度中・優先高。対象は正規haruka新run pg30726-common91-v3/Sourcef9f9の通常JUnit工具だけ、旧Root失敗cohortや拒否対象の回収ではない。期待: 終端1/未生成reportも明示し、存在する元XML/exec/静的をread-onlyに保存。実際: collect SSH1、bounded exact own-run artifact assertionでpartial tar24member（metadata/公開Main10class/execまで）を保存、coverage XML以降なし。原因: Maven失敗時にも全reportがある前提でcollectorがrequireし、欠測を構造化しなかった。Unit真正1/所有group消失trueを保持し、再起動0/型変更0/原payload上書き0。修正前起票、正規同peer/source/boot/inode/hashの当run既存file限定でoptional存在/欠測を別記し、XMLをproperties除去後に公開・原hash保存する。旧Raw/DB/鍵/VM/Unit/intent等はアクセスしない。YKT2413/451/SS355。修正commit/再試験/完了日未、状態OPEN。\n''')
p=l/'916_横展開管理台帳.md';assert max(map(int,re.findall(r'^## YKT-(\d+)\b',p.read_text(),re.M)))==2412
p.write_text(p.read_text()+'''\n\n## YKT-2413 BUG2880 failed ordinary report optionality

共通原因=成功時report存在を全終端で前提化。対象当runのcoverageXML・Jacocoexec・SpotBugs・JUnit全10XML・initlog・owner/source/terminal/static/admission metadata。検索=新collectorの全追加順/require、partialtar24末尾execと真正collect1を保持。各fileを固定allowlist/regular/noSymlink/bounded/sourceownerで読み、存在/欠測理由を記録、partial/failはPASSへしない。旧Root/cohort/Actual4・原本/Backup/鍵/private旧rawは対象外（当新pureJUnit工具と別契約）。同run再試験の起動0、read-only収集の是正確認が未、状態OPEN/関連commit未。\n''')
receipt=json.loads((m.W/'stage-receipt.json').read_text());cfg=json.loads((m.W/'payload-config.json').read_text());selected=u['selectedWholeClasses'];assert sum(selected.values())==91
code='''from pathlib import Path
import datetime,hashlib,json,os,stat,sys,tarfile
r=Path(RUN)
assert os.getuid()==1000 and Path('/etc/hostname').read_text().strip()=='haruka'
assert hashlib.sha256((r/'stage.json').read_bytes()).hexdigest()==STAGE_SHA
assert (r.stat().st_dev,r.stat().st_ino)==INODE
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT
assert hashlib.sha256((r/'unit-result.json').read_bytes()).hexdigest()==UNIT_SHA
c=json.loads((r/'payload/config.json').read_text());assert c['sourceCommit']==SOURCE
assert hashlib.sha256((r/'payload/helper.py').read_bytes()).hexdigest()==HELPER_SHA
for n,h in c['payloadHashes'].items():assert hashlib.sha256((r/'payload'/n).read_bytes()).hexdigest()==h
target=r/'payload/source/program/characterization/target'
names=['owner.json','stage.json','payload/config.json','prepare-tmp.json','run-tmp.json','prepare-result.json','unit-verify-begin.json','unit-verify-process.json','unit-verify-exit.json','unit-result.json','admission.json','pmd.xml','checkstyle.xml']
names+=['payload/source/program/characterization/target/'+s for s in ['jacoco.exec','site/jacoco/jacoco.xml','spotbugsXml.xml']]
names+=['payload/source/program/characterization/target/surefire-reports/TEST-dev.codex.schubert.characterization.'+n+'.xml' for n in SELECTED]
expected={'ArtifactComparator.class','ArtifactComparator$ComparisonResult.class','GateCli.class','GateCli$BaselineNumbers.class','GateCli$TreeStats.class','GateContractValidator.class','GateContractValidator$ValidationResult.class','TargetAdapter.class','TargetAdapter$Target.class','CorrelatedLogEvidenceValidator.class'}
classes=list((target/'classes').rglob('*.class'));assert len(classes)==10 and {p.name for p in classes}==expected
names += [str(p.relative_to(r)) for p in classes]
names += [str(p.relative_to(r)) for p in sorted(r.glob('class-init-*.log'))]
present=[];missing=[];files={}
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as t:
 for n in names:
  p=r/n
  if not os.path.lexists(p):missing.append(n);continue
  s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_size<64*1024**2
  data=p.read_bytes();files[n]=hashlib.sha256(data).hexdigest();present.append(n)
  import io
  info=tarfile.TarInfo(n);info.size=len(data);info.mode=0o600;t.addfile(info,io.BytesIO(data))
 report=json.dumps(dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCommit=SOURCE,originalUnitExit=1,present=present,missing=missing,files=files,newTestsExecuted=0,oldRootCohortAccess=False),indent=2).encode()
 info=tarfile.TarInfo('preservation-manifest.json');info.size=len(report);info.mode=0o600;t.addfile(info,io.BytesIO(report))
'''
prefix='RUN='+repr(str(m.REMOTE))+'\nSTAGE_SHA='+repr(receipt['stageReceiptSha256'])+'\nINODE='+repr((receipt['owner']['runDevice'],receipt['owner']['runInode']))+'\nBOOT='+repr(receipt['owner']['bootId'])+'\nUNIT_SHA='+repr(sha(unit))+'\nSOURCE='+repr(u['sourceCommit'])+'\nHELPER_SHA='+repr(cfg['payloadHashes']['helper.py'])+'\nSELECTED='+repr(list(selected))+'\n'
compile(prefix+code,'<same-owned-pure-junit-readonly-export>','exec')
archive=m.ssh('collect-optional-preservation-v2',prefix+code,binary=True)
private=m.W/'preserved-terminal';assert not private.exists();private.mkdir(mode=0o700)
with tarfile.open(archive) as t:
 entries=t.getmembers();assert len({x.name for x in entries})==len(entries)
 for x in entries:
  path=Path(x.name);assert x.isfile() and not path.is_absolute() and '..' not in path.parts
 t.extractall(private,filter='data')
meta=json.loads((private/'preservation-manifest.json').read_text());assert meta['sourceCommit']==u['sourceCommit']
for name,digest in meta['files'].items():assert sha(private/name)==digest
out=b/'evidence/PG30734-common91-original-terminal-independent-xml-preservation-v1';assert not out.exists();out.mkdir();suites=[];failures=[]
for name,count in selected.items():
 p=private/('payload/source/program/characterization/target/surefire-reports/TEST-dev.codex.schubert.characterization.'+name+'.xml')
 if not p.exists():continue
 tree=ET.parse(p);root=tree.getroot();cases=root.findall('testcase');suites.append(dict(name=name,expected=count,actual=len(cases),failures=int(root.get('failures')),errors=int(root.get('errors')),skipped=int(root.get('skipped')),rawXmlSha256=sha(p)))
 for case in cases:
  for child in case:
   if child.tag in ['failure','error']:failures.append(dict(classname=case.get('classname'),name=case.get('name'),kind=child.tag,message=child.get('message'),detail=child.text))
 for props in list(root.findall('properties')):root.remove(props)
 for node in [root,*cases]:
  for child in list(node):
   if child.tag in ['system-out','system-err']:node.remove(child)
 ET.indent(tree);tree.write(out/p.name,encoding='utf-8',xml_declaration=True)
result=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=u['sourceCommit'],productionCoreMain='2ebbdf391873a5be6247ea59cb9addffb886c591',originalMavenExit=1,originalCollectExit=1,suites=suites,actualTestCases=sum(x['actual'] for x in suites),failures=sum(x['failures'] for x in suites),errors=sum(x['errors'] for x in suites),skipped=sum(x['skipped'] for x in suites),failureDetails=failures,missingArtifacts=meta['missing'],privateArchiveSha256=sha(archive),privateExecSha256=meta['files'].get('payload/source/program/characterization/target/jacoco.exec'),newTestsExecuted=0,sourceInputsUnchanged=True,ownedGroupAbsent=True,wholeProgramAccepted=False,coverage=None,formalAcceptanceAdded=0,allSpecificHoldsRetained=True)
(out/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,originalMavenExit=1,testCases=result['actualTestCases'],failures=result['failures'],errors=result['errors'],skipped=result['skipped'],failureNames=[x['name'] for x in failures],missing=meta['missing'],testReplays=0)))
