# MaintenanceRecords原whole八・単体テスト仕様

2026-10-31／PG-D969／NK-BAT-001、OPS009/UI251/SS331・341・343§6.13、SSC055、PT-BAT038～045。Production6b53/normal14216、HEAD5717c3e360f99fd2e80698e4e7f737693329d2b8・push83060真正0。群3372実leafP00403開始1/3/7共有pp cap10固定、Completion論理ownerP01712は共有参照/追加費用0。最初componentへsplit親を指定したevent要求はappend前guard拒否、正規単一leafで一度だけ起票、旧費用の付替え0。

対象MaintenanceRecordsTest全文八（先行索引は旧関連資料だけで当current PT未登録）、Main MaintenanceRecords全body＋MaintenanceCompletion/Outcome全body、既BatchRun/MaintActivationの当source proofを参照して元再受入しない。初期値は固定UUID/Instant/ASCII手書き文字列、production encodeでexpectedを作らない。
- literalRecords：NKRUN1/NKACT1/NKDONE1固定byte72/109/140/141、SUCCESS0/WARNING10、全field復元。
- identityTemporalBoundaries：UUID全0/全f、年0001/9999、cutoff UTC14:59:59.999999/15:00:00のJST業務日。
- malformedSources：空/不足/余分/CRLF/BOM/末尾行とmagic/delimiter各byte0..255独立変異、固定例外message/cause/suppressed0。
- scalarAliases：UUID大文字/短縮/不正字、timestamp表記・offset・閏秒・年0/不正日、status00/01/11/50/70/+0/空白/x、終了cutoff以前拒否。異なる正常IDは認証違反とは扱わない。
- completionInvariants：終了cutoff-1μs/年10000/非μs拒否、cutoff同値許可。
- nullContracts：codec/read/activation/completionの11個null引数NPE期待。NPEをcatchして正常化するMain追加なし。
- ownershipAndRedaction：byte配列非共有/入力不変・後続破壊後のimmutable値保持、record equals/hash/表示固定redaction。
- concurrentUse：自己8thread/64独立固定ID、全completionbyte一致・future5秒、unique64/WARNING32。終了時executor close。

自己SLOT CWD target/maintenance-record-tracesへ公開固定fixture四fileを書出す。実業務原本/intent/permit・退役・Run成功認定・外部配備/親/Root/VM/DB/JMS/鍵/Graph/crypto・native操作なし。このcodecがNKDONE bytesを作ることを真正親DONEの証明にしない。関連MaintenanceRetirementRecordsTest wholeはFixture経由LinuxDirectoryCalls.createを含むため未着手HOLD・一部抽出0、退役methodの未達は全Source分母に残す。

Command: python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15870_maintenance_records_eight_pt.py。固定Main2/Test1hashは同scriptに明記、normal/snapshot/現src/当batchJar全closure比較。FreshJDK25.0.4/javac25 procなし/Xlint/Werror・6Jar・外部固定deps/JUnitPlatform1.13.4/JaCoCo0.8.15、原8/1だけ、親180秒。元Main変更・前source成功持込0。15872同exec受動CRC/session/全Source二・Code三/公式filter不変更、四held六native trueprobe0を確認。期待coverage未確認、未実行retirement branchを除外/全100にしない。Failed/flaky/skipped/not-runをPASSへ算入0、障害は修正前915/916、独立期待/結果とhashを3032へ。正式1964/53/歴史17/190/工数null/QA051final/全HOLD維持。
