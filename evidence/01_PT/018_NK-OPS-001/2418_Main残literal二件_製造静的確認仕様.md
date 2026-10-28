# Main残literal二件・製造静的確認仕様

Program NK-BAT-001（TransferCleanup.execute）/NK-OPS-001（LinuxSystemdSession.releaseOutput/read/Native.bind）。元class/methodのRD/UI/SSは各source Javadocと原Program仕様を継承する。新methodは追加しない。

event2785/REMAINING_MAIN_LITERAL_SOURCE_ONLY2_V1、着手前1/3/6pp cap10・主F03、元主担当費P01709/P01803保持。BUG2030/31-YKT1778/79修正前起票。元Main SHA ee543c1e/862ef7c7は原PMD02953/06175と一致、後続成果索引と現全文を照合し当二指摘が未対応と確認した。

PGはTransferCleanupのprivate MINIMUM_SUPPORTED_DATE_YEAR=1とyear比較一token、LinuxSystemdSessionのprivate LIBC_FREE_SYMBOL="free"と同literal四tokenだけ。全元source/token/hashを保存し原token列への逆変換・境界/operator/symbol/slot/例外/guard変更の非同値反例で全挙動不変更を確認する。RD/UI/SS/承認仕様・固定ABI/順序/ownership/budget/counterには変更不要、SSC/QA不要の実装規約是正。

PT判定REVIEW_STATIC：既whole TransferはOwnedTransferDirectory/LinuxDirectoryCallsによる実inode/FFM/削除経路、SystemdはArena/libsystemd/bus/nativeの既HOLDに依存。動的製品PT/部分抽出/新harness/実サービス・VMは実行しない。許可済み通常六module compile/package/NullAway/format PT0と明示source PMD/Checkstyle、bytecode読取SpotBugs・全class metadata比較だけ行う。これは動的PT免除又は実測coverage100の承認ではない。

PT-LITERAL-SOURCE-001/002は各原token逆・反例と原diagnostic除去、003は同source六normal PT0/静的/公開ABIと物理差・他Main/Test同byte、004は原WBS/owner-costと旧runtime/sourceを保全したtrace。期待値は元全文/固定数字1・symbol free/原class metadata、Productionを呼んで生成しない。各manifestへ実command/時間/source/SDK/exit/hash、結果2419へ保存する。動的PT NOT_EXECUTED・coverage NOT_MEASURED、正式1964/53/17-190/工数null/QA051final維持。
