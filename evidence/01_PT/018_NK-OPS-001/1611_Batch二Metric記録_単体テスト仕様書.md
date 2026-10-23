# 1611 Batch二Metric記録 単体テスト仕様書

NK-OPS-001/P018-09/共有C07追加費0、RD171 MON005～013/UI252/SS341§3・SS351§6/8/10・PG-D536。BatchMetricContract(Step/Status/lookup/labels/names/mode)、BatchMetricRecorder(constructor/record/detail/seconds/tags)。group1854、開始共有16/残84/reset1793306748・見積2/5/9pp/上限10、元/v4/v5は不変更。

固定oracle：十stepはBACKUP_DB/BACKUP_CONFIG/CLEAN_NOTIFICATION/CLEAN_QUESTION/CLEAN_SESSION/CLEAN_INBOX_OUTBOX/CLEAN_LOG/CLEAN_BATCH_RUN/CLEAN_TRANSFER/CLEAN_EXPIRY、四terminal SUCCESS/WARNING/FAILED/SKIPPED。SS351の`nk_batch_runs_total`はcounter/step,status、`nk_batch_last_success_timestamp_seconds`はgauge/step。既SS341永続step/result型との対応を保ち、Morning親全体の未確定labelを追加しない。

| Test ID | 入力・操作 | 独立期待値と根拠 |
|---|---|---|
| BATCHMET001 | 全enum/name/metric型・キー | 固定十/四・上記二名/型/キー一致 |
| BATCHMET002 | 全canonical文字列lookup | 各literalが同一enumへ、alias/任意値は許可しない |
| BATCHMET003 | null/欠落/大小文字/秘密canary/未知1000個 | 固定CONFIG_INVALID又は境界例外、raw値の反射なし |
| BATCHMET004 | STANDARD/DEBUG/null/未知mode | 詳細false/true/例外、外部service操作なし |
| BATCHMET005 | 十×四のlabel map・変更試行 | 全40でstep/statusだけ、不可変・成功gaugeはstepだけ |
| BATCHREC001 | DEBUG所有実SimpleMeterRegistry生成/全初期値 | counter40/gauge10・全50系列、counter0/lastSuccess NaN（未観測をepoch0にしない） |
| BATCHREC002 | 全40組合せ各一回/固定終了時刻 | 各counter1、SUCCESSのみ各gaugeへ固定秒値、他statusは上書きしない |
| BATCHREC003 | 成功時刻前進/逆行/同値、非success後 | counterは各一回、gauge最大SUCCESS時刻だけ、fraction独立vector一致 |
| BATCHREC004 | STANDARD全状態/null/invalid | 正常は登録/記録0、無効は拒否し詳細disabledでも隠さない |
| BATCHREC005 | constructor/null/UTC0001・9999・範囲外・ns粒度 | 有効両端受理、範囲外/µs外とnullは副作用前に拒否 |
| BATCHREC006 | provider Runtime/NPE/Error/合成OOM/非formatable故障 | 同一Throwable・attempt1・retry0・gauge未更新、registry未close/借用保持 |
| BATCHREC007 | 64並行成功・逆順時刻 | counter64、gauge固定最大時刻、系列50不変 |
| BATCHREC008 | registry登録失敗/別owner/反復入力 | 部分構築失敗は同一伝播・callerがcleanup、別owner独立・生ID系列増加なし |

新13＋必要既140を当source固定後ordinary Maven verify、XML全case/終了/FES0・lint/Werror/NullAway/SB、単一session/CRC/実Main四counter100、PMD/CS個別判定。SDKは既Web同版1.17.1・四Jar元pins PG7106/421/1572、offlineのみ/取得なし。srcBatchPOMは一core依存node追加だけ、harnessも同版を使う。全六通常compile/Jar/source差分・旧1669class不変・traceを別postで確認する。予定PG7252/7254以降manifestへOS/JDK/tool/branch/source・command/日時/終了/XML/coverage/static/path/hashを結合し、未実行は未実行扱い。

実Batch/DB/Backup/Root/provider/exporter/JMX/VM/鍵/配備/GC操作なし。固定Instantはcallerの供給値であり実業務完了・exactly-once・永続lastSuccess bootstrap・parentMorning全体の成功証拠ではない。所有registryは各testが最終closeし、productionへclose権限を渡さない。正式1964/53・歴史17/別source新7/原190新受入0・工数null・QA051final/PTALT0・実HOLD/全体451未受入を維持する。発見障害は修正前に915/916へ起票。
