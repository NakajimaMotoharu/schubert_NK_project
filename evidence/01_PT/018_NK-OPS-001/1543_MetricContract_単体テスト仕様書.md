# 1543 MetricContract 単体テスト仕様書

2026-10-23、NK-OPS-001/P018-09/C07共有参照。着手見積0.5/1.5/3pp、群上限10pp、共有開始0/着手表示6/reset1793306748。元C07監査費に加算しない。元計画のSS351§6/10・RD MON005/006/009/013・UI252§4～6から26 metric名/type/label-name集合とHTTP durationの9bucketを内部閉enumへ実装する。PG-D518。以前のmode段階1541/1542は同package既成果として保持。

PT_DEFAULT：純粋enum/Set/Listと自己所有の静的TSV fixture、実network/DB/VM/service/key/native/Rootの操作0。実label値や実metric送信は受け付けず、高cardinality値のruntime安全を本stageだけで保証しない。既ready gaugeを置換しない。STANDARD/DEBUGはmode policyの別責務、全C07/P018-09受入0。

Expectedは独立fixture `monitoring/metric-catalog.tsv` のSS351各行から作成し、Production enumを使ってexpectedを生成しない。SS表の複数名を展開した26件、label集合のexact一致とcounter/gauge/histogramを比較する。HTTP bucketは.05/.1/.25/.5/1/1.5/2/2.5/5のliteral9件。MQ/DB histogramへ未承認のbucketを割り当てない。

| Test ID / method | 入力/操作 | 独立期待値 |
|---|---|---|
| PT-OPS-METRIC-001 / metric001 | TSV全26名parse/type/label、enum全件を照合 | 全26一意・閉集合完全一致、TSV由来の種類とlabel集合 |
| 002 / metric002 | null/空/未知/大小文字/前後space/改行・合成canary名 | null契約違反又は固定CONFIG_INVALID、原入力漏洩0 |
| 003 / metric003 | 全26の正label、各key欠落/余計なusername/IP/ID/token/path等、null集合/要素 | 正集合のみ正常、欠落/追加は固定CONFIG_INVALID、nullを補正しない |
| 004 / metric004 | 返却Setへの変更、caller Setを後で変更 | 返却変更不可・入力を保持せず次callへ影響0 |
| 005 / metric005 | HTTP bucket取得/変更 | 独立literal9値/順序、immutable、他histogramへ適用するAPIなし |
| 006 / metric006 | 64 callerが全26を並行検証 | 原不変値、全Future成功・executor finally終端、sleepなし |

実行は親既gateを継承するpure harnessを二suiteへ拡張し、同sourceでmode7＋新catalog6=13を必要回帰として実行する。旧4222/common44の確認再演0。対象追加全physicalを除外せず四counter100・CRC/単一session・原XML・PMD/Checkstyle/SpotBugsと適用性を独立照合する。harnessのmetadata/compiler selectionが不足なら正常へ補正しない。実行command/source/exit/hashは後続1544/新onlymanifest、未実行は非合格。TX/rollback/再送は能力のない純粋metadataで非該当、collector/exporter/cardinality/alert/実mode切替は未完で別管理。
