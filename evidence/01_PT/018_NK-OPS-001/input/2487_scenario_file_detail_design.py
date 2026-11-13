"""SSC344 file/game order detail and priorSSC343 limited status, design docs only."""
from pathlib import Path
import subprocess,json,re,hashlib,difflib,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();ss=next((r/'documents/300_SS').glob('**/343*.md'));ledger=r/'documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md';base=subprocess.check_output(['git','show',main+':'+str(ss.relative_to(r))],text=True);oldledger=subprocess.check_output(['git','show',main+':'+str(ledger.relative_to(r))],text=True);assert max(map(int,re.findall(r'SSC-(\d{3})',oldledger)))==343 and ss.read_text()==base
addition='''## SSC344 Scenario fileのゲーム内順と全体前後対応（2026-11-14、PG詳細補足）

UI223§3.2/4/5・UI254§4、SS331/V002/V004、SS343§10のfile ID対応・表示順を純metadata部品`ScenarioFileMigrationMap`へ具体化する。Entryのglobal順を扱うSSC343とは別範囲で、file内entry_index、Route prefix、speaker候補、audio link、動画/music、全DB/game/FK検証を代用しない。既存gamesのid/display_orderはV004通り1/1・2/2、file target IDとdisplay_orderは既N12を維持する。RD/UI/DDL/電文の変更や新DIFはない。

FilePairはgameId/currentFileId/targetFileId。gameIdはNK固定game1/2へ解決済みの値とし、実Current game対応の正しさはETL側の独立条件。source keyはgameIdとsigned currentFileIdの組、同game同sourceは拒否し別game同sourceは混合しない。targetは全gameを通じて1..999999999999で一意。game数値順→各game内currentFileIdの数値昇順を固定し、各gameで1始まりdense displayOrderを付与する。target再採番大小・入力List順を表示順へ使用しない。MappedFileもgameとtarget/order各N12をconstructorで検査する。List件数intに対するdense順位はN12内で、到達不能な余剰branchは追加しない。

保存List/位置Mapを明示copyして不変化し、null入力/要素・重複・不正範囲を拒否する。lookup(game,source)は当tupleだけ、unknownや不正gameを先頭/0へ補完しない。previous/nextは全保存順（games.display_order→files.display_order）で隣を返し、game1の最後とgame2の最初も接続する。最初/最後だけOptional.empty、未知sourceを端と混同しない。返値は宣言ID/順位であり、実DB存在・全file件数・game/FK・ロード成功・権限の証明ではない。

canonical ASCII/LFはheader `NKMIGFILEORDER1`の後にgameId TAB currentFileId TAB targetFileId TAB displayOrder LF。数値正準decimal、source signedを保持、game/source数値順でBOM/escape/余剰列なし。返却byte[]は毎回別所有、record/aggregate診断は固定redaction。空mapはheaderのみ、lookup/navigationは未知拒否で、移行完了を意味しない。

PT-MIG-FILEORDER001..012はgame1(2→900/order1,10→100/order2)・game2(1→50/order1)の手書き全byte、signed source両端/0・game別同source、source/target重複、game1/2・N12上下境界/null、不変入力/List/byte、既存/未知lookup、game内及び跨ぎ前後/両端、空/gap/入力再順序、所有8worker64taskを独立literalで検証する。Future各5秒・finallyshutdownNow/await10秒で未終端fail。Main/FilePair/MappedFile/privateSourceKey全4physicalの通常static/PT/CRC初期化/全四counterと独立postを確認し、actualMaster/DB/ETL/Root/native/CHR/全451/ITST未完は当局所結果で閉じない。

'''
entry='''

## SSC-344 Scenario fileゲーム内順・全体前後navigationの内部具体化（2026-11-14、PG、設計確定）

SS343§10・SS331/V002/V004・UI223/254・RD141161、WBS-P01903.02。未実装file対応artifactをpuredataとして具体化。解決済NK game1/2とsigned sourcefileIDのkey、global unique N12 target、game/source数値順と各game dense順位、immutableList/位置Map・unknown拒否・跨ぎprevious/next・ASCII四列を規定。Entry順や実game/FK/全件移行・権限を代用せず、RD/UI変更不要の内部補足でQA不要。未実装なので偽BUGなし。状態: 設計記述確定、main採用履歴を正とし、当部品製造/通常PT/実ETL未完。設計source/mainと実績は後記。
'''
a='状態: 設計確定・main公開待ち、製造/PT/実ETL未完。';z='状態: 設計確定・main公開済み（PR210、1f1eccc4575a78ac3989b045f9cc6a0041ac0dcd）、当純Entry対応PG/通常PT限定完了、実ETL/全451/PGPT全体未完。';assert oldledger.count(a)==1
qual='\n2026-11-14 SSC343限定実績: Coreeac60a4ca541670fa3ecc1747017c9b585d6d536、Unit source02452cf0eb644728a104ea053e7b28305546d6ca。PG30294真正新12/FES0・PG30296全3CRC/初期化/既定JaCoCo四100、適用静的0、source新障害0。公開実装branch commit048e856aeec9eda6965e286f1a771d3492917497/evidence/01_PT/018_NK-OPS-001/evidence/PG30302-scenario-id-order12-independent-source-trace-join-v1/manifest.json。fullETL/DB完全性・game/FK/画面順/CHR/native/全451/generatedfilter全体扱いは未受入、正式1964PT/53scopeを更新しない。今回mainは設計書と台帳だけでcode/config/tools/evidence混入0。\n'
localbefore=ledger.read_text();assert localbefore.count(a)==1 and max(map(int,re.findall(r'SSC-(\d{3})',localbefore)))==343;newss=base.split('\n',1)[0]+'\n\n'+addition+base.split('\n',1)[1];newledger=oldledger.replace(a,z).rstrip()+'\n'+qual+entry;ss.write_text(newss);ledger.write_text(localbefore.replace(a,z).rstrip()+'\n'+qual+entry)
patch=''.join(difflib.unified_diff(base.splitlines(True),newss.splitlines(True),fromfile='a/'+str(ss.relative_to(r)),tofile='b/'+str(ss.relative_to(r))))+''.join(difflib.unified_diff(oldledger.splitlines(True),newledger.splitlines(True),fromfile='a/'+str(ledger.relative_to(r)),tofile='b/'+str(ledger.relative_to(r))))
e=b/'evidence/PG30310-ssc344-file-order-design-only-main-patch-v1';e.mkdir();p=e/'design-only-main-patch.json';p.write_text(json.dumps(dict(baseMain=main,paths=[str(ss.relative_to(r)),str(ledger.relative_to(r))],patchUtf8Sha256=hashlib.sha256(patch.encode()).hexdigest(),patch=patch),ensure_ascii=False,indent=2)+'\n');(e/'manifest.json').write_text(json.dumps(dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ssc='SSC344',baseMain=main,patch=dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()),priorSsc343LimitedStatusIncluded=True,actualMasterDbRootVmNativeKeyUnitOps=0,sourceMainCreated=False,productTestsExecuted=0,newAcceptance=0,designOnlyMainPublicationPending=True),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,ssc='SSC344',designFiles=2,sourceCodeCreated=0)))
