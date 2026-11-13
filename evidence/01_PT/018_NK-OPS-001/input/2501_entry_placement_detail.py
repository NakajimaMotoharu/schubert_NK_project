"""SSC345 internal entry/file composition; design-only main patch, before implementation."""
from pathlib import Path
import subprocess,json,re,hashlib,difflib,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();ss=next((r/'documents/300_SS').glob('**/343*.md'));ledger=r/'documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md';base=subprocess.check_output(['git','show',main+':'+str(ss.relative_to(r))],text=True);oldledger=subprocess.check_output(['git','show',main+':'+str(ledger.relative_to(r))],text=True);assert max(map(int,re.findall(r'^## SSC-(\d+)\b',oldledger,re.M)))==344 and ss.read_text()==base
addition='''## SSC345 Scenario entry所属file・entry_indexと移行対応の接続（2026-11-14、PG詳細補足）

SS343§10、SS331/V002/V004・UI223§3.2/4/5・UI254の既存ID/表示順/FK条件を内部ScenarioEntryPlacementMapで接続する。SSC343のglobal entry順とSSC344のfile/game順を再実装せず二mapを再利用する。RD/UI/DDL/電文を変更せず、新QA不要。実Currentからのgame/entry_index抽出の正しさ、実DB件数/FK/ロード/権限は別条件である。

入力はScenarioFileMigrationMap、ScenarioEntryMigrationMap及びPlacement(gameId,currentFileId,currentEntryId,entryIndex)のList。gameは解決済NK1/2、source両IDはsigned値を保持、entryIndexは既DDL通り0..IntegerMAX。null両map/List/要素を拒否、List件数はEntry対応件数と完全一致、各source entryは一回だけ、既知file/game及びentryだけを許容する。targetFileIdとentryIndexの組も一意で、別fileの同indexは許容する。未知を新ID/0/先頭へ補完しない。空Entryと空Placementは値として許容するが、必要全量の移行成功ではない。

PlacedEntryはcurrentEntryId,targetEntryId,displayOrder,gameId,targetFileId,entryIndex。target entry/file/order各1..999999999999、game1/2、index>=0をconstructorで検査する。global entriesはEntry対応displayOrder昇順、lookupはcurrentEntryIdだけ、entriesForFile(game,sourceFile)は既知fileの行をentryIndex昇順で返す。既知の空fileは空List、未知fileは固定安全例外で拒否し空と混同しない。List/Mapを明示不変copy、byte[]は毎回別所有。公開record/aggregate診断は固定redaction、内部FilePositionは公開/診断/ログへ出さない。

canonical ASCII/LFはheader NKMIGENTRYPLACEMENT1 LFに続きcurrentEntryId TAB targetEntryId TAB displayOrder TAB gameId TAB targetFileId TAB entryIndex LF、global表示順、正準signed/非負decimal、BOM/escape/余剰列なし。realCurrent/DB・game/FK/全99661entry・body/speaker/audio/ロード/Goの証拠へ読み替えない。

PT-MIG-PLACE001..012は手書きentry2→900/order1/game1/file500/index7、10→100/order2/game1/file800/index3、30→50/order3/game2/file600/index0の全byte、同file index0/MAXによるglobal順との逆転、未知file/entry・game、source/targetfile-index重複、件数不足/余剰、空/既知空file、game/index/N12各境界/null、immutable入力/List/byte、signed両端/再順序、所有8worker64task（Future各5秒・finallyshutdownNow/await10秒、非終端fail）を独立literalで確認する。新4physicalと旧Entry3/File4の完全sourceを含め、新component/支援部品・未網羅counterを区別し旧exec/旧成功を合算しない。全451/実ETL/RootVM/native/CHR/ITST未完は局所成功で閉じない。

'''
entry='''\n\n## SSC-345 Scenario entry/file参照とentry_index順の内部接続（2026-11-14、PG、設計確定）

SS343§10・SS331/V002/V004・UI223254・RD141161/WBS-P01903.02。既Entry global順/File game順二mapを合成し、currentEntry/file参照・game・入力全件対応・file/index一意と表示順を未実装artifactへ具体化。puredataのみ、実Current/DB/FK/全件数・権限を代用せず、RD/UI変更不要・QA不要。新Main/独立whole12を予定し製造前に詳細を公開する。状態: 設計確定、main公開待ち、PG/通常PT/実ETL未完。設計source/mainと限定実績は後記。
'''
newss=base.split('\n',1)[0]+'\n\n'+addition+base.split('\n',1)[1];newledger=oldledger.rstrip()+entry;localbefore=ledger.read_text();assert max(map(int,re.findall(r'^## SSC-(\d+)\b',localbefore,re.M)))==344;ss.write_text(newss);ledger.write_text(localbefore.rstrip()+entry);patch=''.join(difflib.unified_diff(base.splitlines(True),newss.splitlines(True),fromfile='a/'+str(ss.relative_to(r)),tofile='b/'+str(ss.relative_to(r))))+''.join(difflib.unified_diff(oldledger.splitlines(True),newledger.splitlines(True),fromfile='a/'+str(ledger.relative_to(r)),tofile='b/'+str(ledger.relative_to(r))));e=b/'evidence/PG30382-ssc345-entry-file-detail-only-main-patch-v1';e.mkdir();p=e/'design-only-main-patch.json';p.write_text(json.dumps(dict(baseMain=main,paths=[str(ss.relative_to(r)),str(ledger.relative_to(r))],patchUtf8Sha256=hashlib.sha256(patch.encode()).hexdigest(),patch=patch),ensure_ascii=False,indent=2)+'\n');(e/'manifest.json').write_text(json.dumps(dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ssc='SSC345',baseMain=main,patch=dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()),actualDbRootVmNativeKeyUnitOps=0,sourceMainCreated=False,productTestsExecuted=0,newAcceptance=0,designOnlyMainPublicationPending=True),indent=2)+'\n');print(json.dumps(dict(actualExit=0,ssc='SSC345',designFiles=2,sourceMainCreated=0)))
