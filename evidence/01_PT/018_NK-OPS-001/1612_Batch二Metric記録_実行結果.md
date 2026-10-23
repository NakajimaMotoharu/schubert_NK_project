# 1612 Batch二Metric記録 実行結果

source `34813cef90b2a5c6b2ad3be835565bf53e96a875`、1611/PG-D536/group1854。PG7252-batch-metric-host-v1原SHA `a556349ec240813acb5e4908087104e468cf96b5fe1bad1f08b69f789e28c7f2` は真正verify0/153PT21suite/FES・rerun/flaky0/六format0。新BATCHMET5＋BATCHREC8と既140当source必要回帰を区別し、旧140成功を算術合算していない。

PG7254-batch-metric-post-v1原SHA `379cef1807e526b900bd9ff61c1fd96224bad8be09e355862133adad7f34bc9a`：全44Java source/実36＋metadata1・単一sessionCRC0、**L672/M146/C36/B307全miss0**。親Enforcer/lint/Werror/NullAway/Spotless・SpotBugs/Checkstyle0。PMD raw28/exit4/processing0、旧27の全指摘対象Main同byte＋新BatchMetricRecorder.recordの一private final lockを契約必須として別1614へ全行結合する。recordはCounter→SUCCESS timestamp最大更新を同ownerで直列化、lockを外部公開せず逆向きcallbackなし、providerをcatch正常化/retry/format/closeしない。SDK四Jarを原pinsで開始前/後照合した。

新13全成功：承認済み二metric名/type/key・既十step四terminal固定、全40counter＋10gauge以外登録0、STD詳細0でもinvalid拒否、DEBUG初期counter0/lastSuccess NaN、全40matrix各1、SUCCESSだけ時刻最大更新・逆行/同値/他status無更新、UTC0001～9999/µs粒度・null境界、Runtime/NPE/Error/合成OOM/非formatableの同一伝播/attempt1/借用保持、64並行counter64/固定最大時刻、登録失敗のcaller所有/二registry分離/1000反復系列不増を独立assert。metric値はSDKのbinary64であり、9999年末のµs値は固定IEEE期待253402300800.0秒へ丸められる（原業務timestampを書換えない）。

PG7257-batch-metric-pom-review-v1原SHA `125359f9b10d78d4e4a7e0353beb4344a7567f98d9ecf739fd919b0fa9a195a4`：新BatchPOMは同版core1.17.1一compile依存nodeだけ、全他XML意味不変。版/scope/exclusion/重複/他依存変更/欠落の六静的負改変を拒否。既BatchStep/BatchStepResult.Status全二sourceはe7同byteで十/四canonical literal一致。これは静的reviewであり153PTへの加算0。実SDKは既421/1572/7106四Jarの再利用・offline/取得なし、version/上位仕様緩和0。

新障害/追加発見/上位変更0。実Batch/DB/Backup/Root/VM/keys/exporter等操作0、実terminal hook/一度だけ発行・永続lastSuccess bootstrap/parentMorning全体metric・native/CHR/全体451は未受入HOLD。正式1964/53・歴史17/別source新7・原190新受入0・工数null/QA051final/PTALT0不変更、原本/鍵/native/stash/Currentbaseline保全。OS/JDK/tool/branch/source・command/日時/終了/XML/coverage/static/path/hashは元7252/7254へ一意結合する。
