# BrokerJournalEvidence 二つの値記録の実行結果

2026-11-19 JST、PT-P01810-CATALOG-065A/B。製品Core `ecf8a00fbd37720b80f8e107d59727723c706a12`、fixture `5f11aa844b24722f7ff76429f81bb51462bedf90`、PG40080。全2/1 suite、失敗・エラー・skip・未実行0、初回成功2。試験のみ追加。既compile三物理からSummary／Anchorを実行、外側parserを初期化していないことを確認し、過去のexecを取り込まなかった。

- Summary CRC `00afb37da5c39979`、生LINE 2／METHOD 6／CLASS 1／命令24。各miss0、元々分岐0。
- Anchor CRC `03ba24213b5afc99`、生LINE 2／METHOD 8／CLASS 1／命令36。各miss0、元々分岐0。
- 当fixtureでPMD・Checkstyle・format・javac Werror指摘0。元のMain全静的結果、外側生分岐、取得・解析・連携の正式条件は別。

独立レコード `evidence/01_PT/018_NK-OPS-001/evidence/PG40080-p01810-detached-journal-values-v1/independent.json` SHA-256 `e4c631b6e6b7b9334b570523614e78a0a7b5a3bdec4010b140488cd1e503974c`。584／585、PGPT-20261008-6106。C02、実journal／broker、全451、全P018-10は未受入。
