# 1753 共通Summary exporter・API接続 単体テスト仕様

NK-OPS-001/WBS-P018-09/C07、RD171/UI252/SS311351/1752。group1980、開始3/5/9pp・cap10は固定。PG-D592：既存ExactDurationMeterRegistryの一atomic snapshotから、公式Prometheus model/text writerで標準histogramを形成する。共通Bootstrapの純技術関数、業務APIへの逆依存・HTTP endpoint・暗黙PropertiesLoader・file/env/tracer読取を追加しない。

## PGと独立PT

Productionはbootstrap.monitoring.PrometheusSummaryExporter。Micrometer1.17.1/公式textformats1.7.0（model/config1.7.0）を既六moduleの外部依存へ追加する。公開Mavenの親POMをchecksum照合し、新規外部座標だけを準備、既内部snapshot/設定/証跡を上書きしない。

公開scrapeは借用registryと承認名→label-key集合を受ける。各呼出しで集合を防御copyし、sourceをcloseしない。各summary一snapshot、有限正順bucket/CDF/有限非負sum/非負countを検証、区間countと+Infを形成する。未知meterは無視、選択した非summaryやlabel不整合は拒否し、欠落を0へ偽装しない。有限CDFのbinary64は2^53未満の整数だけを受理する（2^53以上は整数精度を証明できないので例外、丸め/clampしない）。総countはlong、有限CDFが小さい場合はLong.MAX_VALUEも保持する。totalはlongへ戻さない。

|Test ID|対象・独立oracle|
|---|---|
|SUMENC001～024|bootstrap単体24：手書きsnapshot/秒CDF→標準text、複数family/series、escape、空/unknown、label/name/null、非summary、負/NaN/Infinity/count、境界順/CDF単調・整数・上限、2^53とlong最大、snapshot一回、借用closed/lifetime、IO/Runtime/Error伝播。期待値はliteralの標準text/sample値、Productionから生成しない|
|APISUM001～006|API実registry＋Db/Mq recorder接続6：初期全series0、1ns、有限5境界の前/等/後（独立long ns）、二Long.MAX_VALUE nsの正sum1.8446744073709553E10秒、STANDARD空・二owner独立、並行更新。SQL/JMS/実VMなし|
|既exDur001～010/Db9/Mq9|現sourceの実Test一覧を開始前照合し既28を確定、合計58/5suite。初稿の8/8・56予定は過去版からの誤った仮計数で、実行前に最新009各一件を含め訂正、成功加算ではない。想定数と異なる結果を算術PASSへしない|

fixtureはメモリのみ。IO例外はpackage内writer注入で独立故障、private反射なし。workerは有限・finally停止。null/欠落/空/未知を正常0へ扱わない。失敗時は未実装TDDと既実装違反を区別し、後者は915/916先行。

## 実行・品質・証跡

実装WIP発見：元constructor(boolean)はpureだがSDK1.7.0でdeprecated（初回8248 -Werror、PT0）。public Builderのconstructor/二boolean設定/build bytecodeもpureでLoader呼出しなしを照合、非deprecatedの明示builder＋二flag falseを採用する。警告抑制なし。IO故障fixtureは公式interface実装としdeprecated constructorを呼ばない。元8248の失敗を変更/転用しない。

JDK25.0.4/Maven3.9.12、既421と各実行manifestのcommand/branch/source/tool/hash/終了codeを正とする。新source正常six/NullAway/format→fresh対象PT→同exec CRC/line-method-class-branch100・静的・generated metadata・全physical/traceへ。新module境界を追加せず、既byteの成功を新Mainへ合算しない。必要全体451は別途未実行として維持。実行command・確定matrix・終了code・input/expected/actual/hash/BUGは1754と公開manifestへ記載する。

現時点は未実装・未実行・coverage未測定。正式1964/53・原190新受入0・QA051final/PTALT0・工数null不変。actual VM/Root/cohort/native/DB/Backup/鍵/intent/permit/配備/サービス/拒否未特定操作HOLD。通常小区切りで終了せず、許可済みPG/PTを継続する。
