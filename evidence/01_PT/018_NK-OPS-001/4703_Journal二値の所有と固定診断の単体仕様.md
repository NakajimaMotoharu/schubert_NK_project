# BrokerJournalEvidence 二つの値記録の単体仕様

NK-OPS-001、SS351の固定診断／SS343のbroker観測、WBS-P017-10成果をWBS-P018-10.03/2で参照。PT-P01810-CATALOG-065A/B。現製品Coreの既compileから外側classとSummary／Anchorの三物理のみを受け入れる。journalを取得するAPIやbroker、systemd、DB、ファイル入力へ進まない。

| Test ID | 手作り入力 | 独立期待値 |
|---|---|---|
| PT-P01810-CATALOG-065A | Summary。件数33／34、独立二つの固定digest | 両accessorの入力一致。両値が等しいときhash一致。各componentだけを変えると不一致。固定の `BrokerJournalSummary[redacted]` のみ。 |
| PT-P01810-CATALOG-065B | Anchor。合成invocation、単調時刻141、cursor、固定digest | 四accessorの入力一致。全同値時hash一致、各componentの差を単独認識、固定の `BrokerJournalAnchor[redacted]` のみ。 |

不正journal JSON、範囲、外部依存、不足観測、実行元が真正であること、実sinkは別契約。原PG15904の4試験は再実行せず永続保持し、その測定で未hitだったAnchorも今回の別execで独立に測定する。対象二値以外のcoverageを加算しない。
