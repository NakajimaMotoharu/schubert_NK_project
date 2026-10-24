# 1752 Histogram backend契約 結果・次のPG/PT

NK-OPS-001/WBS-P018-09/C07/RD171/UI252/SS311351、1751/PG-D591、group1978開始0.25/1/3pp/cap10。候補source6246c954d6d0ac7171bf009663bb2e6539d8be32不変更。

## 確認済み

PG8234-histogram-backend-contract-v1原manifest SHA **1d4e0e828576b8a9e0ef3061301ddb48fa2af110b0688a2b5114af6d7cee1038**、終了0。固定7Java（2marker含む）/3POM・SDK15Jar/元8170-8173の全byteと18public型ABIを照合。command/終了/SDK/source/output hashは公開manifest、元javap receipt/logは /home/mini/codex/project1/work/pgpt-runs/PG379/pg8234-histogram-backend-contract-v1。SDK/製品target class初期化0、製品PT0/coverage未測定、監査をPASS/正式受入へ加算しない。

|接続点|事実・含意|
|---|---|
|API ExactDurationMeterRegistry|独自atomic snapshotがcount/正double total/有限5CDFを保持、.001/.01/.1/1/1.5秒。DEBUGは純計算markerを要求。元Simple成功をnative public sumへ転用しない|
|Web OverflowSafeHttpMeterRegistry|safe totalはpublic wrapperのdouble、delegate long totalを公開不可。maxはSDK時間窓。既httpDur005はmax/totalを確認するが、窓経過後のCDFは未確認なのでPrometheus累積bucketへ無条件転用しない|
|SDK Snapshot/ClassicHistogramBuckets|公開constructor/builderで標準histogramを構成できる。Classic bucketsは区間ごとのcountで、MicrometerのCDFから差分と+Infを形成する必要がある（SDK count計算は区間countの和）|
|SDK HistogramSnapshot/MetricMetadata/Labels|公開data modelでname/全label/total/bucketを形成可、private collectorMapやvendor namespace追加は不要|
|SDK PrometheusTextFormatWriter(false)|明示constructorは二boolean初期化だけ、標準text出力に使える。PrometheusMeterRegistryの暗黙PropertiesLoaderを使わず、ファイル/envやtracerに触れない経路を採れる|
|module/POM|現6moduleを維持。API/Webから相互の業務artifactへ依存しない。shared bootstrapの純技術formatterにMicrometer/公式model-textformat依存を限定追加する候補が成立、実service/Rootへの導入とは別|

## 次の一経路（PGを省略しない）

まず **APIの既精度registry→新共通summary text encoder→公式histogram text** を一接続経路として閉じる。

1. 次群でsource/独立PTを並行作成。新Production encoderはsrc/schubert-nk-bootstrap/src/main/java配下、借用MeterRegistry＋閉じたname/label-key仕様を受け、DistributionSummaryのsnapshotを公式model/writerへ渡す。SDKLoader/HTTP/server/DB/実Rootを呼ばず、source registryを勝手にcloseしない。新moduleを作らない。
2. bootstrap POMは既Micrometer1.17.1と公式exposition-textformats1.7.0（model/config等の実依存）だけを追加候補にする。既隔離SDKの公開POM/Jar/hashを照合して新規外部M2座標だけを準備、既内部snapshot/設定を上書きしない。toolchain421へsource/version/再現を記録する。
3. CDF→区間count/+Inf/正sum/秒単位、label/name/同family複数series、zero/NaN・不整合拒否、借用寿命、checked IO/Runtime/Error、IEEE count表現の境界を独立literal vectorで単体試験。provider欠落/不整合を正常な0へ変換しない。期待値をencoderやnative実測から作らない。
4. 別のtools内API普通PTで実ExactDurationMeterRegistry＋実Db/Mq Recorderを接続し、1ns/境界前後/二Long.MAX_VALUE nanosecondsの正sum・全bucket/count/name/labelを標準textに対して比較。fake markerを実装せず既factoryを使う。bootstrapの試験からAPI artifactへ逆依存させない。
5. 変更後正常六build/NullAway、対象全分岐・四coverage100/静的・全physical/traceを同sourceで確認する。cross-cut正式受入の所定全回帰は別途必要、Root HOLDを緩和せず未実行分を合格へ算入しない。codec/Currentbaseline/業務仕様/DIFは不変更。

その後にHTTP counter＋Timerへ進む。必要なら先に既HTTP snapshotのclock-expiry/CDF単体観点を追加し、発見障害は修正前に915/916。native delegateに結び付く旧overflow sumを採用したり、間に合わないからmarkerだけ付けたりしない。必要な内部依存の分解は継続し、監査/計画完成だけで全体停止しない。

## 保留・計測

今回新規PG/製品PT/正式受入0。開始22→fresh22残78/reset1793382075、丸め共有差0は専有費/無料ではない。usagef52bdbd8/12:43:19JSTは明示0/完全性未証明、実N/T・工数null。原-v4-v5/群開始見積不変更、metadata読取/tool/判断費として分離する。

正式1964PT/53scope・原190新受入0・QA051final/PTALT0、実VM/Root/cohort/native/DB/Backup/鍵/intent/permit/配備/サービス・拒否未特定操作HOLD不変更。候補sourceは未配備、実runtime UNKNOWN。新encoderはpure formatterで、runtime owner/真正source/HTTP経路の受入を代替しない。
