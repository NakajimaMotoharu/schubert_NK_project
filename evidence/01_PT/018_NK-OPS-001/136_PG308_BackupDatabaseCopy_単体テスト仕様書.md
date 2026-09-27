# PG308 専用backup資格情報コピー PT仕様（実装前）

Program NK-OPS-001、batch.file.BackupDatabaseCopy.dump/create/write/readback/erase/namespace/metadata、BAK/BKO/OPS009/UI251/SS341 6.1・3436.6/SSC090・091、BUG271/YKT205。PT-OPS-DBCP001～008、BackupDatabaseCopyTest。Production worker専用borrowed tmpfs0700のroot/UID/GID/固定NSS/Unit・出力FD・親排他・全30分budgetの真正入場はcaller必須、本部品が推定しない。

001独立正常oracle：literal public pgpass1..65536byte、新600 UUID.part・write force close→元inode/name/readback一致→caller-owned byte全zero→固定dump callback→zero write force close/readback→同inode/name再照合→unlink/sync、runtime空。callback内部のliteral bytesと消去marker、close/force順序を独立検証。
002境界/null/invariant：0/65537/null、依存null、UID/GID0/負/uint32上限超拒否、1/65536/uint32上限許容。nullをcatch正常化しない。
003入場：root/file mode・owner/group・nlink・size・device/inode・ACL・tmpfs・readonly、不明metadata/null/wrong type、作成前/後/root原本差し替え拒否。dump呼出0を確認。
004 I/O全位置：open/write/size/force/close/read、zero progress/negative/overread/short/long/position不整合/readback不一致、各syscall位置、acquired resource全close。throw前にraw byte全zeroを確認、生成済みfile保全。
005 callback失敗/unknown/compound：dump途中IO/Runtime/Errorは同identity（既知IOは固定redaction）と未廃棄file、scopeを返さないquarantine中にunlink0/次dump0。取得済み子terminal/NativeStart隔離はARCHPROC suite依存。
006 消去：callback後だけzero、zero全readback/元inode/名前束縛を再照合、unlink後sync失敗は不確定・復元再作成なし。
007 並行/衝突：private lock、UUID CREATE_NEW、collision overwrite0、callerroot借用close0、独立copy状態。
008 NativeNio公開fixture：実FD・0600/private root、synthetic metadata portはnative入場代用にしない。実専用Unit/nativeDBdumpは後続別実測。

expectedはpublic literal byte/SQLdump list非空条件/OSmode/call-count・latchで作りProductionmethodをexpected生成に使わない。新class全line/method/class/branch100%・全counter0、静的0、relatedPT/collector ownership/105canary。初期TDD未実装は障害扱いせず、既実装仕様違反は915へ先行起票。command/environment/commit/exit/実値/hash/障害は137結果/provisional PG308へ保存。未実行/failed/skippedを合格にしない。
