# 借用Outboxの12件を同一execで検証

PG43552は2026-11-23 19:15 JSTに終了0。固定候補 `4c3c96d35a1131ac116dea039a5ebb3451749ca9`、製品Core `87927ea17c1c8dbef528bc0c6882c24b1fe7c871`、JDK25・JaCoCo 0.8.15。PT-OUT-JDBC001～012、2 fixtureの12件を実行し、成功12、失敗・skip・未実行0。SQL・日時・再送表・null・資源所有の独立期待値は4688と既存fixtureに従う。JDK内の合成JDBCプロキシを使用した。

| 測定対象 | 行 | method | class | branch |
|---|---:|---:|---:|---:|
| JdbcOutboxRepository | 178/178 | 13/13 | 1/1 | 40/40 |
| RequiredColumn | 3/5 | 1/2 | 1/1 | 2/2 |

同一セッションの二物理を無filterで測定。claimとlease判定を含むrepositoryの四カウンタはこの範囲で到達。RequiredColumn.requireValueは3行・1 method・2分岐到達。private constructor 2行・1 methodが残る。PG43436／38／40／42の四execは原記録を維持し、新execへ合成していない。12件は既存名称で、試験定義・固有Test IDの追加は0。

WBS-P004-05/2、SS331／332の借用資源条件、SSC-471。実DB・正規API JARと全製品451は引き続き未受入。正式 `PT-WEB-20260925-24` 1964PT／53 scope、元WBS16/190。実行証跡・全入力、JUnit、class初期化、単一execのhashはmanifestを参照する。

- manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG43552-current-jdbc-outbox-12-single-exec-v1/manifest.json`
- SHA-256 `ece1baa5241fa96148834289425c6bb180fe7767ef9dc5cff9ef4b5b15938b62`
