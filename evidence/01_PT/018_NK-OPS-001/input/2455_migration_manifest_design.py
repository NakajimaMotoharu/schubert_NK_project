"""SSC342 detailed offline inventory claim format; no data access or deployment."""
from pathlib import Path
import subprocess,json,hashlib,re,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();ss=next((r/'documents/300_SS').glob('**/343*.md'));ledger=r/'documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md';old=subprocess.check_output(['git','show',main+':'+str(ledger.relative_to(r))],text=True);assert max(map(int,re.findall(r'SSC-(\d{3})',old)))==341
addition='''## SSC342 移行素材inventoryの純metadata値・canonical差分（2026-11-14、PG内詳細補足）

P01903/SS343§10のcanonical manifestの内部単位を次で固定する。RD141/161・UI254の移行対象、全file件数/byte/SHA、表示順/ID対応、非移行log/account、現行原本保全、移行/切戻し判定は変更しない。これは未実装artifactの詳細化で、新しい業務仕様・操作権限・DIFを追加しない。

`AssetMigrationManifest`は既に採取した非秘密metadataの不変値だけを扱うbootstrap moduleの内部部品とし、file/DB/原本/鍵/Unit/権限・移行処理を操作しない。Entryはkind（SCENARIO/AUDIO/VIDEO/MUSIC）、currentPath、targetPath、byteLength、sha256。二pathはNFCのroot-relative POSIX表記、空/先頭slash/backslash/空segment/`.`/`..`/NUL・ISO制御・未対応surrogateを拒否する。ここでsymlink/実inode/許可root/実SHAを検証済みとはしない。それらの実読取と移行ID/category/pair/display_order/DB参照は後続ETLの独立条件として残す。CurrentPath/targetPathは一つの物理fileにつき各一意、byteLengthは非負long、SHAはlowerhex64。これは列挙済みfileの全体manifestであり、同一素材を参照する複数DB行やlinkをEntryへ重複挿入しない。

canonical UTF8/LFはheader `NKMIGASSET1`一行の後、currentPathのString自然順で、kind・currentPath・targetPath・byteLength正準decimal・sha256の五列をtabで区切り各行LFで終える。BOM/引用/escapeは出力しない。pathのtab/LF/CRは禁止済みで曖昧な列を作らない。入力Listと返却List/byte[]の所有を分離し、不変snapshotを保持する。空manifestは空inventory値として表現可だが、§10の本番件数基準を満たす証明ではない。総byteはchecked加算しlong overflowを拒否、原本の公表基準59,627file/19,240,707,190byteを実測又はこの部品の都合で変更しない。

Observationは既採取のtargetPath/byteLength/sha256という同じ構文の宣言値。`compareClaims`はtargetPathの重複を拒否し、欠落file数・余剰file数・byte不一致数・SHA不一致数と観測file/byteを返す。長さとSHAが共に異なる場合は各不一致へ一件ずつ計上する。値・null・要素の契約をconstructor/factoryで確定し、返値のmetadataMatchesは宣言値間の一致だけ。実filehash、symlink不存在、DB整合、移行完了、起動/配備許可、Go/rollback合格と読み替えない。不一致のrawpath/provider textを例外へ埋めない。

PT-MIG-ASSET001..012は固定synthetic二file（`abc`と空byteの既知SHA）による独立全byte golden、NFC/相対path/invalidscalar/null・重複、非負long/overflow、順序/alias/返却byte独立、完全一致/欠落/余剰/長さ・SHAの個別/同時不一致を検証する。sourceでexpectedを作らず、固定literalと算術を用いる。原master実体・DBdump/credentialをfixtureにしない。実採取/ETL/ID・表示順/transaction/COPY/途中失敗・再実行/実root・原本/DB/CHR/全451/ITSTは未完の別条件であり、当部品の通常PTだけで閉じない。

'''
base=subprocess.check_output(['git','show',main+':'+str(ss.relative_to(r))],text=True);entry='''

## SSC-342 移行素材canonical inventory・宣言metadata差分の内部具体化（2026-11-14、PG、設計確定）

関連SS343§10、RD141161/FIL003005/MIG003006・MIG-DAT003006、UI254、WBS-P01903。既存canonical manifestに値形式の詳細がなく、Production artifact/独立fixtureが未割当。RD/UI変更不要・QA不要。上位仕様を維持する内部実装具体化として起票後にSS343へ反映。Entry五列/NFCrootrelative/byteSHA/重複/checked総byte、固定UTF8LF・宣言比較counts/null/aliasを規定し、実inode/symlink/原本/DB/ID表示順/ETL/Go権限を付与しない。未実装なので新BUGを偽起票しない。状態: 設計確定・main公開待ち、code/PT/実移行未完。設計commit/main反映・製造/通常PT証拠は後記。
'''
# Require no pending unrelated edits in the two design files; use main as viewed original.
assert ss.read_text()==base
root_ledger_before=ledger.read_text()
ss.write_text(base.split('\n',1)[0]+'\n\n'+addition+base.split('\n',1)[1]);ledger.write_text(root_ledger_before.rstrip()+'\n'+entry)
e=b/'evidence/PG30150-p01903-design-and-independent-metadata-fixtures-v1';assert not e.exists();e.mkdir();import difflib
main_ss=base.split('\n',1)[0]+'\n\n'+addition+base.split('\n',1)[1];main_ledger=old.rstrip()+'\n'+entry
patch=''.join(difflib.unified_diff(base.splitlines(True),main_ss.splitlines(True),fromfile='a/'+str(ss.relative_to(r)),tofile='b/'+str(ss.relative_to(r))))+''.join(difflib.unified_diff(old.splitlines(True),main_ledger.splitlines(True),fromfile='a/'+str(ledger.relative_to(r)),tofile='b/'+str(ledger.relative_to(r))))
(e/'design-only-main.patch').write_text(patch)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();wr=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');fixture=dict(scope='SYNTHETIC_DECLARED_METADATA_ONLY_NOT_ACTUAL_FILES_OR_MASTER',originalPublicBaseline=dict(files=59627,bytes=19240707190,notMeasuredHere=True),entries=[dict(kind='SCENARIO',currentPath='input/a.txt',targetPath='assets/a.txt',byteLength=3,sha256='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'),dict(kind='AUDIO',currentPath='input/b.bin',targetPath='assets/b.bin',byteLength=0,sha256='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')],expectedFiles=2,expectedBytes=3,realFileDbHashClaims=0,plannedCases=['canonical UTF8 LF exact independent string','relative/NFC/scalar/refusal/null','negativebytes/badSHA','duplicatepaths','longoverflow','inputoutputalias','fullmatch','missing','unexpected','size','SHA','simultaneous size+SHA'])
wr(e/'synthetic-fixtures.json',fixture);wr(e/'manifest.json',dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceAtPlanning=main,ssc='SSC342',designFiles=[dict(path=str(p.relative_to(r)),sha256=sha(p)) for p in [ss,ledger]],fixture=dict(path=str((e/'synthetic-fixtures.json').relative_to(r)),sha256=sha(e/'synthetic-fixtures.json')),actualOriginalMasterDbVmRootNativeKeyActions=0,productTestsExecuted=0,newAcceptance=0,designOnlyMainPublicationPending=True))
print(json.dumps(dict(actualExit=0,designPaths=[str(ss.relative_to(r)),str(ledger.relative_to(r))],sourceMain=main,fixtures=2,actualOperations=0)))
