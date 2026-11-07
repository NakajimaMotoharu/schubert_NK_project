# provenance証跡候補検索の是正結果

BUG2415/YKT2160を修正前起票。source d50ce6132a7acf008496d7a401604510f630ed12でstrict single-target inputProvenance/counters/physicalを追加した。Main/Testの明示path/同module/内部class/hash、元source一致、唯一physical/CRC/full closure、除外無し/旧exec合算無し/CLASS計1を検査する。候補の原exit/旧source/partial/missing BRANCHを保持し、権限・正式受入・全source資格を推定しない。

PG22056: 元toolの新規先行1件がexit1/failure1、既存候補の見落としを再現。Product実行0、原tool/Testのsource/hash/赤結果を保存。
PG22060: 工具全33件（既25＋新8）exit0、失敗/skip0。欠落/aggregate/path traversal/namespace/不正hash・CRC/旧source/partial/失敗exit/BRANCH未測定の否定を含む。Pyflakesは工具とTestを検査し0。Product Testとは別計上。

横展開の対象はtracked公開manifest名に限定し、held/privateを読取前除外、2MiB超は候補化しない。対象3件：18612 ReplySender（4件）、18622 DlqSender（8件）、18630 Web返信DLQ（8件）。いずれも原hash/単一physical/CRC/明示Mainを保持して候補表示するだけで、原20件を再実行しない。18590 config-loader全10sourceのaggregateは明示単一Mainが無いため分割せず非対応根拠として記録した。

独立PG22062は全33成功case名・元stage/raw hash・3原receipt/宣言Main/hash/CRC/元counter/source/exitを再照合。工具回帰の確認再演0、Product/VM/DB/JMS/Root/native/held操作0。
回帰manifest SHA-256 `f6e95f6fa4a67ab472451b936924cb93b3132975833b50cd0dc60d32db1d4ca2`。
独立manifest SHA-256 `f387ab8e9d2654e4bcd9efb381d29ff5e82f235c5ffb422f131385fec0d4e92f`。

ArtemisRequestSenderは引き続き候補なしだが未実装と断定しない。既TestにはEmbeddedActiveMQ/実factory、MainにはWebStartupExceptionがあるため、既whole Testの部分抽出・新fixtureで実行しない。独立性が成立しない範囲はHOLD、許可済み別PG/PTを続ける。

有限tool障害と横展開はCLOSED。新Product Test/sourceproof/leaf0、unique388/whole88/正式1964-53/工数null、全runtime/451/QA051 final・既HOLDは不変。原計画/費用/旧成功は維持する。
