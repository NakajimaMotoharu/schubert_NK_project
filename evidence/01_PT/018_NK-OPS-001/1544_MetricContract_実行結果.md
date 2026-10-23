# 1544 MetricContract 実行結果

2026-10-23、1543/PG-D518、P018-09のpure catalogue stage。新規製造1enum/閉Kind、独立26行TSV、通常新6PTを追加。C07/P018-09全受入0、元190の追加受入0。既mode7は新sourceの必要回帰内数であり新13PTと数えない。

| 原証拠 | 対象sourceと真正結果 | manifest SHA-256 |
|---|---|---|
|PG7012-metric-catalog-host-v1|d3fa8d42efa1ceacf13e13adbbbc60da22166ac8、六format0/pure通常verify0、13件/2suite/FES0・rerun/flaky0|f29e1722480b3dc010be0cd6d6378b8429142a539564110fedb8cf4e1552277f|
|PG7014-metric-catalog-post-v1|同source、全4実行class＋metadata1、CRC不一致0/単一session、L75/M17/C4/B15全miss0、元13XML完全一致|3e0f98bf55ff1277289326e48578abca7fc65cfe1e5f0c8f593307a6f6dc2b1d|
|PG7016-metric-oracle-audit-v1|origin/main8b91944df SS351から独立に抽出した26名/type/label集合とTSV全26一致、HTTP9bucket literal一致、Production期待値生成0/PT実行0|a5c2abeffb8d5fed963dd1c979e826344a6a4adad313fbe992c62be0bc02d752|

pathは各 `evidence/provisional/<原証拠名>/manifest.json`。原archive/開始/実終了/log/XML/exec/classは `work/pgpt-runs/PG379/pg7012-metric-catalog-host-v1`。独立期待値/Test ID/fixtureは1543、実command・OS・Java25.0.4/Maven3.9.12/親NullAway・Jacoco0.8.15/hash/sourceは原manifestへ保存。物理classpath/class/XMLが同一source/runであることを実測し、旧mode/4222/common44/nativeとのexec union0。

## 全6 PMD指摘の個別適用性

raw終了4/6件、Checkstyle0/SpotBugs0。元reportのrule/message/行/source hashは7014に保存、抑止/除外変更0、未分類0。既三getterは同byte/同25～27行で1542の個別根拠と一致し、当13PTで不変性を必要回帰した。

| Finding | 判定 | 全当対象と根拠 |
|---|---|---|
|MetricContract13 service重複4|REQUIRED_CONTRACT|SS351各metricの独立label-nameを表のまま明示。001/003/006と7016の全26行でservice所有4metricを照合。自由値・秘密value・mutable stateではない |
|MetricContract15 address重複5|REQUIRED_CONTRACT|MQ/messages及びAddress別4gaugeの承認済label-name。同上26行joinで全5を照合、未知/秘密key拒否 |
|MetricContract24 status重複4|REQUIRED_CONTRACT|outbox2/媒体byte/batch runの承認済label-name。同上で全4を照合。raw文面を都合よく書換えず保存 |
|MonitoringModePolicy25 detailedMetricsEnabled|CONTEXT_NOT_APPLICABLE|private final primitiveのread-only value accessor、1542行別根拠、当mode001/002/007 |
|同26 retentionDays|CONTEXT_NOT_APPLICABLE|同final int/15又は0の固定保持値、当mode001/007 |
|同27 retentionBytes|CONTEXT_NOT_APPLICABLE|同final long/5000000000又は0、当mode001/007 |

metric metadataだけでは実label値の閉集合・runtime cardinality・actual exporterを受入しない。監視service、実mode切替、alert state/thresholdの接続は未完。F03 Root11/実Root/VM/DB/鍵/native/配備/未特定拒否HOLD、正式1964/53・歴史17・source別前回新7・工数nullは不変更。

fresh共有使用6/残94/reset1793306748、着手6から整数差0だが消費0ではない。専有N/T/実費null。usage cursor1c10710660322a7cdd76c17ec2fcc128712dafa159fa155dec35838486b8c30d（09:17:22 JST、explicit0/coverage限定）。元/v4/v5・開始0.5/1.5/3pp不変更。次は既承認SS351§7の純粋alert lifecycle（同condition/service単一event/count/lastSeen、warning5分/critical10分正常＋原因撤去）の実装・通常PTへ継続し、未確定thresholdの意味や実操作を推測しない。
