"""SSC343 pure ID/order format, preserving approved DB/wire and Current order contracts."""
from pathlib import Path
import subprocess,json,re,hashlib,difflib,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();ss=next((r/'documents/300_SS').glob('**/343*.md'));ledger=r/'documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md';base=subprocess.check_output(['git','show',main+':'+str(ss.relative_to(r))],text=True);oldledger=subprocess.check_output(['git','show',main+':'+str(ledger.relative_to(r))],text=True);assert max(map(int,re.findall(r'SSC-(\d{3})',oldledger)))==342;assert ss.read_text()==base
addition='''## SSC343 Scenario entry移行ID対応と現行ID順の不変値（2026-11-14、PG詳細補足）

SS343§10のID対応/表示順固定を、UI223§3.2・UI254§4・SS331/V002の既存条件のまま内部部品`ScenarioEntryMigrationMap`へ具体化する。対象はglobal `script_entries`だけで、file別entry_index、games/script_files/speaker/audio/link、動画/musicのcategory/pair/順序を代用しない。現行ID維持やbookmark互換を追加しない。Actual ETL/全件数/DB・game/FK・表示結果の受入は別に残す。

入力IdPairはcurrentId/targetIdのlong二値。currentIdは採取済みのsigned値を改変/再解釈せず保持し、targetIdはV002 identity/CHECKとEntryId/wireの1..999999999999だけを許容する。currentIdとtargetIdはそれぞれ重複拒否。sourceの数値昇順（減算比較や文字列順ではない）へ並べ、1始まりdenseのdisplayOrderを一度固定する。再採番したtargetの大小・入力List順は表示順へ影響させない。Java Listのint件数に対する1始まり順位はN12以内であり、不要な到達不能branchで検査を増やさない。公開MappedEntryもtarget/order各1..N12をconstructorで保護する。

入力List/要素のnullは拒否、保存List/MapはList.copyOf/Map.copyOf等で不変性を明示する。mappings返却Listは変更不能、返却canonical byte[]は毎回別所有。lookup(currentId)は当mapに登録したtupleだけを返し、未知を0/先頭/新IDへ補完せず固定安全例外で拒否する。返値はID/順位の宣言データであり、実DB存在/完全性/ロード成功/起動・配備権限ではない。

canonicalはASCII/LFのheader `NKMIGSCENARIOORDER1`一行に続き、currentId TAB targetId TAB displayOrder LFの三列、currentId数値昇順。longの正準decimal（sourceはsigned可）を使用しBOM/escape/余剰列なし。空mapはheaderのみでlookup拒否、必要移行件数を満たすとはみなさない。record/aggregate診断は固定redactionとし原本DB/本文/credentialをログへ含めない。

PT-MIG-ORDER001..012は(10→100,2→900)からの手書き2/900/1・10/100/2、signed source両端/0とN12 target/order上下境界、source/target個別重複/null、immutable入力/返値/byte、未知lookup、空、gapと再順序、有限64task/8workerを独立literalで検証する。Future各5秒・finally shutdownNow/await10秒で未終端fail。Production sort/encoderからexpectedを作らない。全Main/Testの通常static/PT/全physical四counterと独立postを行い、実Current/DB/ETL/Root/native/CHR/全451/ITSTや全scope同source資格を当局所結果で閉じない。RD/UI/外部電文/DDL/画面の仕様は変更せず、新QA不要。

'''
entry='''

## SSC-343 Scenario entry移行ID対応・現行ID順固定の内部具体化（2026-11-14、PG、設計確定）

SS343§10・SS331/V002・UI2233.2/2544・RD141161、WBS-P01903.02。未実装ID対応artifactを純metadata部品として具体化し、current signed IDを保持・target/orderは既存N12・source数値順でdense displayOrder・重複/null/不変ListMap/未知lookup拒否・固定ASCII三列を定める。target順への置換やbookmark互換/実DB存在/ETL完了/権限を追加しない。source/target/順序12独立PTを先行規定。RD/UI変更不要・内部補足でQA不要、未実装なので偽BUG起票なし。状態: 設計確定・main公開待ち、製造/PT/実ETL未完。設計source/main commitと実装/試験証拠は後記。
'''
localbefore=ledger.read_text();assert max(map(int,re.findall(r'SSC-(\d{3})',localbefore)))==342;newss=base.split('\n',1)[0]+'\n\n'+addition+base.split('\n',1)[1];newledger=oldledger.rstrip()+'\n'+entry;ss.write_text(newss);ledger.write_text(localbefore.rstrip()+'\n'+entry)
patch=''.join(difflib.unified_diff(base.splitlines(True),newss.splitlines(True),fromfile='a/'+str(ss.relative_to(r)),tofile='b/'+str(ss.relative_to(r))))+''.join(difflib.unified_diff(oldledger.splitlines(True),newledger.splitlines(True),fromfile='a/'+str(ledger.relative_to(r)),tofile='b/'+str(ledger.relative_to(r))))
e=b/'evidence/PG30268-ssc343-id-order-design-only-main-patch-v1';e.mkdir();p=e/'design-only-main-patch.json';p.write_text(json.dumps(dict(baseMain=main,paths=[str(ss.relative_to(r)),str(ledger.relative_to(r))],patchUtf8Sha256=hashlib.sha256(patch.encode()).hexdigest(),patch=patch),ensure_ascii=False,indent=2)+'\n');(e/'manifest.json').write_text(json.dumps(dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ssc='SSC343',baseMain=main,patch=dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()),rootLedgerPrefixPreserved=True,actualOriginalDataDbVmRootNativeKeyUnitOps=0,MainSourceCreated=False,productTestsExecuted=0,newAcceptance=0,designOnlyMainPublicationPending=True),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,ssc='SSC343',designFiles=2,originalDataAccessed=False,sourceCodeCreated=0)))
