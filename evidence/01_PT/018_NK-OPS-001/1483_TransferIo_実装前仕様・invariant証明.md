# TransferIo 実装前仕様・invariant証明

実行工具（実装後固定）：`python3 -B tools/quality/pg6760_transfer_io_selected.py run`新only27件/10suite、元真正0後同tool `read`で原6762。実宣言は旧Transfer六＋Failure一＋新八＋六guard十二=27、管理三/format0、全旧oracle/他850Main/gates/Current不変。old1667へ黙って合わせず、new1669・old全keys＋明記Io/NioIo二だけ・旧family以外の物理byte差0を原Jarで照合する。full4197/646は新八を含む宣言予定で、まだ合格ではない。

1481準備を着手仕様へ固定。NK-BAT-001/OPS009/FIL006/UI237251/SS333§12/341/SSC118、TransferCleanup、BUG1612/YKT1365・PG-D503、群1693 P017-09低.5/標準1.5/高4pp（未較正・着手前固定）。基点bad7b4533/原4189 Q491bbf38、全Main851/1667・旧Test不変。修正前実測family L4/M0/C0/B10miss。未実装の注入口に対する初回compile不能を既実装の障害PTには数えず、現quality残件と独立oracleを先に固定する。

## 同値の根拠と保持条件

日付は既`[0-9]{8}`のASCII八桁だけ通り、`uuuuMMdd`の隣接固定MM/dd各二桁とstrict parserによりyearは四桁0000～9999。year>9999のtrue側はこの受理集合に存在しない。year<1は残す。旧0/1/9999 Testを保持し、除外やprivate input偽造ではなく同じ受理集合の述語へ整理する。

|同一性呼出し|firstの生成|nextの生成|毎回固定される属性|
|---|---|---|---|
|child開始|root.atExistingEntryHandle→inspect(true,admitted.device)|held child→inspect(true,admitted.device)|constructor UID/GID・directory0750・admitted.device|
|file削除直前|同上before|held child→inspect(true,admitted.device)|同上|
|child終了|同上before|held child→inspect(true,admitted.device)|同上|
|空child削除直前|同上before|parent entry→inspect(true,admitted.device)|同上|
|root各再観測|initial inspect(true,-1)のadmitted|root→inspect(true,admitted.device)|同上、deviceはfirstで固定|

従ってdevice/uid/gid/mode比較を同一性から取り除いても各fresh inspectの拒否条件は一切消えず、inode比較だけは必ず残す。保護属性が変わった入力はinspectで拒否する負試験を追加する。root/child観測・guard・heldFD・NOFOLLOW・unlink/sync・mtime・成功/失敗/保全集計/正常化禁止/資源所有は不変更。

Ioはpackage-only三読取(metadata map/filesystem/openNames)。既constructorはdefault NIOへ委譲し、Test constructorはnonnull借用Ioを受ける。metadata/nullは既policyで拒否、null filesystem/stream/Path要素/filenameは固定IO失敗にしNPEをcatchして成功化しない。absentは実NOFOLLOWのまま。新nested Ioは宣言だけ、NioIoは既Files呼出しの一対一委譲、削除機能なし。Main数1667→1669、追加classは`batch:dev/codex/schubert/nk/batch/file/TransferCleanup$Io.class`と`$NioIo.class`だけ、851source/943artifact数は不変。全旧/新物理mapとclass内全method/branch適用性を実証する。

## 独立fixtureとTest ID

fresh JUnit TempDirだけ。root/date0750・file0640、実fixture UID/GID、固定cutoff2026-09-30T00:00:00Z、公開UUID名11111111-2222-4333-8444-555555555555.part・byte17,23,41・mtime=cutoff-1秒。数値期待はSSのtarget/success/failure/retained/bytesから独立に固定。既TestのexpectedをProduction計算で置換しない。faultは読取口の入力値か自己所有DirectoryCalls backendだけ、実UID変更/mount/race/原本/VM/Rootは触れない。全FD/stream後条件と元byte/ino保持、guard試行とmutating call数をassertする。

|Test ID|目的・入力|固定期待|
|---|---|---|
|PT-OPS-TRANSFER-IO-001|9桁/符号/全角/7桁/19000229と有効20000229/20240229の空directory|target/success/failure/bytes0、retained5・WARNING/PROTECTED_RECORDS、invalid五保全/valid二削除/root保持。既year0/1/9999は旧Test回帰|
|002|initial root size<0/nlink<2/null map/null又はunsupported filesystem|全体IO失敗・削除0・byte/全inode保全、FD/stream全解放|
|003|child-directory又はfileのdeviceだけ異常入力|target/success/failure/bytes0、retained1・WARNING、元file/date/root保持|
|004|admission後root又はchildのinodeだけ異常入力|全体IO失敗・削除0・元実file/dir不変、借用FDはcallerがclose|
|005|root再観測のuid/gid/mode/deviceを一属性ずつ異常化|全体IO失敗・削除0、削除した重複predicateの代わりにfresh inspectが毎回拒否する根拠|
|006|self-owned unlink backendが正常returnしてもfileを残す|target1/success0/failure1/retained0/bytes0、WARNING/IO_FAILURE、元byte/file/date/root保全、後条件実不存在を成功補完しない|
|007|metadata/fs/openNames IOException、iterator/close IOException、null stream/Path要素/filename|全体IO失敗・削除0・stream全close・固定失敗。private反射/実競合なし、nullを空列挙へ補完0|
|008|新借用Ioのnull constructor契約|既nonnull invariant拒否・borrowed rootを勝手にclose/変更0、caller closeで全FD解放|

全新八JUnitの予定、subvector水増し0。既TransferCleanupTest六/FailureTest一・六guard十二を同source回帰（最終inventoryは実宣言で照合）。PT_DEFAULT。source/実command/format/compile-null/六static/原XML/Jar/四counter・Main1669増分/関連BUG/証跡hashは後続結果へ。global100/実Transfer処理/Root/native/CHR/正式/QA051final/ITSTは未受入、原-v4/17/工数null/全HOLD不変更。
