"""Reuse the successful sixteen-source compile; run only the missing changed-Test static checks."""
from pathlib import Path
import hashlib,json,re,sys,xml.etree.ElementTree as ET
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
import pg9666_pagination_static as stage
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
cp=b/'evidence/PG37236-monitor-lock4-test-static-v3/compile.json';c=ld(cp);assert c['actualExit']==0 and c['sourceClosureCount']==16 and c['expectedTests']==113
assert all(sha(r/n)==h for n,h in c['inputHashes'].items())
ledger=r/'documents/900_OTHER/910_台帳';bug=ledger/'915_障害表.md';ykt=ledger/'916_横展開管理台帳.md'
assert max(map(int,re.findall(r'\bBUG-?(\d{3,4})(?!\d)',bug.read_text())))==3165
assert max(map(int,re.findall(r'\bYKT-?(\d{3,4})(?!\d)',ykt.read_text())))==2634
with bug.open('a') as f:f.write('\n\n## BUG3166 PG 2026-11-17 静的工具のrename参照順\n\n対象4653/PG37236。低/高。期待成功したcurrent16 Test compileを保持し当Testだけ静的確認。実際compile真正0後、source_pathsをrename定義前に参照してNameError/工具真正1、PMD/CS/製品113は未実行。原因=生成時の代入順。修正前起票、元compile全byte/input/commandを再使用する新static-only工具へ順序を明示する。compile再演0、Main/期待値変更0。YKT2635、状態OPEN。\n')
with ykt.open('a') as f:f.write('\n\n## YKT2635 BUG3166 static-only入力順\n\n対象rename/path/current source/hash/compiled16/SDK/Main1101の依存。rename資料と固定pathを先に読み、全source/class byte一致後だけCS/PMDを起動する。旧compile成功と後段工具失敗は別保持、既成功compileを反復しない。生成済み4653を再実行せず新4654の静的後段だけ実施。状態OPEN。\n')
root=ld(r/c['rootCompile']['path']);assert root['actualExit']==0 and all(sha(r/n)==h for n,h in root['inputHashes'].items())
work=Path(c['work']);assert all(sha(work/'component'/n)==h for n,h in c['physicalClassHashes'].items()) and all(sha(work/'test-classes'/n)==h for n,h in c['testPhysicalHashes'].items())
renamep=b/'evidence/PG37234-monitor-lock-test-name-source-v1/manifest.json';rename=ld(renamep);path=r/rename['path'];assert sha(path)==rename['afterSha256']
out=b/'evidence/PG37238-monitor-lock4-reused-compile-static-v1';assert not out.exists();out.mkdir();listing=out/'sources.txt';listing.write_text(str(path)+'\n')
jdk=tc/'jdk-25.0.4/bin';sg=tc/'static-gates-20261015';rules=r/'tools/quality/static';libs=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))]
stage.SLOT=out;stage.ENV=dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(tc/'jdk-25.0.4'),LANG='C.UTF-8')
commands={'checkstyle':[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(out/'checkstyle.xml'),'@'+str(listing)],'pmd':[str(jdk/'java'),'-cp',':'.join(map(str,libs)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',str(tc/'jdk-25.0.4/lib/jrt-fs.jar')+':'+str(work/'test-classes')+':'+c['classpath'],'--no-cache','--format','xml','--report-file',str(out/'pmd.xml')]}
stages={n:stage.step(n,cmd,work,timeout=120) for n,cmd in commands.items()};raw=[];errors=[]
for node in ET.parse(out/'pmd.xml').getroot().iter():
 tag=node.tag.rsplit('}',1)[-1]
 if tag in ['error','configerror']:errors.append(dict(node.attrib))
 if tag=='file':
  for x in node:
   if x.tag.rsplit('}',1)[-1]=='violation':raw.append(dict(path=str(Path(node.get('name')).relative_to(r)),**x.attrib,message=(x.text or '').strip()))
assert not errors and not ET.parse(out/'checkstyle.xml').getroot().findall('.//error')
assert stages['checkstyle']['actualExit']==0 and stages['pmd']['actualExit'] in [0,4] and not any(x['timedOut'] for x in stages.values())
pins={str(p):sha(p) for p in [*map(Path,c['toolDependencies']),*libs,sg/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml',tc/'google-java-format-1.36.1-all-deps.jar']}
oldp=b/'evidence/PG37228-monitor-lock4-test-static-v2/manifest.json';old=ld(oldp);main_raw=[x for x in old['rawFindings'] if '/src/main/' in x['path']];assert len(main_raw)==4 and all(x['rule']=='AvoidCatchingGenericException' for x in main_raw)
for x in main_raw:assert root['inputHashes'][x['path']]==old['mainInputHashes'][x['path']]
v=dict(c,actualExit=0,terminalAtUTC=stages['pmd']['endUTC'],mainInputHashes=root['inputHashes'],testSourceHashes=c['inputHashes'],toolDependencyHashes=pins,wholeTestSourceCounts=c['selectedWholeCounts'],stages=stages,rawFindings=raw,reusedUnchangedMainFindings=main_raw,unchangedMainStaticProof=ref(oldp),processingErrors=errors,sourcePatch=ref(renamep),reusedActualCompile=ref(cp),testCompileRerunsAfterSuccess=0,mainCompileRerunsAfterSuccess=0,productTestsExecuted=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,expectedTests=113,testPmdRaw=len(raw),unchangedMainRaw=len(main_raw),compileReruns=0,productTests=0)))
