# Snapshot鍵使用・close並行・単体テスト仕様

2026-10-26追記訂正：以下は群2254開始時の未実装計画。2000の限定静的レビューで、SS343がconsumer停止→codec close/process中close禁止を既に要求すると確認した。KEYLIFE001の途中close待機は追加提案であり、通常の承認前提を表さない。二IDはNOT_IMPLEMENTED_NOT_EXECUTED_HOLD、ResponseSnapshotLifetimeTest未作成、修正/新Test/実行/coverageなし。元witnessに有効な動的証拠なし、failed turn01a1737c-d6fd-75d0-932b-49fe6a09b029の拒否suboperationは未特定。同検証/工具診断/lock実装を再試行しない。原見積1/3/8と原文は保持し、2000は実行結果ではなくSTATIC_PT_DESIGN_REVIEW_COMPLETEとして区別する。

2026-10-26、NK-MSG-002/WBS-P006-01/群2254、開始1/3/8pp cap10。ResponseSnapshotCodec.encrypt/decrypt/close、RD DAT009/MQ008/OPS009、UI241242、SS324§6/15・352§11.2/343、PG-D675/BUG1775/YKT1526。元source21d7c3042/normal9866・既9成功は保全し、未修正witnessの根拠にだけ使う。

許可範囲は自己所有有限host JVM/制御thread・public合成32byte key・nonce/短い非秘密plaintext/独立JCEだけ。実鍵file/credential/DB/HTTP/JMS/VM/Root/native保全物/permit/intent/Graph9/拒否操作0。providerをpackage constructor seamで停止し、owner closeとkey使用の順序を制御する。private reflection/実OOM/OS操作/他processへの介入は行わない。SPIの全体交換も行わない。

修正前witnessはprovider到達→旧close帰還→provider解放→encrypt帰還の順を保持し、返却ciphertextを別JCE/SS由来の8 length-prefixed AADで復号する。構成keyで不認証、zero配列でのみ認証という結果が出た場合だけdefectReproduced/真正exit1として保存する。setup失敗・未知結果は別エラーで、成功や既PTへ加算しない。

|Test ID|class/method|操作と独立期待|
|---|---|---|
|PT-IDEM-KEYLIFE001|ResponseSnapshotLifetimeTest.keylife001CloseWaitsForBorrowedKeyAndNeverEncryptsWithErasedBytes|encryptのprovider保持中に別自己threadでcloseを開始し、待機/終端を観測後release。採用lease方針ではcloseがin-flight終了前に消去しない。返却値を独立JCE/SSのliteral purpose/table/UUID/layout/version/ownerで認証・inflateし入力完全一致、caller key不変。close後の両入口は拒否、全自己thread終端|
|PT-IDEM-KEYLIFE002|ResponseSnapshotLifetimeTest.keylife002ConcurrentEncryptDecryptRemainIndependentBeforeClose|32独立caller/異Message-owner/入力、test-only atomic nonce連番で重複0。全返却を独立JCE/独立AAD/inflateと原入力へ一致、Production decryptも原入力一致（roundtripだけをoracleにしない）。全worker終了後close、以後入口拒否/caller key不変|

新Test一source二method、既Codec7＋NonceFailure2を含む全11/3suiteを新source単一runで実行し、全Codec source unitの四counter/CRC/sessionを測定する。reader/writer lockの例外解放・null/閉じた入口は旧9と新2/全unitで確認、未実行を100へ補完しない。Java25/正常compile・NullAway・SpotBugs・変更Main/Test PMD/CS、全1843byte差分・既Test byte、五AES codecのencrypt/decrypt/close排他を独立確認する。新sourceの必要回帰であり元9成功だけの確認再演ではない。

仕様期待を新crypto implementationから作らない。keyは固定public合成vector、AADはDataOutputStreamで8個literal length-prefixed fieldを手組、cipherは標準JCE/InflaterInputStreamで独立検証。raw key/nonce/cipher/plaintextを証跡へ出力せずboolean/件数/入力生成規則とhashを保存する。JVM/JCA内部copyの物理消去は保証外。1994の元provider障害/PMDraw3/四100を保全し、他source/native/全451/正式へ合算しない。

実command/日時/JDK/tool/source/branch/終了code/全Test ID/XML/coverage・BUG/各hashは2000へ。正式1964-53/17-190/QA051final/工数null/全HOLD・原見積/費用/cursorは保持する。対象未再現や有効なcaller前提で不具合が否定された場合はcodeを変えずその根拠を保存し、通常小群で全体停止しない。
