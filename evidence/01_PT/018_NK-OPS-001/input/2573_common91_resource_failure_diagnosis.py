"""BUG2881 before repair: bounded own-run resource/phase metadata, no test restart or raw-log export."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';l=r/'documents/900_OTHER/910_台帳';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((b/'evidence/PG30734-common91-original-terminal-independent-xml-preservation-v1/manifest.json').read_text());assert (report['actualTestCases'],report['failures'],report['errors'],report['skipped'])==(91,0,29,0)
assert {x['message'] for x in report['failureDetails']}=={'resource missing: fixtures/expected.json','resource missing: cases/catalog.json','resource missing: browser/manifest.json','resource missing: cases/dif-allowlist.json','public definition resource missing'}
p=l/'915_障害表.md';assert max(map(int,re.findall(r'^## BUG-(\d+)\b',p.read_text(),re.M)))==2880
p.write_text(p.read_text()+'''\n\n## BUG-2881 PT 2026-11-14 common91 Maven test resource/classpath assembly

重要度高・優先高。期待: 同sourceの承認済7 public JSON resourceを元byteのままtest classpathへ用意し、原全91が独立oracleで実行できる。実際Sourcef9f9/PG30730 Maven真正1、PG30734全91/F0E29S0。GateContract4・GateMetrics5・GateDefinition11・GateEvidence9がresource missingでerror、他62にも工程合格を付けない。原Source snapshotには7file存在/hash確認、JUnit basedir/classpathは当module/target/test-classesで正規、具体的copy phase原因は未確定。再現は当保存XML/元runだけ、成功62の再演/別source転用0。原因調査は当新pureJUnit工具のresource phase/output metadataだけ、業務DB/旧Root/cohort/鍵/rawへ触れない。修正前起票、YKT2414/SS355/451、Test/Main/oracle/schema/閾値を変更せず標準Maven resource組立を修復する。修正commit/再試験/完了日未、状態OPEN。\n''')
p=l/'916_横展開管理台帳.md';assert max(map(int,re.findall(r'^## YKT-(\d+)\b',p.read_text(),re.M)))==2413
p.write_text(p.read_text()+'''\n\n## YKT-2414 BUG2881 public resource classpath assembly

共通原因未確定、対象tests/resources下browser1/cases5/fixtures1の全7JSON、Maven process-test-resources出力/target/test-classes・GateContract resource loader/Definition fixture経由Metrics/Evidenceの29error。Source pathで直接読むGate/Comparator等とは分離し、loader/期待値を別方式へ変更しない。元7input hash/元Maven91 exit1/XML保存、各7の標準copy/byte/classpath/全91再試験・再発防止前提check未。調査は当新known-source run限定、旧失敗cohort/原本/Backup/VM/鍵/private旧rawは非対象。状態OPEN、関連commit未、PG30734及び次の限定diagnosis参照。\n''')
spec=importlib.util.spec_from_file_location('owned_resource_diagnosis_transport',i/'2565_haruka_common60_controller.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);stage=json.loads((t.W/'stage-receipt.json').read_text());cfg=json.loads((t.W/'payload-config.json').read_text())
code='''from pathlib import Path
import hashlib,json,os,re
r=Path(RUN);assert os.getuid()==1000 and Path('/etc/hostname').read_text().strip()=='haruka'
assert hashlib.sha256((r/'stage.json').read_bytes()).hexdigest()==STAGE
assert (r.stat().st_dev,r.stat().st_ino)==INODE
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT
assert hashlib.sha256((r/'payload/helper.py').read_bytes()).hexdigest()==HELPER
config=json.loads((r/'payload/config.json').read_text());assert config['sourceCommit']==SOURCE
root=r/'payload/source';module=root/'program/characterization';observed=[]
for name,h in config['payloadHashes'].items():
 if not name.startswith('source/program/characterization/tests/resources/'):continue
 p=r/'payload'/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h
 rel=name.split('/tests/resources/',1)[1];target=module/'target/test-classes'/rel
 row=dict(sourceRelative=rel,sourceSha256=h,targetExists=target.is_file(),targetSymlink=target.is_symlink())
 if target.is_file() and not target.is_symlink():row['targetSha256']=hashlib.sha256(target.read_bytes()).hexdigest()
 observed.append(row)
lines={}
for label in ['compile-static','unit-verify']:
 log=r/(label+'.private.log');out=[]
 for line in log.read_text(errors='replace').splitlines():
  if re.search(r'(resources:|resources-plugin|testResources|Copying [0-9]+ resource|skip non existing resourceDirectory|Skipping.*resource)',line,re.I):out.append(line)
 lines[label]=out[:50]
value=dict(actualExit=0,source=SOURCE,resources=observed,matchingBuildResourceLines=lines,rawLogsExported=False,newTestsExecuted=0,sourceModified=False)
print('PGPT_JSON_BEGIN');print(json.dumps(value));print('PGPT_JSON_END')
'''
prefix='RUN='+repr(t.REMOTE)+'\nSTAGE='+repr(stage['stageReceiptSha256'])+'\nINODE='+repr((stage['owner']['runDevice'],stage['owner']['runInode']))+'\nBOOT='+repr(stage['owner']['bootId'])+'\nHELPER='+repr(cfg['payloadHashes']['helper.py'])+'\nSOURCE='+repr(report['source'])+'\n'
compile(prefix+code,'<own-resource-metadata-readonly>','exec');value=t.ssh('resource-diagnosis-readonly-001',prefix+code);out=b/'evidence/PG30736-common91-resource-classpath-own-run-diagnosis-v1';assert not out.exists();out.mkdir();(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(value,ensure_ascii=False))
