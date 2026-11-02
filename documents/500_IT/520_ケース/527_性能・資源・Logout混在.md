# 性能・資源・Logout混在 結合テストケース

編集正本は [cases.json](../data/cases.json)。この巻は自動生成。全件NOT_EXECUTED。SUPERSEDEDは旧ID履歴。PENDING_REAUDITは具体シナリオ再監査待ちで、仕様確定・実行可能へ算入しない。

全ケースは [512](../510_方針・準備/512_結合構成・環境・データ.md) の経路・環境・fixture・観測・C-ISOLATE と [541](../540_実行・管理/541_Codex実行・判定・証跡・再開.md) を参照する。共通CP-BASEの入力以外の初期状態・証跡・中断・後片付けは cases.json.profiles に一元化し、個別追加条件と併せて必須とする。

他巻：[インターフェース](521_インターフェース.md) / [トランザクション・データ](522_トランザクション・データ.md) / [認証・権限・セキュリティ](523_認証・権限・セキュリティ.md) / [ファイル・メディア・Range](524_ファイル・メディア・Range.md) / [運用・復旧・監視](525_運用・復旧・監視.md) / [MQ・非同期・容量](526_MQ・非同期・容量.md) / [性能・資源・Logout混在](527_性能・資源・Logout混在.md)

<a id="it-perf-001"></a>
## IT-PERF-001 STANDARD実10名・route別同期SLAと全失敗分母

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧性能観点を固有10session・周期mix・計測窓・独立統計・対象除外根拠まで具体化。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SYNC |
| 確認契約 | STANDARD実10名・route別同期SLAと全失敗分母 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 2 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `7147c428bb9d`
- [342_Caddy・systemd・PostgreSQL・Java設定設計.md](<../../300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md>) Caddy・systemd・PostgreSQL・Java設定設計 > 8. Resource・disk合計・実測gates ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（2件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-001"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 各対象route p95&lt;=2.5s、MQwait各&lt;=2.0s、ID/表示/DB後条件一致、取違え0。timeout/errorを全分母へ記録し該当失敗を合格化0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 計画停止/起動直後/故障中/media全体転送時間の上位明示範囲だけ別窓、任意外れ値削除0。CPU/RSS/heap/direct/meta/GC/thread/FD/pool/lock/WAL/queue/journal/diskを同窓収集。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | DEBUG/instrumented spanの負荷は別対照、正式STANDARDの性能窓にagent付き値を混ぜない。対象計測不能ならNOT_JUDGED、許容差でSLA緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧性能観点を固有10session・周期mix・計測窓・独立統計・対象除外根拠まで具体化。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-001`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-001-s01"></a>
#### IT-PERF-001-S01 / normal10

種類：正常、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "clients": 10,
  "mix100": {
    "Scenario検索": 60,
    "Game一覧": 20,
    "Log一覧ADMIN": 10,
    "質問通知照会": 10
  },
  "schedule": "各user100slotを固定seed20261102でshuffle、ADMIN2のLog割当計20slot/全体1000slot",
  "master": "99661entry/fullasset、Log100/page/通知50/page"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 300秒warmup→1800秒測定を2反復。実Browser入力開始→描画完了とWebMQwaitを独立計測、各route全試行をfreeze。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "最終release/config/schema/protocol/master hashをrun manifestへfreeze",
  "hardware": "16GB/256GB、本番CPU型番/core/周波数/OS/JDKを固定",
  "clients": "USER8+ADMIN2各1inflight/think0 closed loop",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全HTTP/MQ/DB span、OS/PG/JVM/MQ/FD1秒。採取overhead無負荷対照を別保存",
  "statistics": "route/windowごとの全試行raw、p95=昇順ceil(.95*N)番、失敗/timeout/censoredを別件数として全issued分母に保持し成功選別0",
  "sla": "通常10名同期E2Ep95<=2.5s/MQwait各<=2.0s/取り違え0、未規定throughput/error許容率/劣化%を新設0",
  "stop": "所有/source/env変更/証拠欠落/仕様資源上限/安全停止境界で新規発行停止、inflightと未知commitを保全",
  "drain": "120秒の観測終了で残件を0補完0、各ID状態/最古/解消見通しを保全し承認復旧へ",
  "mass_balance": "issued=terminal+outstanding、accepted ID集合=確定unique+明示残件、二重業務更新0/拒否要求の更新0",
  "overrides": {
    "clients": 10,
    "mix100": {
      "Scenario検索": 60,
      "Game一覧": 20,
      "Log一覧ADMIN": 10,
      "質問通知照会": 10
    },
    "schedule": "各user100slotを固定seed20261102でshuffle、ADMIN2のLog割当計20slot/全体1000slot",
    "master": "99661entry/fullasset、Log100/page/通知50/page"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-001-S01/http.jsonl, IT-PERF-001-S01/wire.jsonl, IT-PERF-001-S01/db.jsonl, IT-PERF-001-S01/mq.jsonl, IT-PERF-001-S01/metric.jsonl, IT-PERF-001-S01/time.jsonl | 各対象route p95&lt;=2.5s、MQwait各&lt;=2.0s、ID/表示/DB後条件一致、取違え0。timeout/errorを全分母へ記録し該当失敗を合格化0。 |
| A02 | IT-PERF-001-S01/http.jsonl, IT-PERF-001-S01/wire.jsonl, IT-PERF-001-S01/db.jsonl, IT-PERF-001-S01/mq.jsonl, IT-PERF-001-S01/metric.jsonl, IT-PERF-001-S01/time.jsonl | 計画停止/起動直後/故障中/media全体転送時間の上位明示範囲だけ別窓、任意外れ値削除0。CPU/RSS/heap/direct/meta/GC/thread/FD/pool/lock/WAL/queue/journal/diskを同窓収集。 |
| A03 | IT-PERF-001-S01/http.jsonl, IT-PERF-001-S01/wire.jsonl, IT-PERF-001-S01/db.jsonl, IT-PERF-001-S01/mq.jsonl, IT-PERF-001-S01/metric.jsonl, IT-PERF-001-S01/time.jsonl | DEBUG/instrumented spanの負荷は別対照、正式STANDARDの性能窓にagent付き値を混ぜない。対象計測不能ならNOT_JUDGED、許容差でSLA緩和0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-002"></a>
## IT-PERF-002 20stream・最大SCN・worstSQLの資源競合

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

並行数/route比率/最大recordとbyteを固定し、転送全長と同期開始SLAを分離。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | 20stream・最大SCN・worstSQLの資源競合 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 100 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `7147c428bb9d`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（2件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-002"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 同期対象routep95&lt;=2.5s/MQwait&lt;=2.0s、Range開始時間別記、全転送時間を同期p95へ混合0。active stream&lt;=20、21番はRANGE020の拒否/permit回収を別判定。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-FS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | SCN10000/48000000byte/独立hash/順序、検索100/log100/新規通知50、wireplaintext&lt;=1000000/cipher上限はsnapshot別測定。FD/thread/direct/heap/pool/lockが設計上限、終端permit/FD残留0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-FS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 各QueryID/plan/rows/loops/statement数を対応、N+1/非限定loadを検出。既受付を容量制御で消去0、全logicalID別のmassbalance成立。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-FS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

並行数/route比率/最大recordとbyteを固定し、転送全長と同期開始SLAを分離。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-002`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-002-s01"></a>
#### IT-PERF-002-S01 / media20_sync10

種類：競合、反復：100、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "sync_clients": 10,
  "mix100": {
    "worstSearch": 40,
    "SCN10000": 20,
    "Log100": 20,
    "NTS50": 20
  },
  "media_clients": 20,
  "media": "audio401/402交互、Range0-1048575を完了後再発行",
  "SCN": "5000entry×voice2=10000record/48000000byte"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 通常10名窓と同sourcefixtureで300秒warmup→1800秒測定2反復、20streamを実body終端まで保持。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "最終release/config/schema/protocol/master hashをrun manifestへfreeze",
  "hardware": "16GB/256GB、本番CPU型番/core/周波数/OS/JDKを固定",
  "clients": "USER8+ADMIN2各1inflight/think0 closed loop",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全HTTP/MQ/DB span、OS/PG/JVM/MQ/FD1秒。採取overhead無負荷対照を別保存",
  "statistics": "route/windowごとの全試行raw、p95=昇順ceil(.95*N)番、失敗/timeout/censoredを別件数として全issued分母に保持し成功選別0",
  "sla": "通常10名同期E2Ep95<=2.5s/MQwait各<=2.0s/取り違え0、未規定throughput/error許容率/劣化%を新設0",
  "stop": "所有/source/env変更/証拠欠落/仕様資源上限/安全停止境界で新規発行停止、inflightと未知commitを保全",
  "drain": "120秒の観測終了で残件を0補完0、各ID状態/最古/解消見通しを保全し承認復旧へ",
  "mass_balance": "issued=terminal+outstanding、accepted ID集合=確定unique+明示残件、二重業務更新0/拒否要求の更新0",
  "overrides": {
    "sync_clients": 10,
    "mix100": {
      "worstSearch": 40,
      "SCN10000": 20,
      "Log100": 20,
      "NTS50": 20
    },
    "media_clients": 20,
    "media": "audio401/402交互、Range0-1048575を完了後再発行",
    "SCN": "5000entry×voice2=10000record/48000000byte"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-002-S01/http.jsonl, IT-PERF-002-S01/wire.jsonl, IT-PERF-002-S01/db.jsonl, IT-PERF-002-S01/mq.jsonl, IT-PERF-002-S01/fs.jsonl, IT-PERF-002-S01/metric.jsonl, IT-PERF-002-S01/time.jsonl | 同期対象routep95&lt;=2.5s/MQwait&lt;=2.0s、Range開始時間別記、全転送時間を同期p95へ混合0。active stream&lt;=20、21番はRANGE020の拒否/permit回収を別判定。 |
| A02 | IT-PERF-002-S01/http.jsonl, IT-PERF-002-S01/wire.jsonl, IT-PERF-002-S01/db.jsonl, IT-PERF-002-S01/mq.jsonl, IT-PERF-002-S01/fs.jsonl, IT-PERF-002-S01/metric.jsonl, IT-PERF-002-S01/time.jsonl | SCN10000/48000000byte/独立hash/順序、検索100/log100/新規通知50、wireplaintext&lt;=1000000/cipher上限はsnapshot別測定。FD/thread/direct/heap/pool/lockが設計上限、終端permit/FD残留0。 |
| A03 | IT-PERF-002-S01/http.jsonl, IT-PERF-002-S01/wire.jsonl, IT-PERF-002-S01/db.jsonl, IT-PERF-002-S01/mq.jsonl, IT-PERF-002-S01/fs.jsonl, IT-PERF-002-S01/metric.jsonl, IT-PERF-002-S01/time.jsonl | 各QueryID/plan/rows/loops/statement数を対応、N+1/非限定loadを検出。既受付を容量制御で消去0、全logicalID別のmassbalance成立。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-003"></a>
## IT-PERF-003 host16GB・disk256GBとprocess上限の実収支

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

RSS/割当/プランナhintを二重計上せず全構成の実効上限とピークを同時間軸で照合。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-OPS |
| 確認契約 | host16GB・disk256GBとprocess上限の実収支 |
| 必要環境 | E-OPS |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 2 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [342_Caddy・systemd・PostgreSQL・Java設定設計.md](<../../300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md>) Caddy・systemd・PostgreSQL・Java設定設計 > 8. Resource・disk合計・実測gates ／ 固定承認本文 ／ commit `7147c428bb9d`
- [342_Caddy・systemd・PostgreSQL・Java設定設計.md](<../../300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md>) Caddy・systemd・PostgreSQL・Java設定設計 > 8. Resource・disk合計・実測gates ／ 固定承認本文 ／ commit `7147c428bb9d`
- [342_Caddy・systemd・PostgreSQL・Java設定設計.md](<../../300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md>) Caddy・systemd・PostgreSQL・Java設定設計 > 5. Java/JVM・Spring process > 5.1 Resource ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-003"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 16GB配分/各MemoryMax Web1536M/API2048M/Batch1536M/Artemis2048Mとheap/direct/meta表値以内。native/headroom0へ設定0、effective_cache_size6GBはallocation加算0、共有PGpage二重計数0。 | O-OS, O-METRIC, O-DB, O-MQ, O-FS, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | SSD256GB配分合計256GB、Artemisjournal/paging10GiB予算とpayload上限/metadataoverheadを別計測、PGWAL/temp/backup7世代80GB/transfer5GB、STANDARD詳細DEBUG保存なし。 | O-OS, O-METRIC, O-DB, O-MQ, O-FS, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 上限超過前の警告/critical/9001/ready制御と既受付/証跡保全を各容量caseへ照合。目標達成のためMemoryMax/上位予算を勝手に拡大0。 | O-OS, O-METRIC, O-DB, O-MQ, O-FS, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | batch/Inspector/PG/Artemisは設計の同時phaseだけ積算、停止中API/Web枠を二重常時使用しない。diskpeakにはpartと旧7世代併存を含め、保持失敗で旧成功削除0。 | O-OS, O-DB, O-MQ, O-FS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 復旧後10名窓のSLA/資源収束を測定、maintenance停止窓と正常窓を混合0。 | O-OS, O-DB, O-MQ, O-FS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, DEP-OPS-HOLD を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

RSS/割当/プランナhintを二重計上せず全構成の実効上限とピークを同時間軸で照合。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-003`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-003-s01"></a>
#### IT-PERF-003-S01 / normal_peak

種類：正常、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "workload": "PERF002の10sync+20stream+SCN10000",
  "budgets_GB": {
    "PG": 4,
    "Artemis": 2,
    "API": 2,
    "Web": 1.5,
    "OS_Caddy_cache": 3,
    "Safety_DEBUG": 3.5
  },
  "disk_GB": [
    45,
    35,
    30,
    10,
    5,
    10,
    80,
    5,
    36
  ]
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 300秒warmup→1800秒測定2反復、hostcgroupとprocessRSS/heap/direct/metaspace/nativeを重複排除して採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "最終release/config/schema/protocol/master hashをrun manifestへfreeze",
  "hardware": "16GB/256GB、本番CPU型番/core/周波数/OS/JDKを固定",
  "clients": "USER8+ADMIN2各1inflight/think0 closed loop",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全HTTP/MQ/DB span、OS/PG/JVM/MQ/FD1秒。採取overhead無負荷対照を別保存",
  "statistics": "route/windowごとの全試行raw、p95=昇順ceil(.95*N)番、失敗/timeout/censoredを別件数として全issued分母に保持し成功選別0",
  "sla": "通常10名同期E2Ep95<=2.5s/MQwait各<=2.0s/取り違え0、未規定throughput/error許容率/劣化%を新設0",
  "stop": "所有/source/env変更/証拠欠落/仕様資源上限/安全停止境界で新規発行停止、inflightと未知commitを保全",
  "drain": "120秒の観測終了で残件を0補完0、各ID状態/最古/解消見通しを保全し承認復旧へ",
  "mass_balance": "issued=terminal+outstanding、accepted ID集合=確定unique+明示残件、二重業務更新0/拒否要求の更新0",
  "overrides": {
    "workload": "PERF002の10sync+20stream+SCN10000",
    "budgets_GB": {
      "PG": 4,
      "Artemis": 2,
      "API": 2,
      "Web": 1.5,
      "OS_Caddy_cache": 3,
      "Safety_DEBUG": 3.5
    },
    "disk_GB": [
      45,
      35,
      30,
      10,
      5,
      10,
      80,
      5,
      36
    ]
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-003-S01/os.jsonl, IT-PERF-003-S01/metric.jsonl, IT-PERF-003-S01/db.jsonl, IT-PERF-003-S01/mq.jsonl, IT-PERF-003-S01/fs.jsonl, IT-PERF-003-S01/time.jsonl | 16GB配分/各MemoryMax Web1536M/API2048M/Batch1536M/Artemis2048Mとheap/direct/meta表値以内。native/headroom0へ設定0、effective_cache_size6GBはallocation加算0、共有PGpage二重計数0。 |
| A02 | IT-PERF-003-S01/os.jsonl, IT-PERF-003-S01/metric.jsonl, IT-PERF-003-S01/db.jsonl, IT-PERF-003-S01/mq.jsonl, IT-PERF-003-S01/fs.jsonl, IT-PERF-003-S01/time.jsonl | SSD256GB配分合計256GB、Artemisjournal/paging10GiB予算とpayload上限/metadataoverheadを別計測、PGWAL/temp/backup7世代80GB/transfer5GB、STANDARD詳細DEBUG保存なし。 |
| A03 | IT-PERF-003-S01/os.jsonl, IT-PERF-003-S01/metric.jsonl, IT-PERF-003-S01/db.jsonl, IT-PERF-003-S01/mq.jsonl, IT-PERF-003-S01/fs.jsonl, IT-PERF-003-S01/time.jsonl | 上限超過前の警告/critical/9001/ready制御と既受付/証跡保全を各容量caseへ照合。目標達成のためMemoryMax/上位予算を勝手に拡大0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-003-s02"></a>
#### IT-PERF-003-S02 / maintenance_peak

種類：正常、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "public": "停止/正規M/A保持",
  "backup": "実7世代→新世代/retention",
  "cleanup": "log10001/通常kind1001/Inspector1001"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：親元1800秒+再開後300warmup/1800測定、過去親timeoutを延長して救済0。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 通常業務と同時稼働させず正規Morning内の実dump/tar/age/cleanup時ピークを採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "最終release/config/schema/protocol/master hashをrun manifestへfreeze",
  "hardware": "16GB/256GB、本番CPU型番/core/周波数/OS/JDKを固定",
  "clients": "USER8+ADMIN2各1inflight/think0 closed loop",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全HTTP/MQ/DB span、OS/PG/JVM/MQ/FD1秒。採取overhead無負荷対照を別保存",
  "statistics": "route/windowごとの全試行raw、p95=昇順ceil(.95*N)番、失敗/timeout/censoredを別件数として全issued分母に保持し成功選別0",
  "sla": "通常10名同期E2Ep95<=2.5s/MQwait各<=2.0s/取り違え0、未規定throughput/error許容率/劣化%を新設0",
  "stop": "所有/source/env変更/証拠欠落/仕様資源上限/安全停止境界で新規発行停止、inflightと未知commitを保全",
  "drain": "120秒の観測終了で残件を0補完0、各ID状態/最古/解消見通しを保全し承認復旧へ",
  "mass_balance": "issued=terminal+outstanding、accepted ID集合=確定unique+明示残件、二重業務更新0/拒否要求の更新0",
  "overrides": {
    "public": "停止/正規M/A保持",
    "backup": "実7世代→新世代/retention",
    "cleanup": "log10001/通常kind1001/Inspector1001"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A04 | IT-PERF-003-S02/os.jsonl, IT-PERF-003-S02/db.jsonl, IT-PERF-003-S02/mq.jsonl, IT-PERF-003-S02/fs.jsonl, IT-PERF-003-S02/metric.jsonl, IT-PERF-003-S02/time.jsonl | batch/Inspector/PG/Artemisは設計の同時phaseだけ積算、停止中API/Web枠を二重常時使用しない。diskpeakにはpartと旧7世代併存を含め、保持失敗で旧成功削除0。 |
| A05 | IT-PERF-003-S02/os.jsonl, IT-PERF-003-S02/db.jsonl, IT-PERF-003-S02/mq.jsonl, IT-PERF-003-S02/fs.jsonl, IT-PERF-003-S02/metric.jsonl, IT-PERF-003-S02/time.jsonl | 復旧後10名窓のSLA/資源収束を測定、maintenance停止窓と正常窓を混合0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-010"></a>
## IT-PERF-010 Transfer bytes warning/critical境界matrix

仕様：**PENDING_DECISION** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧5caseの値差を1familyへ統合。scan値/新規拒否/既受付非破壊を各入力行で追跡。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Transfer bytes warning/critical境界matrix |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 100 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（1件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-010"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 開始時warning=false、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 今回201record/964800byteの追加後もcritical未満。容量以外正常ならF成功/ready1、rootbyteは+964800/count+1、warning/critical判定は独立整数表。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 開始時warning=true、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 今回201record/964800byteの追加後もcritical未満。容量以外正常ならF成功/ready1、rootbyteは+964800/count+1、warning/critical判定は独立整数表。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 開始時warning=true、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A06 | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A07 | 開始時warning=true、critical=true。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A08 | 開始時critical到達済みなので新規Fは9001/新part・ready0、rootbyte/count/旧Inboxsnapshot非更新。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A09 | 開始時warning=true、critical=true。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A10 | 開始時critical到達済みなので新規Fは9001/新part・ready0、rootbyte/count/旧Inboxsnapshot非更新。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A11 | 実root5GB上限超過0/既存ready非削除、各成功file48000000byte/10000record/hash完全一致、公開UNKNOWNは保全。 | O-FS, O-DB, O-MQ, O-WIRE, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A12 | critical4.5GB未満で全要求が同時判定したときの先行予約・受理数・9001発生点はISS-TRANSFERの判断待ち。観測結果を正解へ逆輸入せず当該predicateだけNOT_JUDGED。 | O-FS, O-DB, O-MQ, O-WIRE, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A13 | 初回最大8fileを全て許した場合でもpeak4883000000byteで5GB未満。既定API8/Web20を超える人工並行で上限逸脱を作らない。 | O-FS, O-DB, O-MQ, O-WIRE, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：ISS-TRANSFER。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧5caseの値差を1familyへ統合。scan値/新規拒否/既受付非破壊を各入力行で追跡。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-010`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-010-s01"></a>
#### IT-PERF-010-S01 / 3499999999

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "root_bytes": 3499999999,
  "SCN_records": 201,
  "other_axis": "files=100 (<5000)"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. exclusive完全scan→新規SCN201recordを一回要求。scan値/警報/予約/公開/応答を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-010-S01/fs.jsonl, IT-PERF-010-S01/db.jsonl, IT-PERF-010-S01/wire.jsonl, IT-PERF-010-S01/metric.jsonl | 開始時warning=false、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 |
| A02 | IT-PERF-010-S01/fs.jsonl, IT-PERF-010-S01/db.jsonl, IT-PERF-010-S01/wire.jsonl, IT-PERF-010-S01/metric.jsonl | 今回201record/964800byteの追加後もcritical未満。容量以外正常ならF成功/ready1、rootbyteは+964800/count+1、warning/critical判定は独立整数表。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-010-s02"></a>
#### IT-PERF-010-S02 / 3500000000

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "root_bytes": 3500000000,
  "SCN_records": 201,
  "other_axis": "files=100 (<5000)"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. exclusive完全scan→新規SCN201recordを一回要求。scan値/警報/予約/公開/応答を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A03 | IT-PERF-010-S02/fs.jsonl, IT-PERF-010-S02/db.jsonl, IT-PERF-010-S02/wire.jsonl, IT-PERF-010-S02/metric.jsonl | 開始時warning=true、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 |
| A04 | IT-PERF-010-S02/fs.jsonl, IT-PERF-010-S02/db.jsonl, IT-PERF-010-S02/wire.jsonl, IT-PERF-010-S02/metric.jsonl | 今回201record/964800byteの追加後もcritical未満。容量以外正常ならF成功/ready1、rootbyteは+964800/count+1、warning/critical判定は独立整数表。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-010-s03"></a>
#### IT-PERF-010-S03 / 4499999999

種類：境界、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "root_bytes": 4499999999,
  "SCN_records": 201,
  "other_axis": "files=100 (<5000)"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. exclusive完全scan→新規SCN201recordを一回要求。scan値/警報/予約/公開/応答を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A05 | IT-PERF-010-S03/fs.jsonl, IT-PERF-010-S03/db.jsonl, IT-PERF-010-S03/wire.jsonl, IT-PERF-010-S03/metric.jsonl | 開始時warning=true、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 |
| A06 | IT-PERF-010-S03/fs.jsonl, IT-PERF-010-S03/db.jsonl, IT-PERF-010-S03/wire.jsonl, IT-PERF-010-S03/metric.jsonl | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-010-s04"></a>
#### IT-PERF-010-S04 / 4500000000

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "root_bytes": 4500000000,
  "SCN_records": 201,
  "other_axis": "files=100 (<5000)"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. exclusive完全scan→新規SCN201recordを一回要求。scan値/警報/予約/公開/応答を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A07 | IT-PERF-010-S04/fs.jsonl, IT-PERF-010-S04/db.jsonl, IT-PERF-010-S04/wire.jsonl, IT-PERF-010-S04/metric.jsonl | 開始時warning=true、critical=true。criticalなら9001/ready新規0。既存ready自動削除0。 |
| A08 | IT-PERF-010-S04/fs.jsonl, IT-PERF-010-S04/db.jsonl, IT-PERF-010-S04/wire.jsonl, IT-PERF-010-S04/metric.jsonl | 開始時critical到達済みなので新規Fは9001/新part・ready0、rootbyte/count/旧Inboxsnapshot非更新。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-010-s05"></a>
#### IT-PERF-010-S05 / 5000000000

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "root_bytes": 5000000000,
  "SCN_records": 201,
  "other_axis": "files=100 (<5000)"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. exclusive完全scan→新規SCN201recordを一回要求。scan値/警報/予約/公開/応答を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A09 | IT-PERF-010-S05/fs.jsonl, IT-PERF-010-S05/db.jsonl, IT-PERF-010-S05/wire.jsonl, IT-PERF-010-S05/metric.jsonl | 開始時warning=true、critical=true。criticalなら9001/ready新規0。既存ready自動削除0。 |
| A10 | IT-PERF-010-S05/fs.jsonl, IT-PERF-010-S05/db.jsonl, IT-PERF-010-S05/wire.jsonl, IT-PERF-010-S05/metric.jsonl | 開始時critical到達済みなので新規Fは9001/新part・ready0、rootbyte/count/旧Inboxsnapshot非更新。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-010-s06"></a>
#### IT-PERF-010-S06 / concurrent_quota

種類：競合、反復：100、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "root_bytes": 4499000000,
  "root_files": 100,
  "requests": 8,
  "each_record_count": 10000,
  "each_file_bytes": 48000000,
  "barrier": "各quota確認前、8consumer既定max8以内、同一runの別Message/token/UUID"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：barrier解除を各2秒残余内に収める。timeoutは元Message/tokenを保全、終端確認120秒/UNKNOWN再送0。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 8要求をquota判定入口で同時解放し、公開前後のlogicalbyte/予約/実file/応答を全timeline採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A11 | IT-PERF-010-S06/fs.jsonl, IT-PERF-010-S06/db.jsonl, IT-PERF-010-S06/mq.jsonl, IT-PERF-010-S06/wire.jsonl, IT-PERF-010-S06/metric.jsonl, IT-PERF-010-S06/time.jsonl | 実root5GB上限超過0/既存ready非削除、各成功file48000000byte/10000record/hash完全一致、公開UNKNOWNは保全。 |
| A12 | IT-PERF-010-S06/fs.jsonl, IT-PERF-010-S06/db.jsonl, IT-PERF-010-S06/mq.jsonl, IT-PERF-010-S06/wire.jsonl, IT-PERF-010-S06/metric.jsonl, IT-PERF-010-S06/time.jsonl | critical4.5GB未満で全要求が同時判定したときの先行予約・受理数・9001発生点はISS-TRANSFERの判断待ち。観測結果を正解へ逆輸入せず当該predicateだけNOT_JUDGED。 |
| A13 | IT-PERF-010-S06/fs.jsonl, IT-PERF-010-S06/db.jsonl, IT-PERF-010-S06/mq.jsonl, IT-PERF-010-S06/wire.jsonl, IT-PERF-010-S06/metric.jsonl, IT-PERF-010-S06/time.jsonl | 初回最大8fileを全て許した場合でもpeak4883000000byteで5GB未満。既定API8/Web20を超える人工並行で上限逸脱を作らない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-011"></a>
## IT-PERF-011（統合済・実行対象外）

継続先：[IT-PERF-010](527_性能・資源・Logout混在.md#it-perf-010)。byte境界5SCへ統合。

<a id="it-perf-012"></a>
## IT-PERF-012（統合済・実行対象外）

継続先：[IT-PERF-010](527_性能・資源・Logout混在.md#it-perf-010)。byte境界5SCへ統合。

<a id="it-perf-013"></a>
## IT-PERF-013（統合済・実行対象外）

継続先：[IT-PERF-010](527_性能・資源・Logout混在.md#it-perf-010)。byte境界5SCへ統合。

<a id="it-perf-014"></a>
## IT-PERF-014（統合済・実行対象外）

継続先：[IT-PERF-010](527_性能・資源・Logout混在.md#it-perf-010)。byte境界5SCへ統合。

<a id="it-perf-020"></a>
## IT-PERF-020 Transfer count warning/critical境界matrix

仕様：**PENDING_DECISION** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧5caseの値差を1familyへ統合。scan値/新規拒否/既受付非破壊を各入力行で追跡。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Transfer count warning/critical境界matrix |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 100 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 13. Capacity・metric・alert ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（2件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-020"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 開始時warning=false、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 今回201record/964800byteの追加後もcritical未満。容量以外正常ならF成功/ready1、rootbyteは+964800/count+1、warning/critical判定は独立整数表。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 開始時warning=true、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 今回201record/964800byteの追加後もcritical未満。容量以外正常ならF成功/ready1、rootbyteは+964800/count+1、warning/critical判定は独立整数表。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 開始時warning=true、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A06 | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A07 | 開始時warning=true、critical=true。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A08 | 開始時critical到達済みなので新規Fは9001/新part・ready0、rootbyte/count/旧Inboxsnapshot非更新。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A09 | 開始時warning=true、critical=true。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A10 | 開始時critical到達済みなので新規Fは9001/新part・ready0、rootbyte/count/旧Inboxsnapshot非更新。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A11 | 10000上限超過0/既存file削除0、最大8受理でも9007件、logicalbytes107718400byte。新規file完全性/公開UNKNOWN保全。 | O-FS, O-DB, O-MQ, O-WIRE, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A12 | 9000到達を跨ぐ先行予約・受理数・拒否発生点だけISS-TRANSFER判断待ち。解放後全要求終端/FDpoolbefore、既定並行上限を増加0。 | O-FS, O-DB, O-MQ, O-WIRE, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：ISS-TRANSFER。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧5caseの値差を1familyへ統合。scan値/新規拒否/既受付非破壊を各入力行で追跡。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-020`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-020-s01"></a>
#### IT-PERF-020-S01 / 4999

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "root_count": 4999,
  "SCN_records": 201,
  "other_axis": "bytes=100000000 (<3.5GB)"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. exclusive完全scan→新規SCN201recordを一回要求。scan値/警報/予約/公開/応答を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-020-S01/fs.jsonl, IT-PERF-020-S01/db.jsonl, IT-PERF-020-S01/wire.jsonl, IT-PERF-020-S01/metric.jsonl | 開始時warning=false、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 |
| A02 | IT-PERF-020-S01/fs.jsonl, IT-PERF-020-S01/db.jsonl, IT-PERF-020-S01/wire.jsonl, IT-PERF-020-S01/metric.jsonl | 今回201record/964800byteの追加後もcritical未満。容量以外正常ならF成功/ready1、rootbyteは+964800/count+1、warning/critical判定は独立整数表。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-020-s02"></a>
#### IT-PERF-020-S02 / 5000

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "root_count": 5000,
  "SCN_records": 201,
  "other_axis": "bytes=100000000 (<3.5GB)"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. exclusive完全scan→新規SCN201recordを一回要求。scan値/警報/予約/公開/応答を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A03 | IT-PERF-020-S02/fs.jsonl, IT-PERF-020-S02/db.jsonl, IT-PERF-020-S02/wire.jsonl, IT-PERF-020-S02/metric.jsonl | 開始時warning=true、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 |
| A04 | IT-PERF-020-S02/fs.jsonl, IT-PERF-020-S02/db.jsonl, IT-PERF-020-S02/wire.jsonl, IT-PERF-020-S02/metric.jsonl | 今回201record/964800byteの追加後もcritical未満。容量以外正常ならF成功/ready1、rootbyteは+964800/count+1、warning/critical判定は独立整数表。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-020-s03"></a>
#### IT-PERF-020-S03 / 8999

種類：境界、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "root_count": 8999,
  "SCN_records": 201,
  "other_axis": "bytes=100000000 (<3.5GB)"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. exclusive完全scan→新規SCN201recordを一回要求。scan値/警報/予約/公開/応答を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A05 | IT-PERF-020-S03/fs.jsonl, IT-PERF-020-S03/db.jsonl, IT-PERF-020-S03/wire.jsonl, IT-PERF-020-S03/metric.jsonl | 開始時warning=true、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 |
| A06 | IT-PERF-020-S03/fs.jsonl, IT-PERF-020-S03/db.jsonl, IT-PERF-020-S03/wire.jsonl, IT-PERF-020-S03/metric.jsonl | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-020-s04"></a>
#### IT-PERF-020-S04 / 9000

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "root_count": 9000,
  "SCN_records": 201,
  "other_axis": "bytes=100000000 (<3.5GB)"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. exclusive完全scan→新規SCN201recordを一回要求。scan値/警報/予約/公開/応答を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A07 | IT-PERF-020-S04/fs.jsonl, IT-PERF-020-S04/db.jsonl, IT-PERF-020-S04/wire.jsonl, IT-PERF-020-S04/metric.jsonl | 開始時warning=true、critical=true。criticalなら9001/ready新規0。既存ready自動削除0。 |
| A08 | IT-PERF-020-S04/fs.jsonl, IT-PERF-020-S04/db.jsonl, IT-PERF-020-S04/wire.jsonl, IT-PERF-020-S04/metric.jsonl | 開始時critical到達済みなので新規Fは9001/新part・ready0、rootbyte/count/旧Inboxsnapshot非更新。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-020-s05"></a>
#### IT-PERF-020-S05 / 10000

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "root_count": 10000,
  "SCN_records": 201,
  "other_axis": "bytes=100000000 (<3.5GB)"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. exclusive完全scan→新規SCN201recordを一回要求。scan値/警報/予約/公開/応答を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A09 | IT-PERF-020-S05/fs.jsonl, IT-PERF-020-S05/db.jsonl, IT-PERF-020-S05/wire.jsonl, IT-PERF-020-S05/metric.jsonl | 開始時warning=true、critical=true。criticalなら9001/ready新規0。既存ready自動削除0。 |
| A10 | IT-PERF-020-S05/fs.jsonl, IT-PERF-020-S05/db.jsonl, IT-PERF-020-S05/wire.jsonl, IT-PERF-020-S05/metric.jsonl | 開始時critical到達済みなので新規Fは9001/新part・ready0、rootbyte/count/旧Inboxsnapshot非更新。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-020-s06"></a>
#### IT-PERF-020-S06 / concurrent_count

種類：競合、反復：100、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "root_count": 8999,
  "root_bytes": 100000000,
  "requests": 8,
  "each_record_count": 201,
  "each_file_bytes": 964800
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 8要求をquota入口barrierで同時解放し、rootcount/予約/公開/9001の順序を全採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A11 | IT-PERF-020-S06/fs.jsonl, IT-PERF-020-S06/db.jsonl, IT-PERF-020-S06/mq.jsonl, IT-PERF-020-S06/wire.jsonl, IT-PERF-020-S06/metric.jsonl, IT-PERF-020-S06/time.jsonl | 10000上限超過0/既存file削除0、最大8受理でも9007件、logicalbytes107718400byte。新規file完全性/公開UNKNOWN保全。 |
| A12 | IT-PERF-020-S06/fs.jsonl, IT-PERF-020-S06/db.jsonl, IT-PERF-020-S06/mq.jsonl, IT-PERF-020-S06/wire.jsonl, IT-PERF-020-S06/metric.jsonl, IT-PERF-020-S06/time.jsonl | 9000到達を跨ぐ先行予約・受理数・拒否発生点だけISS-TRANSFER判断待ち。解放後全要求終端/FDpoolbefore、既定並行上限を増加0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-021"></a>
## IT-PERF-021（統合済・実行対象外）

継続先：[IT-PERF-020](527_性能・資源・Logout混在.md#it-perf-020)。件数境界5SCへ統合。

<a id="it-perf-022"></a>
## IT-PERF-022（統合済・実行対象外）

継続先：[IT-PERF-020](527_性能・資源・Logout混在.md#it-perf-020)。件数境界5SCへ統合。

<a id="it-perf-023"></a>
## IT-PERF-023（統合済・実行対象外）

継続先：[IT-PERF-020](527_性能・資源・Logout混在.md#it-perf-020)。件数境界5SCへ統合。

<a id="it-perf-024"></a>
## IT-PERF-024（統合済・実行対象外）

継続先：[IT-PERF-020](527_性能・資源・Logout混在.md#it-perf-020)。件数境界5SCへ統合。

<a id="it-retry-100-集中-なし"></a>
## IT-RETRY-100-集中-なし QA050 size/fault/due分布の選定matrix

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

初版18caseの値名違いを9parameter行へ統合。全size×fault pairと両due分布/各faultの分布を保持し、根拠なき三因子積を撤回。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050 size/fault/due分布の選定matrix |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 2 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > QA-050承認反映：再試行のPT・IT/STと間隔調整（2026-10-03） ／ ['QA-050'] ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（1件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-RETRY-100-集中-なし"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A06 | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A07 | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A08 | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A09 | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A10 | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A11 | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A12 | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A13 | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A14 | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A15 | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A16 | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A17 | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A18 | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A19 | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A20 | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A21 | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A22 | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A23 | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A24 | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A25 | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A26 | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A27 | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

初版18caseの値名違いを9parameter行へ統合。全size×fault pairと両due分布/各faultの分布を保持し、根拠なき三因子積を撤回。

QA050の容量点・故障種・due形態をpairwiseで選定。同じretry契約なのでcase1、具体9SC、反復は別。除外9組は第三因子相互作用が未規定、異常実測/設計変更で追加する。

契約：`ITC-RETRY-100-集中-なし`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-retry-100-集中-なし-s01"></a>
#### IT-RETRY-100-集中-なし-S01 / 100_集中_なし

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "due_rows": 100,
  "distribution": "集中",
  "due": "集中=t0、分散=900秒へ等間隔(i*900/N秒)",
  "fault": "なし",
  "normal_workload": "10名/search60/game20/QSB10/NTS10",
  "workers": 2,
  "protected": "別群:物理session削除0102/復号不能各10row"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：専有APIまたはBrokerの所有Unit停止/復帰（なしは注入0）。待機：各対照45分+混在45分、復旧/drain15分上限。未解消は保全し収束0と見なさない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同source正常対照45分と同一45分混在窓。初期5/30/300秒、その後900秒定常を少なくとも2周期実時間で観測。故障ありはt0+60秒停止→+90秒復帰。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 2700,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "comparison_seconds": 2700
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-RETRY-100-集中-なし-S01/http.jsonl, IT-RETRY-100-集中-なし-S01/wire.jsonl, IT-RETRY-100-集中-なし-S01/db.jsonl, IT-RETRY-100-集中-なし-S01/mq.jsonl, IT-RETRY-100-集中-なし-S01/metric.jsonl, IT-RETRY-100-集中-なし-S01/time.jsonl | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 |
| A02 | IT-RETRY-100-集中-なし-S01/http.jsonl, IT-RETRY-100-集中-なし-S01/wire.jsonl, IT-RETRY-100-集中-なし-S01/db.jsonl, IT-RETRY-100-集中-なし-S01/mq.jsonl, IT-RETRY-100-集中-なし-S01/metric.jsonl, IT-RETRY-100-集中-なし-S01/time.jsonl | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 |
| A03 | IT-RETRY-100-集中-なし-S01/http.jsonl, IT-RETRY-100-集中-なし-S01/wire.jsonl, IT-RETRY-100-集中-なし-S01/db.jsonl, IT-RETRY-100-集中-なし-S01/mq.jsonl, IT-RETRY-100-集中-なし-S01/metric.jsonl, IT-RETRY-100-集中-なし-S01/time.jsonl | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-retry-100-集中-なし-s02"></a>
#### IT-RETRY-100-集中-なし-S02 / 100_分散_API停止復帰

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "due_rows": 100,
  "distribution": "分散",
  "due": "集中=t0、分散=900秒へ等間隔(i*900/N秒)",
  "fault": "API停止復帰",
  "normal_workload": "10名/search60/game20/QSB10/NTS10",
  "workers": 2,
  "protected": "別群:物理session削除0102/復号不能各10row"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：専有APIまたはBrokerの所有Unit停止/復帰（なしは注入0）。待機：各対照45分+混在45分、復旧/drain15分上限。未解消は保全し収束0と見なさない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同source正常対照45分と同一45分混在窓。初期5/30/300秒、その後900秒定常を少なくとも2周期実時間で観測。故障ありはt0+60秒停止→+90秒復帰。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 2700,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "comparison_seconds": 2700
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A04 | IT-RETRY-100-集中-なし-S02/http.jsonl, IT-RETRY-100-集中-なし-S02/wire.jsonl, IT-RETRY-100-集中-なし-S02/db.jsonl, IT-RETRY-100-集中-なし-S02/mq.jsonl, IT-RETRY-100-集中-なし-S02/metric.jsonl, IT-RETRY-100-集中-なし-S02/time.jsonl | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 |
| A05 | IT-RETRY-100-集中-なし-S02/http.jsonl, IT-RETRY-100-集中-なし-S02/wire.jsonl, IT-RETRY-100-集中-なし-S02/db.jsonl, IT-RETRY-100-集中-なし-S02/mq.jsonl, IT-RETRY-100-集中-なし-S02/metric.jsonl, IT-RETRY-100-集中-なし-S02/time.jsonl | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 |
| A06 | IT-RETRY-100-集中-なし-S02/http.jsonl, IT-RETRY-100-集中-なし-S02/wire.jsonl, IT-RETRY-100-集中-なし-S02/db.jsonl, IT-RETRY-100-集中-なし-S02/mq.jsonl, IT-RETRY-100-集中-なし-S02/metric.jsonl, IT-RETRY-100-集中-なし-S02/time.jsonl | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-retry-100-集中-なし-s03"></a>
#### IT-RETRY-100-集中-なし-S03 / 100_集中_Broker停止復帰

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "due_rows": 100,
  "distribution": "集中",
  "due": "集中=t0、分散=900秒へ等間隔(i*900/N秒)",
  "fault": "Broker停止復帰",
  "normal_workload": "10名/search60/game20/QSB10/NTS10",
  "workers": 2,
  "protected": "別群:物理session削除0102/復号不能各10row"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：専有APIまたはBrokerの所有Unit停止/復帰（なしは注入0）。待機：各対照45分+混在45分、復旧/drain15分上限。未解消は保全し収束0と見なさない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同source正常対照45分と同一45分混在窓。初期5/30/300秒、その後900秒定常を少なくとも2周期実時間で観測。故障ありはt0+60秒停止→+90秒復帰。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 2700,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "comparison_seconds": 2700
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A07 | IT-RETRY-100-集中-なし-S03/http.jsonl, IT-RETRY-100-集中-なし-S03/wire.jsonl, IT-RETRY-100-集中-なし-S03/db.jsonl, IT-RETRY-100-集中-なし-S03/mq.jsonl, IT-RETRY-100-集中-なし-S03/metric.jsonl, IT-RETRY-100-集中-なし-S03/time.jsonl | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 |
| A08 | IT-RETRY-100-集中-なし-S03/http.jsonl, IT-RETRY-100-集中-なし-S03/wire.jsonl, IT-RETRY-100-集中-なし-S03/db.jsonl, IT-RETRY-100-集中-なし-S03/mq.jsonl, IT-RETRY-100-集中-なし-S03/metric.jsonl, IT-RETRY-100-集中-なし-S03/time.jsonl | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 |
| A09 | IT-RETRY-100-集中-なし-S03/http.jsonl, IT-RETRY-100-集中-なし-S03/wire.jsonl, IT-RETRY-100-集中-なし-S03/db.jsonl, IT-RETRY-100-集中-なし-S03/mq.jsonl, IT-RETRY-100-集中-なし-S03/metric.jsonl, IT-RETRY-100-集中-なし-S03/time.jsonl | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-retry-100-集中-なし-s04"></a>
#### IT-RETRY-100-集中-なし-S04 / 1000_分散_なし

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "due_rows": 1000,
  "distribution": "分散",
  "due": "集中=t0、分散=900秒へ等間隔(i*900/N秒)",
  "fault": "なし",
  "normal_workload": "10名/search60/game20/QSB10/NTS10",
  "workers": 2,
  "protected": "別群:物理session削除0102/復号不能各10row"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：専有APIまたはBrokerの所有Unit停止/復帰（なしは注入0）。待機：各対照45分+混在45分、復旧/drain15分上限。未解消は保全し収束0と見なさない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同source正常対照45分と同一45分混在窓。初期5/30/300秒、その後900秒定常を少なくとも2周期実時間で観測。故障ありはt0+60秒停止→+90秒復帰。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 2700,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "comparison_seconds": 2700
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A10 | IT-RETRY-100-集中-なし-S04/http.jsonl, IT-RETRY-100-集中-なし-S04/wire.jsonl, IT-RETRY-100-集中-なし-S04/db.jsonl, IT-RETRY-100-集中-なし-S04/mq.jsonl, IT-RETRY-100-集中-なし-S04/metric.jsonl, IT-RETRY-100-集中-なし-S04/time.jsonl | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 |
| A11 | IT-RETRY-100-集中-なし-S04/http.jsonl, IT-RETRY-100-集中-なし-S04/wire.jsonl, IT-RETRY-100-集中-なし-S04/db.jsonl, IT-RETRY-100-集中-なし-S04/mq.jsonl, IT-RETRY-100-集中-なし-S04/metric.jsonl, IT-RETRY-100-集中-なし-S04/time.jsonl | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 |
| A12 | IT-RETRY-100-集中-なし-S04/http.jsonl, IT-RETRY-100-集中-なし-S04/wire.jsonl, IT-RETRY-100-集中-なし-S04/db.jsonl, IT-RETRY-100-集中-なし-S04/mq.jsonl, IT-RETRY-100-集中-なし-S04/metric.jsonl, IT-RETRY-100-集中-なし-S04/time.jsonl | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-retry-100-集中-なし-s05"></a>
#### IT-RETRY-100-集中-なし-S05 / 1000_集中_API停止復帰

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "due_rows": 1000,
  "distribution": "集中",
  "due": "集中=t0、分散=900秒へ等間隔(i*900/N秒)",
  "fault": "API停止復帰",
  "normal_workload": "10名/search60/game20/QSB10/NTS10",
  "workers": 2,
  "protected": "別群:物理session削除0102/復号不能各10row"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：専有APIまたはBrokerの所有Unit停止/復帰（なしは注入0）。待機：各対照45分+混在45分、復旧/drain15分上限。未解消は保全し収束0と見なさない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同source正常対照45分と同一45分混在窓。初期5/30/300秒、その後900秒定常を少なくとも2周期実時間で観測。故障ありはt0+60秒停止→+90秒復帰。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 2700,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "comparison_seconds": 2700
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A13 | IT-RETRY-100-集中-なし-S05/http.jsonl, IT-RETRY-100-集中-なし-S05/wire.jsonl, IT-RETRY-100-集中-なし-S05/db.jsonl, IT-RETRY-100-集中-なし-S05/mq.jsonl, IT-RETRY-100-集中-なし-S05/metric.jsonl, IT-RETRY-100-集中-なし-S05/time.jsonl | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 |
| A14 | IT-RETRY-100-集中-なし-S05/http.jsonl, IT-RETRY-100-集中-なし-S05/wire.jsonl, IT-RETRY-100-集中-なし-S05/db.jsonl, IT-RETRY-100-集中-なし-S05/mq.jsonl, IT-RETRY-100-集中-なし-S05/metric.jsonl, IT-RETRY-100-集中-なし-S05/time.jsonl | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 |
| A15 | IT-RETRY-100-集中-なし-S05/http.jsonl, IT-RETRY-100-集中-なし-S05/wire.jsonl, IT-RETRY-100-集中-なし-S05/db.jsonl, IT-RETRY-100-集中-なし-S05/mq.jsonl, IT-RETRY-100-集中-なし-S05/metric.jsonl, IT-RETRY-100-集中-なし-S05/time.jsonl | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-retry-100-集中-なし-s06"></a>
#### IT-RETRY-100-集中-なし-S06 / 1000_分散_Broker停止復帰

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "due_rows": 1000,
  "distribution": "分散",
  "due": "集中=t0、分散=900秒へ等間隔(i*900/N秒)",
  "fault": "Broker停止復帰",
  "normal_workload": "10名/search60/game20/QSB10/NTS10",
  "workers": 2,
  "protected": "別群:物理session削除0102/復号不能各10row"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：専有APIまたはBrokerの所有Unit停止/復帰（なしは注入0）。待機：各対照45分+混在45分、復旧/drain15分上限。未解消は保全し収束0と見なさない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同source正常対照45分と同一45分混在窓。初期5/30/300秒、その後900秒定常を少なくとも2周期実時間で観測。故障ありはt0+60秒停止→+90秒復帰。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 2700,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "comparison_seconds": 2700
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A16 | IT-RETRY-100-集中-なし-S06/http.jsonl, IT-RETRY-100-集中-なし-S06/wire.jsonl, IT-RETRY-100-集中-なし-S06/db.jsonl, IT-RETRY-100-集中-なし-S06/mq.jsonl, IT-RETRY-100-集中-なし-S06/metric.jsonl, IT-RETRY-100-集中-なし-S06/time.jsonl | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 |
| A17 | IT-RETRY-100-集中-なし-S06/http.jsonl, IT-RETRY-100-集中-なし-S06/wire.jsonl, IT-RETRY-100-集中-なし-S06/db.jsonl, IT-RETRY-100-集中-なし-S06/mq.jsonl, IT-RETRY-100-集中-なし-S06/metric.jsonl, IT-RETRY-100-集中-なし-S06/time.jsonl | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 |
| A18 | IT-RETRY-100-集中-なし-S06/http.jsonl, IT-RETRY-100-集中-なし-S06/wire.jsonl, IT-RETRY-100-集中-なし-S06/db.jsonl, IT-RETRY-100-集中-なし-S06/mq.jsonl, IT-RETRY-100-集中-なし-S06/metric.jsonl, IT-RETRY-100-集中-なし-S06/time.jsonl | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-retry-100-集中-なし-s07"></a>
#### IT-RETRY-100-集中-なし-S07 / 10000_集中_なし

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "due_rows": 10000,
  "distribution": "集中",
  "due": "集中=t0、分散=900秒へ等間隔(i*900/N秒)",
  "fault": "なし",
  "normal_workload": "10名/search60/game20/QSB10/NTS10",
  "workers": 2,
  "protected": "別群:物理session削除0102/復号不能各10row"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：専有APIまたはBrokerの所有Unit停止/復帰（なしは注入0）。待機：各対照45分+混在45分、復旧/drain15分上限。未解消は保全し収束0と見なさない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同source正常対照45分と同一45分混在窓。初期5/30/300秒、その後900秒定常を少なくとも2周期実時間で観測。故障ありはt0+60秒停止→+90秒復帰。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 2700,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "comparison_seconds": 2700
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A19 | IT-RETRY-100-集中-なし-S07/http.jsonl, IT-RETRY-100-集中-なし-S07/wire.jsonl, IT-RETRY-100-集中-なし-S07/db.jsonl, IT-RETRY-100-集中-なし-S07/mq.jsonl, IT-RETRY-100-集中-なし-S07/metric.jsonl, IT-RETRY-100-集中-なし-S07/time.jsonl | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 |
| A20 | IT-RETRY-100-集中-なし-S07/http.jsonl, IT-RETRY-100-集中-なし-S07/wire.jsonl, IT-RETRY-100-集中-なし-S07/db.jsonl, IT-RETRY-100-集中-なし-S07/mq.jsonl, IT-RETRY-100-集中-なし-S07/metric.jsonl, IT-RETRY-100-集中-なし-S07/time.jsonl | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 |
| A21 | IT-RETRY-100-集中-なし-S07/http.jsonl, IT-RETRY-100-集中-なし-S07/wire.jsonl, IT-RETRY-100-集中-なし-S07/db.jsonl, IT-RETRY-100-集中-なし-S07/mq.jsonl, IT-RETRY-100-集中-なし-S07/metric.jsonl, IT-RETRY-100-集中-なし-S07/time.jsonl | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-retry-100-集中-なし-s08"></a>
#### IT-RETRY-100-集中-なし-S08 / 10000_分散_API停止復帰

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "due_rows": 10000,
  "distribution": "分散",
  "due": "集中=t0、分散=900秒へ等間隔(i*900/N秒)",
  "fault": "API停止復帰",
  "normal_workload": "10名/search60/game20/QSB10/NTS10",
  "workers": 2,
  "protected": "別群:物理session削除0102/復号不能各10row"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：専有APIまたはBrokerの所有Unit停止/復帰（なしは注入0）。待機：各対照45分+混在45分、復旧/drain15分上限。未解消は保全し収束0と見なさない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同source正常対照45分と同一45分混在窓。初期5/30/300秒、その後900秒定常を少なくとも2周期実時間で観測。故障ありはt0+60秒停止→+90秒復帰。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 2700,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "comparison_seconds": 2700
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A22 | IT-RETRY-100-集中-なし-S08/http.jsonl, IT-RETRY-100-集中-なし-S08/wire.jsonl, IT-RETRY-100-集中-なし-S08/db.jsonl, IT-RETRY-100-集中-なし-S08/mq.jsonl, IT-RETRY-100-集中-なし-S08/metric.jsonl, IT-RETRY-100-集中-なし-S08/time.jsonl | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 |
| A23 | IT-RETRY-100-集中-なし-S08/http.jsonl, IT-RETRY-100-集中-なし-S08/wire.jsonl, IT-RETRY-100-集中-なし-S08/db.jsonl, IT-RETRY-100-集中-なし-S08/mq.jsonl, IT-RETRY-100-集中-なし-S08/metric.jsonl, IT-RETRY-100-集中-なし-S08/time.jsonl | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 |
| A24 | IT-RETRY-100-集中-なし-S08/http.jsonl, IT-RETRY-100-集中-なし-S08/wire.jsonl, IT-RETRY-100-集中-なし-S08/db.jsonl, IT-RETRY-100-集中-なし-S08/mq.jsonl, IT-RETRY-100-集中-なし-S08/metric.jsonl, IT-RETRY-100-集中-なし-S08/time.jsonl | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-retry-100-集中-なし-s09"></a>
#### IT-RETRY-100-集中-なし-S09 / 10000_集中_Broker停止復帰

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "due_rows": 10000,
  "distribution": "集中",
  "due": "集中=t0、分散=900秒へ等間隔(i*900/N秒)",
  "fault": "Broker停止復帰",
  "normal_workload": "10名/search60/game20/QSB10/NTS10",
  "workers": 2,
  "protected": "別群:物理session削除0102/復号不能各10row"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：専有APIまたはBrokerの所有Unit停止/復帰（なしは注入0）。待機：各対照45分+混在45分、復旧/drain15分上限。未解消は保全し収束0と見なさない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同source正常対照45分と同一45分混在窓。初期5/30/300秒、その後900秒定常を少なくとも2周期実時間で観測。故障ありはt0+60秒停止→+90秒復帰。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 2700,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "comparison_seconds": 2700
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A25 | IT-RETRY-100-集中-なし-S09/http.jsonl, IT-RETRY-100-集中-なし-S09/wire.jsonl, IT-RETRY-100-集中-なし-S09/db.jsonl, IT-RETRY-100-集中-なし-S09/mq.jsonl, IT-RETRY-100-集中-なし-S09/metric.jsonl, IT-RETRY-100-集中-なし-S09/time.jsonl | 再失効同lease duplicate dispatch0。lease takeoverの旧inflight送信はattemptで区別しlogical失効/監査二重確定0。 |
| A26 | IT-RETRY-100-集中-なし-S09/http.jsonl, IT-RETRY-100-集中-なし-S09/wire.jsonl, IT-RETRY-100-集中-なし-S09/db.jsonl, IT-RETRY-100-集中-なし-S09/mq.jsonl, IT-RETRY-100-集中-なし-S09/metric.jsonl, IT-RETRY-100-集中-なし-S09/time.jsonl | 初期5/30/300と900秒定常の実due/試行時刻を別表、仮想Clockで代用0。protected20rowは欠落扱い/無条件drain削除0。 |
| A27 | IT-RETRY-100-集中-なし-S09/http.jsonl, IT-RETRY-100-集中-なし-S09/wire.jsonl, IT-RETRY-100-集中-なし-S09/db.jsonl, IT-RETRY-100-集中-なし-S09/mq.jsonl, IT-RETRY-100-集中-なし-S09/metric.jsonl, IT-RETRY-100-集中-なし-S09/time.jsonl | 対照/混在のroute別p95、error/timeout率、CPU/DBpool/lock/WAL/journal/oldest/depth/drainを同じ45分窓で比較。設計SLA維持、独自許容劣化%0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-retry-100-集中-api停止復帰"></a>
## IT-RETRY-100-集中-API停止復帰（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-100-集中-broker停止復帰"></a>
## IT-RETRY-100-集中-Broker停止復帰（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-100-分散-なし"></a>
## IT-RETRY-100-分散-なし（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-100-分散-api停止復帰"></a>
## IT-RETRY-100-分散-API停止復帰（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-100-分散-broker停止復帰"></a>
## IT-RETRY-100-分散-Broker停止復帰（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-1000-集中-なし"></a>
## IT-RETRY-1000-集中-なし（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-1000-集中-api停止復帰"></a>
## IT-RETRY-1000-集中-API停止復帰（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-1000-集中-broker停止復帰"></a>
## IT-RETRY-1000-集中-Broker停止復帰（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-1000-分散-なし"></a>
## IT-RETRY-1000-分散-なし（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-1000-分散-api停止復帰"></a>
## IT-RETRY-1000-分散-API停止復帰（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-1000-分散-broker停止復帰"></a>
## IT-RETRY-1000-分散-Broker停止復帰（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-10000-集中-なし"></a>
## IT-RETRY-10000-集中-なし（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-10000-集中-api停止復帰"></a>
## IT-RETRY-10000-集中-API停止復帰（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-10000-集中-broker停止復帰"></a>
## IT-RETRY-10000-集中-Broker停止復帰（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-10000-分散-なし"></a>
## IT-RETRY-10000-分散-なし（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-10000-分散-api停止復帰"></a>
## IT-RETRY-10000-分散-API停止復帰（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-retry-10000-分散-broker停止復帰"></a>
## IT-RETRY-10000-分散-Broker停止復帰（統合済・実行対象外）

継続先：[IT-RETRY-100-集中-なし](527_性能・資源・Logout混在.md#it-retry-100-集中-なし)。9pairwise SCへ集約。全size×fault/両分布を保持、除外三因子組は未実施・未充足相互作用として保持。

<a id="it-perf-030"></a>
## IT-PERF-030 段階負荷1→5→10と短時間集中

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

同時10名条件に至る待ち/飽和点を明示し、旧定常10だけでは見えないbackpressureを観測。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SYNC |
| 確認契約 | 段階負荷1→5→10と短時間集中 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 100 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（1件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-030"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 10名窓の対象route p95&lt;=2.5s、MQwait各&lt;=2.0s。concurrency実数&lt;=10、取り違え0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 全窓のpool/thread/FD/queue/lock推移を比較。1→5/5→10で根拠ない劣化率基準を作らず実数を残す。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | issued/terminal/outstanding一致、burst同期10超0。2秒timeoutを後の完了で救済0、全失敗率を併記。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

同時10名条件に至る待ち/飽和点を明示し、旧定常10だけでは見えないbackpressureを観測。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-030`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-030-s01"></a>
#### IT-PERF-030-S01 / ramp

種類：境界、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "concurrency_steps": [
    1,
    5,
    10
  ],
  "seconds_each": 600,
  "arrival": "closed-loop think0 / each completion next",
  "mix": "Scenario検索70%,Game20%,Log10%（ADMINだけ）"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 各段階300秒warmup後600秒測定。各clientの100要求周期は70/20/10順の固定seed shuffle、失敗も1試行。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "overrides": {
    "concurrency_steps": [
      1,
      5,
      10
    ],
    "seconds_each": 600,
    "arrival": "closed-loop think0 / each completion next",
    "mix": "Scenario検索70%,Game20%,Log10%（ADMINだけ）"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-030-S01/http.jsonl, IT-PERF-030-S01/wire.jsonl, IT-PERF-030-S01/db.jsonl, IT-PERF-030-S01/mq.jsonl, IT-PERF-030-S01/metric.jsonl, IT-PERF-030-S01/time.jsonl | 10名窓の対象route p95&lt;=2.5s、MQwait各&lt;=2.0s。concurrency実数&lt;=10、取り違え0。 |
| A02 | IT-PERF-030-S01/http.jsonl, IT-PERF-030-S01/wire.jsonl, IT-PERF-030-S01/db.jsonl, IT-PERF-030-S01/mq.jsonl, IT-PERF-030-S01/metric.jsonl, IT-PERF-030-S01/time.jsonl | 全窓のpool/thread/FD/queue/lock推移を比較。1→5/5→10で根拠ない劣化率基準を作らず実数を残す。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-030-s02"></a>
#### IT-PERF-030-S02 / burst10

種類：競合、反復：100、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "clients": 10,
  "cycles": 60,
  "period_seconds": 10,
  "inflight_per_client": 1
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 毎10秒境界に10client同時に1要求を発行、未完があれば重ねずmissed slotとして記録。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "overrides": {
    "clients": 10,
    "cycles": 60,
    "period_seconds": 10,
    "inflight_per_client": 1
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A03 | IT-PERF-030-S02/http.jsonl, IT-PERF-030-S02/wire.jsonl, IT-PERF-030-S02/db.jsonl, IT-PERF-030-S02/mq.jsonl, IT-PERF-030-S02/metric.jsonl, IT-PERF-030-S02/time.jsonl | issued/terminal/outstanding一致、burst同期10超0。2秒timeoutを後の完了で救済0、全失敗率を併記。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-031"></a>
## IT-PERF-031 同期照会と質問worker混在

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧通常負荷に非同期acceptanceとcompletionの計測/質量収支がない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SYNC |
| 確認契約 | 同期照会と質問worker混在 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 100 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（1件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-031"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 同期SLAをroute別全試行で判定、QSB受付応答は対応Outbox SENT後のみ。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | drain後Question1/job1/通知1/answer&lt;=1を各tokenで照合。provider業務ERRORは合意fixtureの期待codeだけ、欠落/二重completion0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧通常負荷に非同期acceptanceとcompletionの計測/質量収支がない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-031`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-031-s01"></a>
#### IT-PERF-031-S01 / sync_async

種類：競合、反復：100、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "clients": 10,
  "mix_100slots": {
    "search": 60,
    "game": 20,
    "QSB": 10,
    "NTS": 10
  },
  "arrival": "closed loop think0",
  "provider": "設計対応の決定的隔離provider、Q0..の固定回答表"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 300秒warmup→1800秒測定。USERだけQSB、ADMINはsearch/game/NTSで同じ比率へ固定配分、accepted QSB全IDを追う。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "overrides": {
    "clients": 10,
    "mix_100slots": {
      "search": 60,
      "game": 20,
      "QSB": 10,
      "NTS": 10
    },
    "arrival": "closed loop think0",
    "provider": "設計対応の決定的隔離provider、Q0..の固定回答表"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-031-S01/http.jsonl, IT-PERF-031-S01/wire.jsonl, IT-PERF-031-S01/db.jsonl, IT-PERF-031-S01/mq.jsonl, IT-PERF-031-S01/metric.jsonl, IT-PERF-031-S01/time.jsonl | 同期SLAをroute別全試行で判定、QSB受付応答は対応Outbox SENT後のみ。 |
| A02 | IT-PERF-031-S01/http.jsonl, IT-PERF-031-S01/wire.jsonl, IT-PERF-031-S01/db.jsonl, IT-PERF-031-S01/mq.jsonl, IT-PERF-031-S01/metric.jsonl, IT-PERF-031-S01/time.jsonl | drain後Question1/job1/通知1/answer&lt;=1を各tokenで照合。provider業務ERRORは合意fixtureの期待codeだけ、欠落/二重completion0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-032"></a>
## IT-PERF-032 20media+SCN10000と通常画面混在

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧IT-PERF-002の比率未指定を補い、20streampermitと大容量48MB生成が通常同期へ与える影響を同窓観測。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SYNC |
| 確認契約 | 20media+SCN10000と通常画面混在 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 100 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `7147c428bb9d`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 4. Large-result判定・レイアウト ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-032"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 対象同期routeのp95&lt;=2.5s/MQwait&lt;=2.0s、SCN count10000/size48000000/hash/順序一致。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-FS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | media active&lt;=20/Rangebody&lt;=1048576、FD/permit終端回復。全転送時間と同期SLAを混同0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-FS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧IT-PERF-002の比率未指定を補い、20streampermitと大容量48MB生成が通常同期へ与える影響を同窓観測。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-032`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-032-s01"></a>
#### IT-PERF-032-S01 / mixed

種類：競合、反復：100、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "sync_users": 10,
  "mix": "Scenario検索50/Game30/SCN10000record20",
  "media_clients": 20,
  "media": "Range1MiBを完了後次、同時20維持"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 300秒warmup→1800秒。10同期clientと別20streamclientを独立開始、固有ID/hashで結果追跡。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "overrides": {
    "sync_users": 10,
    "mix": "Scenario検索50/Game30/SCN10000record20",
    "media_clients": 20,
    "media": "Range1MiBを完了後次、同時20維持"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-032-S01/http.jsonl, IT-PERF-032-S01/wire.jsonl, IT-PERF-032-S01/db.jsonl, IT-PERF-032-S01/mq.jsonl, IT-PERF-032-S01/fs.jsonl, IT-PERF-032-S01/metric.jsonl, IT-PERF-032-S01/time.jsonl | 対象同期routeのp95&lt;=2.5s/MQwait&lt;=2.0s、SCN count10000/size48000000/hash/順序一致。 |
| A02 | IT-PERF-032-S01/http.jsonl, IT-PERF-032-S01/wire.jsonl, IT-PERF-032-S01/db.jsonl, IT-PERF-032-S01/mq.jsonl, IT-PERF-032-S01/fs.jsonl, IT-PERF-032-S01/metric.jsonl, IT-PERF-032-S01/time.jsonl | media active&lt;=20/Rangebody&lt;=1048576、FD/permit終端回復。全転送時間と同期SLAを混同0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-033"></a>
## IT-PERF-033 障害復帰後Outbox残件と通常業務継続

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

停止中の失敗率を正常窓から黙って除外せず、復旧直後の集中と収束を区分。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SYNC |
| 確認契約 | 障害復帰後Outbox残件と通常業務継続 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 2 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（1件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-033"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 故障30秒・復帰窓・正常窓を別集計、全発行を残す。復帰窓のSLA例外を勝手に新設0。 | O-HTTP, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | claim&lt;=100/lease10s、同一logical業務1、PENDING/ERROR残件の最古/深さ/drain時間を報告。収束時間SLA未規定は数値記録し上限捏造0。 | O-HTTP, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

停止中の失敗率を正常窓から黙って除外せず、復旧直後の集中と収束を区分。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-033`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-033-s01"></a>
#### IT-PERF-033-S01 / recovery

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "due_outbox": 1000,
  "identities": "unique1000",
  "normal_users": 10,
  "outage_seconds": 30,
  "fault_role": "API senderのbroker connection"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：isolated sender connection cut30sec。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 正常300秒→30秒専用接続遮断→復帰後1800秒、同じ60/20/10/10負荷を継続。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "overrides": {
    "due_outbox": 1000,
    "identities": "unique1000",
    "normal_users": 10,
    "outage_seconds": 30,
    "fault_role": "API senderのbroker connection"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-033-S01/http.jsonl, IT-PERF-033-S01/db.jsonl, IT-PERF-033-S01/mq.jsonl, IT-PERF-033-S01/metric.jsonl, IT-PERF-033-S01/time.jsonl | 故障30秒・復帰窓・正常窓を別集計、全発行を残す。復帰窓のSLA例外を勝手に新設0。 |
| A02 | IT-PERF-033-S01/http.jsonl, IT-PERF-033-S01/db.jsonl, IT-PERF-033-S01/mq.jsonl, IT-PERF-033-S01/metric.jsonl, IT-PERF-033-S01/time.jsonl | claim&lt;=100/lease10s、同一logical業務1、PENDING/ERROR残件の最古/深さ/drain時間を報告。収束時間SLA未規定は数値記録し上限捏造0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-034"></a>
## IT-PERF-034 2時間継続と解放後資源回復

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧30分平均観測だけでは生存中lease/接続/FD蓄積が不明。2時間は試験入力で新運用SLAではない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SYNC |
| 確認契約 | 2時間継続と解放後資源回復 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 2 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（1件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-034"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 設計MemoryMax/DBpool/stream上限内、所有connection/transaction/lock/FD/permitはdrain後before集合へ戻る（既定常駐分はmanifest区別）。 | O-HTTP, O-DB, O-MQ, O-OS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 業務ID質量収支一致、欠落/重複0。heap/RSS傾きは報告のみ、SSにない%/MB閾値でNG0。 | O-HTTP, O-DB, O-MQ, O-OS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧30分平均観測だけでは生存中lease/接続/FD蓄積が不明。2時間は試験入力で新運用SLAではない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-034`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-034-s01"></a>
#### IT-PERF-034-S01 / soak

種類：正常、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "users": 10,
  "duration_seconds": 7200,
  "mix": "search60/game20/QSB10/NTS10",
  "arrival": "closed loop 1inflight"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 300秒warmup→7200秒測定→load停止後120秒drain、同じ計測を継続。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "overrides": {
    "users": 10,
    "duration_seconds": 7200,
    "mix": "search60/game20/QSB10/NTS10",
    "arrival": "closed loop 1inflight"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-034-S01/http.jsonl, IT-PERF-034-S01/db.jsonl, IT-PERF-034-S01/mq.jsonl, IT-PERF-034-S01/os.jsonl, IT-PERF-034-S01/metric.jsonl, IT-PERF-034-S01/time.jsonl | 設計MemoryMax/DBpool/stream上限内、所有connection/transaction/lock/FD/permitはdrain後before集合へ戻る（既定常駐分はmanifest区別）。 |
| A02 | IT-PERF-034-S01/http.jsonl, IT-PERF-034-S01/db.jsonl, IT-PERF-034-S01/mq.jsonl, IT-PERF-034-S01/os.jsonl, IT-PERF-034-S01/metric.jsonl, IT-PERF-034-S01/time.jsonl | 業務ID質量収支一致、欠落/重複0。heap/RSS傾きは報告のみ、SSにない%/MB閾値でNG0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-035"></a>
## IT-PERF-035 計画maintenance排他とbackup/cleanup資源

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

通常業務とbackup並行という根拠のない負荷を作らず、設計のpublic停止/排他下で資源予算と再開後SLAを確認。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-OPS |
| 確認契約 | 計画maintenance排他とbackup/cleanup資源 |
| 必要環境 | E-OPS |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 2 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `7147c428bb9d`
- [342_Caddy・systemd・PostgreSQL・Java設定設計.md](<../../300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md>) Caddy・systemd・PostgreSQL・Java設定設計 > 5. Java/JVM・Spring process > 5.1 Resource ／ 固定承認本文 ／ commit `7147c428bb9d`
- [341_朝batch・backup・削除・再実行設計.md](<../../300_SS/340_batch・基盤/341_朝batch・backup・削除・再実行設計.md>) 朝batch・backup・削除・再実行設計 ／ ['SSC278'] ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-035"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | backup/cleanup中public業務受付成功0。並列Wantsで子を起動0、親1800秒budgetを延長0。 | O-HTTP, O-OS, O-DB, O-MQ, O-FS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 16GB/256GB各配分とMemoryMax内、backup/cleanupのdisk/WAL/journal/IOを別窓記録。再開後10名同期SLAを再判定。 | O-HTTP, O-OS, O-DB, O-MQ, O-FS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, DEP-OPS-HOLD を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

通常業務とbackup並行という根拠のない負荷を作らず、設計のpublic停止/排他下で資源予算と再開後SLAを確認。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-035`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-035-s01"></a>
#### IT-PERF-035-S01 / maintenance

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "public_clients": 10,
  "phase": "Morning backup→cleanup→再起動",
  "backup": "既定全3schema+config/credential archive"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 正常300秒計測→所有Morning開始→public停止からbackup/cleanup別窓採取→再開後300秒warmup/1800秒測定。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可",
  "overrides": {
    "public_clients": 10,
    "phase": "Morning backup→cleanup→再起動",
    "backup": "既定全3schema+config/credential archive"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-035-S01/http.jsonl, IT-PERF-035-S01/os.jsonl, IT-PERF-035-S01/db.jsonl, IT-PERF-035-S01/mq.jsonl, IT-PERF-035-S01/fs.jsonl, IT-PERF-035-S01/metric.jsonl, IT-PERF-035-S01/time.jsonl | backup/cleanup中public業務受付成功0。並列Wantsで子を起動0、親1800秒budgetを延長0。 |
| A02 | IT-PERF-035-S01/http.jsonl, IT-PERF-035-S01/os.jsonl, IT-PERF-035-S01/db.jsonl, IT-PERF-035-S01/mq.jsonl, IT-PERF-035-S01/fs.jsonl, IT-PERF-035-S01/metric.jsonl, IT-PERF-035-S01/time.jsonl | 16GB/256GB各配分とMemoryMax内、backup/cleanupのdisk/WAL/journal/IOを別窓記録。再開後10名同期SLAを再判定。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-036"></a>
## IT-PERF-036 Scenario selective SQL p95 1.5秒

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧IT-PERF-001のE2E2.5秒だけではSS332のSQL単独1.5秒条件を判定できない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SYNC |
| 確認契約 | Scenario selective SQL p95 1.5秒 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 2 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) SQL・transaction・lock・削除設計 > 13. Query plan・性能確認 ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（1件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-036"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | selective query全試行elapsedのceil(.95*N)番&lt;=1.5秒、515の事前独立manifest N(1..100)件/順序とcount/list完全一致。E2E&lt;=2.5秒とは別assertion。 | O-DB, O-WIRE, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | planの不要seq scanなしをpredicate/index/cardinalityと併せレビュー。query名だけから使用indexを推測0、trace対象関数から期待IDを計算0。 | O-DB, O-WIRE, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, ISS-SELECTIVITY を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧IT-PERF-001のE2E2.5秒だけではSS332のSQL単独1.5秒条件を判定できない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-036`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-036-s01"></a>
#### IT-PERF-036-S01 / query_plan

種類：正常、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entries": 99661,
  "page_size": 100,
  "filters": "515のoffline import manifest selectorで事前固定した6filter単独/AND、match集合N=1..100・非match99661-N。生成未完はPREP-DATAで開始不可。",
  "load": "10同時 searchのみ closed-loop"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 300秒warmup→1800秒。Query ID/parameter/plan/DB query begin-endを全試行採取、E2Eも併記。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "resource_manifest": "SS342/343:16GB/256GB, Web1536M/API2048M/Batch1536M/Artemis2048M, PG pool API8/Web2; effective hash固定",
  "users": "P-BASE-v2 USER8+ADMIN2、10固有session、各1inflight",
  "data": "99,661 Scenario entries、Log100/page、新規一覧50/page、SCN10,000record、Asset59,627file/19,240,707,190byteは正本manifest照合",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "metrics": [
    "issued/accepted/completed/unique/error/timeout counts",
    "各route elapsedのp50/p95/p99/max、throughput/sec",
    "MQ wait/queue oldest/depth/drain",
    "CPU/RSS/heap/direct/metaspace/GC/thread/FD",
    "DB pool/lock/wait/WAL",
    "journal/paging/disk free/IOPS/read-write latency"
  ],
  "sampling": "HTTP/MQは全requestイベント、OS/DB/MQは1秒sample。計測実装のoverheadは同source無負荷対照で記録、SLA許容差の追加0。",
  "judgement": "SS354 STANDARD同時10の対象route E2E p95<=2.5s/MQ待ち<=2.0s/取り違え0。timeout/errorを分母から除外せず失敗個別保存。SSに規定のないthroughput floor/error許容率/劣化%/GC閾値を新設しない。",
  "mass_balance": "issued=terminal+outstanding; accepted business ID集合=committed unique ID集合（drain後）; duplicate logical update0; nonaccepted updates0",
  "stop": "仕様資源上限/所有喪失/ディスク安全停止条件/証拠欠落/他job出現で新規load停止。inflightとqueueを保全し、未知commitを再発行しない。",
  "drain": "新規発行停止後120秒観測、未完残件を0へ補完せず一覧保全。指定復旧試験のdrainは別有限窓。",
  "entry": "T-LOAD-v2（未実装）から実browser/HTTP/既存MQ入口、ツールだけmockは不可"
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-036-S01/db.jsonl, IT-PERF-036-S01/wire.jsonl, IT-PERF-036-S01/metric.jsonl, IT-PERF-036-S01/time.jsonl | selective query全試行elapsedのceil(.95*N)番&lt;=1.5秒、515の事前独立manifest N(1..100)件/順序とcount/list完全一致。E2E&lt;=2.5秒とは別assertion。 |
| A02 | IT-PERF-036-S01/db.jsonl, IT-PERF-036-S01/wire.jsonl, IT-PERF-036-S01/metric.jsonl, IT-PERF-036-S01/time.jsonl | planの不要seq scanなしをpredicate/index/cardinalityと併せレビュー。query名だけから使用indexを推測0、trace対象関数から期待IDを計算0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-040"></a>
## IT-PERF-040 実PBKDF2 Login照合と10名混在・security review目標

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧PERFは一般p95中心。password判定doubleを使わない実暗号のCPU/lock競合と0.5～1.0秒目標のreview条件が欠落。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | 実PBKDF2 Login照合と10名混在・security review目標 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 100 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) 認証・認可・session・CSRF実装設計 > 4. Password > 4.1 保存・照合 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) 認証・認可・session・CSRF実装設計 > 4. Password > 4.1 保存・照合 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) 認証・認可・session・CSRF実装設計 > SSC267 Login単体試験の独立境界（2026-10-12） ／ ['SSC267'] ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-040"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | PBKDF2-HMAC-SHA256/salt16/310000/256bit/prefix pbkdf2-v1。実照合p95と0.5～1.0秒目標の内外を報告、外れた場合security review依頼。目標を独自の即NG閾値へ変換0、work factor/同ID意味を変更0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 通常同時10対象E2E p95&lt;=2.5s/MQwait&lt;=2.0s。失敗/timeout全分母、Login時のUser→IP lock/API1500ms/500msは維持。2session上限/最古REPLACED/監査原子、User跨ぎcontext取り違え0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | CPU/GC/thread/FD/DBpool/lock/WAL/queue/journalを同窓採取。停止後active接続/lock/permitはbeforeへ、未確定Loginを成功sessionとして補完0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧PERFは一般p95中心。password判定doubleを使わない実暗号のCPU/lock競合と0.5～1.0秒目標のreview条件が欠落。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-040`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-040-s01"></a>
#### IT-PERF-040-S01 / real_crypto10

種類：競合、反復：100、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "users": "USER8+ADMIN2の10固有user",
  "concurrency": 10,
  "inflight_each": 1,
  "mix100": "Login20/Scenario検索60/Question10/通知10",
  "password": "試験password/独立JCA hash-v1",
  "warmup_sec": 300,
  "measure_sec": 1800,
  "repeats": 2
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実Java25/Caddy/Web/API/DB/MQで閉ループ。Login完了後そのuser最新cookieを使用し他userへ共有しない。crypto開始/終了とE2E/DBlock/poolを別採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "final release immutable manifest",
  "JDK": "25",
  "CPU": "本番相当型番/core/周波数固定、計測器overhead対照記録",
  "arrival": "closed loop、各固有user1inflight、think0",
  "mix100": {
    "Login": 20,
    "ScenarioSearch": 60,
    "QSB": 10,
    "NTS": 10
  },
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全request/crypto span、OS/DB/MQ1秒",
  "p95": "route全試行sort ceil(.95*N)、失敗/censored別記し分母から除外0",
  "normal_comparison": "同一source/fixture/password/hash/CPUの通常10名窓1800秒",
  "failure_overlay": "別caseの故障窓を混ぜて目標を救済しない",
  "mass_balance": "issued=terminal+outstanding、成功Loginに対応auth_sessionを全Messageで照合",
  "stop": "資源上限/所有変化/collector欠落で新規負荷停止、inflight保全",
  "recovery": "120秒drain、未確定ID/FD/lock/queueを一覧し0へ補完しない"
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-040-S01/http.jsonl, IT-PERF-040-S01/wire.jsonl, IT-PERF-040-S01/db.jsonl, IT-PERF-040-S01/mq.jsonl, IT-PERF-040-S01/metric.jsonl, IT-PERF-040-S01/time.jsonl | PBKDF2-HMAC-SHA256/salt16/310000/256bit/prefix pbkdf2-v1。実照合p95と0.5～1.0秒目標の内外を報告、外れた場合security review依頼。目標を独自の即NG閾値へ変換0、work factor/同ID意味を変更0。 |
| A02 | IT-PERF-040-S01/http.jsonl, IT-PERF-040-S01/wire.jsonl, IT-PERF-040-S01/db.jsonl, IT-PERF-040-S01/mq.jsonl, IT-PERF-040-S01/metric.jsonl, IT-PERF-040-S01/time.jsonl | 通常同時10対象E2E p95&lt;=2.5s/MQwait&lt;=2.0s。失敗/timeout全分母、Login時のUser→IP lock/API1500ms/500msは維持。2session上限/最古REPLACED/監査原子、User跨ぎcontext取り違え0。 |
| A03 | IT-PERF-040-S01/http.jsonl, IT-PERF-040-S01/wire.jsonl, IT-PERF-040-S01/db.jsonl, IT-PERF-040-S01/mq.jsonl, IT-PERF-040-S01/metric.jsonl, IT-PERF-040-S01/time.jsonl | CPU/GC/thread/FD/DBpool/lock/WAL/queue/journalを同窓採取。停止後active接続/lock/permitはbeforeへ、未確定Loginを成功sessionとして補完0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-041"></a>
## IT-PERF-041 同期wait admission上限とtimeout後permit回収

仕様：**PENDING_DECISION** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

通常10名ではdefault12と上限20の入場制御、timeout/送信失敗後のpermit漏れを観測できない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SYNC |
| 確認契約 | 同期wait admission上限とtimeout後permit回収 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 2 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [343_設定file・directory・初期data・migration・切戻し設計.md](<../../300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md>) 設定file・directory・初期data・migration・切戻し設計 > 5. 主要設定key > 5.1 Common・Web ／ 固定承認本文 ／ commit `7147c428bb9d`
- [342_Caddy・systemd・PostgreSQL・Java設定設計.md](<../../300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md>) Caddy・systemd・PostgreSQL・Java設定設計 > 5. Java/JVM・Spring process > 5.2 Spring主要値 ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（2件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-041"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 既定admission実効countと設定12/max20を採取、上限を越えるMQsend0/registry二重0、拒否後DB業務更新0。13番のauto伸長/待機/HTTPcodeはSSに一義でなくISS-WAIT-ADMISSIONの該当条件だけ判定待ち。 | O-HTTP, O-WIRE, O-MQ, O-DB, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 2秒timeoutを延長0、late応答は元registryだけ/取違え0。各cycle終端後permit/registry/FD/DBconnection beforeへ、送信失敗も一度回収。通常10名再開SLA維持。 | O-HTTP, O-WIRE, O-MQ, O-DB, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | active wait&gt;20を許容0、未admittedsend0、21番拒否/HTTP期待はISS-WAIT-ADMISSION。20上限を増やして合格0。 | O-HTTP, O-WIRE, O-MQ, O-DB, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 全terminal後20permit回収、100cycle後通常10名SLA/pool/FDの残留0。 | O-HTTP, O-WIRE, O-MQ, O-DB, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：ISS-WAIT-ADMISSION。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

通常10名ではdefault12と上限20の入場制御、timeout/送信失敗後のpermit漏れを観測できない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-041`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-041-s01"></a>
#### IT-PERF-041-S01 / initial12

種類：境界、反復：2、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "waiters": 12,
  "additional": 1,
  "barrier": "12要求のregistry登録後replyを1.9sまで保持",
  "cycles": 100
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 12同時を確認→13番入場を試行→barrier解放、全terminal後同じ通常10名負荷へ戻す。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "最終release/config/schema/protocol/master hashをrun manifestへfreeze",
  "hardware": "16GB/256GB、本番CPU型番/core/周波数/OS/JDKを固定",
  "clients": "USER8+ADMIN2各1inflight/think0 closed loop",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全HTTP/MQ/DB span、OS/PG/JVM/MQ/FD1秒。採取overhead無負荷対照を別保存",
  "statistics": "route/windowごとの全試行raw、p95=昇順ceil(.95*N)番、失敗/timeout/censoredを別件数として全issued分母に保持し成功選別0",
  "sla": "通常10名同期E2Ep95<=2.5s/MQwait各<=2.0s/取り違え0、未規定throughput/error許容率/劣化%を新設0",
  "stop": "所有/source/env変更/証拠欠落/仕様資源上限/安全停止境界で新規発行停止、inflightと未知commitを保全",
  "drain": "120秒の観測終了で残件を0補完0、各ID状態/最古/解消見通しを保全し承認復旧へ",
  "mass_balance": "issued=terminal+outstanding、accepted ID集合=確定unique+明示残件、二重業務更新0/拒否要求の更新0",
  "overrides": {
    "waiters": 12,
    "additional": 1,
    "barrier": "12要求のregistry登録後replyを1.9sまで保持",
    "cycles": 100
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-041-S01/http.jsonl, IT-PERF-041-S01/wire.jsonl, IT-PERF-041-S01/mq.jsonl, IT-PERF-041-S01/db.jsonl, IT-PERF-041-S01/metric.jsonl, IT-PERF-041-S01/time.jsonl | 既定admission実効countと設定12/max20を採取、上限を越えるMQsend0/registry二重0、拒否後DB業務更新0。13番のauto伸長/待機/HTTPcodeはSSに一義でなくISS-WAIT-ADMISSIONの該当条件だけ判定待ち。 |
| A02 | IT-PERF-041-S01/http.jsonl, IT-PERF-041-S01/wire.jsonl, IT-PERF-041-S01/mq.jsonl, IT-PERF-041-S01/db.jsonl, IT-PERF-041-S01/metric.jsonl, IT-PERF-041-S01/time.jsonl | 2秒timeoutを延長0、late応答は元registryだけ/取違え0。各cycle終端後permit/registry/FD/DBconnection beforeへ、送信失敗も一度回収。通常10名再開SLA維持。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-041-s02"></a>
#### IT-PERF-041-S02 / max20

種類：境界、反復：2、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "configured_max": 20,
  "clients": 21,
  "cycles": 100
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 承認済み実効admission20profileを準備し20inflight保持→21番、timeout/sendfailure別窓を実測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "最終release/config/schema/protocol/master hashをrun manifestへfreeze",
  "hardware": "16GB/256GB、本番CPU型番/core/周波数/OS/JDKを固定",
  "clients": "USER8+ADMIN2各1inflight/think0 closed loop",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全HTTP/MQ/DB span、OS/PG/JVM/MQ/FD1秒。採取overhead無負荷対照を別保存",
  "statistics": "route/windowごとの全試行raw、p95=昇順ceil(.95*N)番、失敗/timeout/censoredを別件数として全issued分母に保持し成功選別0",
  "sla": "通常10名同期E2Ep95<=2.5s/MQwait各<=2.0s/取り違え0、未規定throughput/error許容率/劣化%を新設0",
  "stop": "所有/source/env変更/証拠欠落/仕様資源上限/安全停止境界で新規発行停止、inflightと未知commitを保全",
  "drain": "120秒の観測終了で残件を0補完0、各ID状態/最古/解消見通しを保全し承認復旧へ",
  "mass_balance": "issued=terminal+outstanding、accepted ID集合=確定unique+明示残件、二重業務更新0/拒否要求の更新0",
  "overrides": {
    "configured_max": 20,
    "clients": 21,
    "cycles": 100
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A03 | IT-PERF-041-S02/http.jsonl, IT-PERF-041-S02/wire.jsonl, IT-PERF-041-S02/mq.jsonl, IT-PERF-041-S02/db.jsonl, IT-PERF-041-S02/metric.jsonl, IT-PERF-041-S02/time.jsonl | active wait&gt;20を許容0、未admittedsend0、21番拒否/HTTP期待はISS-WAIT-ADMISSION。20上限を増やして合格0。 |
| A04 | IT-PERF-041-S02/http.jsonl, IT-PERF-041-S02/wire.jsonl, IT-PERF-041-S02/mq.jsonl, IT-PERF-041-S02/db.jsonl, IT-PERF-041-S02/metric.jsonl, IT-PERF-041-S02/time.jsonl | 全terminal後20permit回収、100cycle後通常10名SLA/pool/FDの残留0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-042"></a>
## IT-PERF-042 非選択検索・最大page混在のSQLbudget

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

selective1.5秒と非選択query/HTTP2.5秒の責務を分け、worst件数・page端でpool競合を測定。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SYNC |
| 確認契約 | 非選択検索・最大page混在のSQLbudget |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 100 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `7147c428bb9d`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) SQL・transaction・lock・削除設計 > 13. Query plan・性能確認 ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（2件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-042"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | entry99661のpage1は100/page997は61/超過998はAPI最終補正997で61、count99661。Log100/通知50を上限に順序/件数は独立manifest一致、SQL1snapshot/N+1なし。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | APIstatement1500ms/lock500msを実効値で維持、通常同期E2Ep95&lt;=2.5s/MQwait&lt;=2.0s。selective専用p95&lt;=1.5sを非選択へ新要求として適用0、timeoutを成功sample除外0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | plan/IO/temp/WAL/CPU/pool8+2と全queuebacklogを同窓保存、拒否/失敗で業務更新0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

selective1.5秒と非選択query/HTTP2.5秒の責務を分け、worst件数・page端でpool競合を測定。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-042`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-042-s01"></a>
#### IT-PERF-042-S01 / worst_pages

種類：競合、反復：100、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entries": 99661,
  "search": "全filter未指定/1文字高頻度はmanifestで集合freeze",
  "pages": [
    1,
    997,
    998
  ],
  "page_size": 100,
  "Log": "10001件/100page",
  "NTS": "1001件/50page",
  "users": "8USER2ADMIN",
  "mix100": "search40/log30/NTS30"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同10名/300秒warmup→1800秒×2、page集合とDB count/list同snapshotを個別採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "最終release/config/schema/protocol/master hashをrun manifestへfreeze",
  "hardware": "16GB/256GB、本番CPU型番/core/周波数/OS/JDKを固定",
  "clients": "USER8+ADMIN2各1inflight/think0 closed loop",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全HTTP/MQ/DB span、OS/PG/JVM/MQ/FD1秒。採取overhead無負荷対照を別保存",
  "statistics": "route/windowごとの全試行raw、p95=昇順ceil(.95*N)番、失敗/timeout/censoredを別件数として全issued分母に保持し成功選別0",
  "sla": "通常10名同期E2Ep95<=2.5s/MQwait各<=2.0s/取り違え0、未規定throughput/error許容率/劣化%を新設0",
  "stop": "所有/source/env変更/証拠欠落/仕様資源上限/安全停止境界で新規発行停止、inflightと未知commitを保全",
  "drain": "120秒の観測終了で残件を0補完0、各ID状態/最古/解消見通しを保全し承認復旧へ",
  "mass_balance": "issued=terminal+outstanding、accepted ID集合=確定unique+明示残件、二重業務更新0/拒否要求の更新0",
  "overrides": {
    "entries": 99661,
    "search": "全filter未指定/1文字高頻度はmanifestで集合freeze",
    "pages": [
      1,
      997,
      998
    ],
    "page_size": 100,
    "Log": "10001件/100page",
    "NTS": "1001件/50page",
    "users": "8USER2ADMIN",
    "mix100": "search40/log30/NTS30"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-042-S01/http.jsonl, IT-PERF-042-S01/wire.jsonl, IT-PERF-042-S01/db.jsonl, IT-PERF-042-S01/mq.jsonl, IT-PERF-042-S01/metric.jsonl, IT-PERF-042-S01/time.jsonl | entry99661のpage1は100/page997は61/超過998はAPI最終補正997で61、count99661。Log100/通知50を上限に順序/件数は独立manifest一致、SQL1snapshot/N+1なし。 |
| A02 | IT-PERF-042-S01/http.jsonl, IT-PERF-042-S01/wire.jsonl, IT-PERF-042-S01/db.jsonl, IT-PERF-042-S01/mq.jsonl, IT-PERF-042-S01/metric.jsonl, IT-PERF-042-S01/time.jsonl | APIstatement1500ms/lock500msを実効値で維持、通常同期E2Ep95&lt;=2.5s/MQwait&lt;=2.0s。selective専用p95&lt;=1.5sを非選択へ新要求として適用0、timeoutを成功sample除外0。 |
| A03 | IT-PERF-042-S01/http.jsonl, IT-PERF-042-S01/wire.jsonl, IT-PERF-042-S01/db.jsonl, IT-PERF-042-S01/mq.jsonl, IT-PERF-042-S01/metric.jsonl, IT-PERF-042-S01/time.jsonl | plan/IO/temp/WAL/CPU/pool8+2と全queuebacklogを同窓保存、拒否/失敗で業務更新0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-043"></a>
## IT-PERF-043 Inbox/Outbox成長下のclaim・DB解放・通常負荷

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

既存停止復帰代表では大量既存Inboxと送信残件のclaim/pool占有・増幅を独立判定できない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-ASYNC |
| 確認契約 | Inbox/Outbox成長下のclaim・DB解放・通常負荷 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 100 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [324_Outbox・Inbox・冪等性・再送設計.md](<../../300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md>) Outbox・Inbox・冪等性・再送設計 > 8. API `mq_outbox` > 8.3 Claim/send ／ 固定承認本文 ／ commit `7147c428bb9d`
- [324_Outbox・Inbox・冪等性・再送設計.md](<../../300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md>) Outbox・Inbox・冪等性・再送設計 > 8. API `mq_outbox` > 8.3 Claim/send ／ 固定承認本文 ／ commit `7147c428bb9d`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.2 IT-CRASH・RETRY ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-043"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 1claim&lt;=100/lease10秒、未失効を競合workerがclaim0、JMSsend待ち中DBconnection保持0。confirm前SENT0、SENT時leaseclear。drainしたlogicalIDに二重業務更新0/未送信欠落0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 通常10名対象SLAを同source基準窓と判定、Inbox/WAL/DBlock/pool/queue/journal/oldest/drainを実測。根拠ないbacklog解消時間/throughput閾値を新設0、残件はID一覧で保全。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 1claim&lt;=100/lease10秒、未失効を競合workerがclaim0、JMSsend待ち中DBconnection保持0。confirm前SENT0、SENT時leaseclear。drainしたlogicalIDに二重業務更新0/未送信欠落0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 通常10名対象SLAを同source基準窓と判定、Inbox/WAL/DBlock/pool/queue/journal/oldest/drainを実測。根拠ないbacklog解消時間/throughput閾値を新設0、残件はID一覧で保全。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

既存停止復帰代表では大量既存Inboxと送信残件のclaim/pool占有・増幅を独立判定できない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-043`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-043-s01"></a>
#### IT-PERF-043-S01 / growth1000

種類：競合、反復：100、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "Inbox_rows": 1000,
  "Outbox_pending": 1000,
  "workers": 2,
  "lease_sec": 10,
  "claim_max": 100,
  "sync_clients": 10,
  "mix": "search70/game20/log10",
  "driver": "各row固有Message/tokenを事前freeze"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：1800秒測定+600秒drain観測、未解消を成功0件へ補完0。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 300秒warmup後backlog投入→1800秒通常負荷、claim/lease/sendconfirm/SENTとDBpoolを全ID採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "最終release/config/schema/protocol/master hashをrun manifestへfreeze",
  "hardware": "16GB/256GB、本番CPU型番/core/周波数/OS/JDKを固定",
  "clients": "USER8+ADMIN2各1inflight/think0 closed loop",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全HTTP/MQ/DB span、OS/PG/JVM/MQ/FD1秒。採取overhead無負荷対照を別保存",
  "statistics": "route/windowごとの全試行raw、p95=昇順ceil(.95*N)番、失敗/timeout/censoredを別件数として全issued分母に保持し成功選別0",
  "sla": "通常10名同期E2Ep95<=2.5s/MQwait各<=2.0s/取り違え0、未規定throughput/error許容率/劣化%を新設0",
  "stop": "所有/source/env変更/証拠欠落/仕様資源上限/安全停止境界で新規発行停止、inflightと未知commitを保全",
  "drain": "120秒の観測終了で残件を0補完0、各ID状態/最古/解消見通しを保全し承認復旧へ",
  "mass_balance": "issued=terminal+outstanding、accepted ID集合=確定unique+明示残件、二重業務更新0/拒否要求の更新0",
  "overrides": {
    "Inbox_rows": 1000,
    "Outbox_pending": 1000,
    "workers": 2,
    "lease_sec": 10,
    "claim_max": 100,
    "sync_clients": 10,
    "mix": "search70/game20/log10",
    "driver": "各row固有Message/tokenを事前freeze"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-043-S01/http.jsonl, IT-PERF-043-S01/wire.jsonl, IT-PERF-043-S01/db.jsonl, IT-PERF-043-S01/mq.jsonl, IT-PERF-043-S01/metric.jsonl, IT-PERF-043-S01/lock.jsonl, IT-PERF-043-S01/time.jsonl | 1claim&lt;=100/lease10秒、未失効を競合workerがclaim0、JMSsend待ち中DBconnection保持0。confirm前SENT0、SENT時leaseclear。drainしたlogicalIDに二重業務更新0/未送信欠落0。 |
| A02 | IT-PERF-043-S01/http.jsonl, IT-PERF-043-S01/wire.jsonl, IT-PERF-043-S01/db.jsonl, IT-PERF-043-S01/mq.jsonl, IT-PERF-043-S01/metric.jsonl, IT-PERF-043-S01/lock.jsonl, IT-PERF-043-S01/time.jsonl | 通常10名対象SLAを同source基準窓と判定、Inbox/WAL/DBlock/pool/queue/journal/oldest/drainを実測。根拠ないbacklog解消時間/throughput閾値を新設0、残件はID一覧で保全。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-043-s02"></a>
#### IT-PERF-043-S02 / growth10000

種類：競合、反復：100、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "Inbox_rows": 10000,
  "Outbox_pending": 10000,
  "workers": 2,
  "lease_sec": 10,
  "claim_max": 100,
  "sync_clients": 10,
  "mix": "search70/game20/log10",
  "driver": "各row固有Message/tokenを事前freeze"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：1800秒測定+600秒drain観測、未解消を成功0件へ補完0。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 300秒warmup後backlog投入→1800秒通常負荷、claim/lease/sendconfirm/SENTとDBpoolを全ID採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "最終release/config/schema/protocol/master hashをrun manifestへfreeze",
  "hardware": "16GB/256GB、本番CPU型番/core/周波数/OS/JDKを固定",
  "clients": "USER8+ADMIN2各1inflight/think0 closed loop",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全HTTP/MQ/DB span、OS/PG/JVM/MQ/FD1秒。採取overhead無負荷対照を別保存",
  "statistics": "route/windowごとの全試行raw、p95=昇順ceil(.95*N)番、失敗/timeout/censoredを別件数として全issued分母に保持し成功選別0",
  "sla": "通常10名同期E2Ep95<=2.5s/MQwait各<=2.0s/取り違え0、未規定throughput/error許容率/劣化%を新設0",
  "stop": "所有/source/env変更/証拠欠落/仕様資源上限/安全停止境界で新規発行停止、inflightと未知commitを保全",
  "drain": "120秒の観測終了で残件を0補完0、各ID状態/最古/解消見通しを保全し承認復旧へ",
  "mass_balance": "issued=terminal+outstanding、accepted ID集合=確定unique+明示残件、二重業務更新0/拒否要求の更新0",
  "overrides": {
    "Inbox_rows": 10000,
    "Outbox_pending": 10000,
    "workers": 2,
    "lease_sec": 10,
    "claim_max": 100,
    "sync_clients": 10,
    "mix": "search70/game20/log10",
    "driver": "各row固有Message/tokenを事前freeze"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A03 | IT-PERF-043-S02/http.jsonl, IT-PERF-043-S02/wire.jsonl, IT-PERF-043-S02/db.jsonl, IT-PERF-043-S02/mq.jsonl, IT-PERF-043-S02/metric.jsonl, IT-PERF-043-S02/lock.jsonl, IT-PERF-043-S02/time.jsonl | 1claim&lt;=100/lease10秒、未失効を競合workerがclaim0、JMSsend待ち中DBconnection保持0。confirm前SENT0、SENT時leaseclear。drainしたlogicalIDに二重業務更新0/未送信欠落0。 |
| A04 | IT-PERF-043-S02/http.jsonl, IT-PERF-043-S02/wire.jsonl, IT-PERF-043-S02/db.jsonl, IT-PERF-043-S02/mq.jsonl, IT-PERF-043-S02/metric.jsonl, IT-PERF-043-S02/lock.jsonl, IT-PERF-043-S02/time.jsonl | 通常10名対象SLAを同source基準窓と判定、Inbox/WAL/DBlock/pool/queue/journal/oldest/drainを実測。根拠ないbacklog解消時間/throughput閾値を新設0、残件はID一覧で保全。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-044"></a>
## IT-PERF-044 実Broker再接続・遅着replyと復帰残件の共存

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

初期接続と稼働中reconnectの回数上限を混同せず、復帰直後集中と遅着相関/permitを測定。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SYNC |
| 確認契約 | 実Broker再接続・遅着replyと復帰残件の共存 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 2 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [321_Artemis物理構成・JMS設定設計.md](<../../300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md>) Artemis物理構成・JMS設定設計 > 6. JMS connection factory ／ 固定承認本文 ／ commit `7147c428bb9d`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.2 IT-CRASH・RETRY ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（2件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-044"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 共通retryinterval1s/multiplier2/cap30s、failurecheck10s/TTL30s。runtime reconnectはprocess稼働中unlimited、initial3試行と取り違え0。実schedule/config/観測点を記録、未知timerjitterを新許容差で合格0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-OS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 故障中Web2秒timeout/9000と失敗率を全件保存、既確定QSBは同tokenで回復/二重question0、late replyは元相関だけACK/metric。復帰後outbox同ID送信、SENT確認/queue収束/通常10名SLAを別窓判定。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-OS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | message欠落/未確定ACK成功化/permit registry FD残留0。journal実復旧/全6Queue/security/durability確認後だけ公開、回線復帰だけで成功0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-OS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 共通retryinterval1s/multiplier2/cap30s、failurecheck10s/TTL30s。runtime reconnectはprocess稼働中unlimited、initial3試行と取り違え0。実schedule/config/観測点を記録、未知timerjitterを新許容差で合格0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-OS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 故障中Web2秒timeout/9000と失敗率を全件保存、既確定QSBは同tokenで回復/二重question0、late replyは元相関だけACK/metric。復帰後outbox同ID送信、SENT確認/queue収束/通常10名SLAを別窓判定。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-OS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A06 | message欠落/未確定ACK成功化/permit registry FD残留0。journal実復旧/全6Queue/security/durability確認後だけ公開、回線復帰だけで成功0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-OS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A07 | 共通retryinterval1s/multiplier2/cap30s、failurecheck10s/TTL30s。runtime reconnectはprocess稼働中unlimited、initial3試行と取り違え0。実schedule/config/観測点を記録、未知timerjitterを新許容差で合格0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-OS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A08 | 故障中Web2秒timeout/9000と失敗率を全件保存、既確定QSBは同tokenで回復/二重question0、late replyは元相関だけACK/metric。復帰後outbox同ID送信、SENT確認/queue収束/通常10名SLAを別窓判定。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-OS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A09 | message欠落/未確定ACK成功化/permit registry FD残留0。journal実復旧/全6Queue/security/durability確認後だけ公開、回線復帰だけで成功0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-OS, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

初期接続と稼働中reconnectの回数上限を混同せず、復帰直後集中と遅着相関/permitを測定。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-044`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-044-s01"></a>
#### IT-PERF-044-S01 / broker_stop

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "clients": 10,
  "mix": "search60/game20/QSB10/NTS10",
  "fault_seconds": 90,
  "normal_before_sec": 600,
  "recovery_measure_sec": 1800,
  "backlog": 1000,
  "direction": "Broker正規停止→起動"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：専有隔離loopback Broker正規停止→起動。待機：最大45分/SC、復帰未完で勝手にrestart連打/queuepurge0。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 300秒warmup→正常600秒→90秒指定通信故障→解除後1800秒を別窓で実測、同source正常対照と比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "最終release/config/schema/protocol/master hashをrun manifestへfreeze",
  "hardware": "16GB/256GB、本番CPU型番/core/周波数/OS/JDKを固定",
  "clients": "USER8+ADMIN2各1inflight/think0 closed loop",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全HTTP/MQ/DB span、OS/PG/JVM/MQ/FD1秒。採取overhead無負荷対照を別保存",
  "statistics": "route/windowごとの全試行raw、p95=昇順ceil(.95*N)番、失敗/timeout/censoredを別件数として全issued分母に保持し成功選別0",
  "sla": "通常10名同期E2Ep95<=2.5s/MQwait各<=2.0s/取り違え0、未規定throughput/error許容率/劣化%を新設0",
  "stop": "所有/source/env変更/証拠欠落/仕様資源上限/安全停止境界で新規発行停止、inflightと未知commitを保全",
  "drain": "120秒の観測終了で残件を0補完0、各ID状態/最古/解消見通しを保全し承認復旧へ",
  "mass_balance": "issued=terminal+outstanding、accepted ID集合=確定unique+明示残件、二重業務更新0/拒否要求の更新0",
  "overrides": {
    "clients": 10,
    "mix": "search60/game20/QSB10/NTS10",
    "fault_seconds": 90,
    "normal_before_sec": 600,
    "recovery_measure_sec": 1800,
    "backlog": 1000,
    "direction": "Broker正規停止→起動"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-044-S01/http.jsonl, IT-PERF-044-S01/wire.jsonl, IT-PERF-044-S01/db.jsonl, IT-PERF-044-S01/mq.jsonl, IT-PERF-044-S01/os.jsonl, IT-PERF-044-S01/metric.jsonl, IT-PERF-044-S01/time.jsonl | 共通retryinterval1s/multiplier2/cap30s、failurecheck10s/TTL30s。runtime reconnectはprocess稼働中unlimited、initial3試行と取り違え0。実schedule/config/観測点を記録、未知timerjitterを新許容差で合格0。 |
| A02 | IT-PERF-044-S01/http.jsonl, IT-PERF-044-S01/wire.jsonl, IT-PERF-044-S01/db.jsonl, IT-PERF-044-S01/mq.jsonl, IT-PERF-044-S01/os.jsonl, IT-PERF-044-S01/metric.jsonl, IT-PERF-044-S01/time.jsonl | 故障中Web2秒timeout/9000と失敗率を全件保存、既確定QSBは同tokenで回復/二重question0、late replyは元相関だけACK/metric。復帰後outbox同ID送信、SENT確認/queue収束/通常10名SLAを別窓判定。 |
| A03 | IT-PERF-044-S01/http.jsonl, IT-PERF-044-S01/wire.jsonl, IT-PERF-044-S01/db.jsonl, IT-PERF-044-S01/mq.jsonl, IT-PERF-044-S01/os.jsonl, IT-PERF-044-S01/metric.jsonl, IT-PERF-044-S01/time.jsonl | message欠落/未確定ACK成功化/permit registry FD残留0。journal実復旧/全6Queue/security/durability確認後だけ公開、回線復帰だけで成功0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-044-s02"></a>
#### IT-PERF-044-S02 / reply_loss

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "clients": 10,
  "mix": "search60/game20/QSB10/NTS10",
  "fault_seconds": 90,
  "normal_before_sec": 600,
  "recovery_measure_sec": 1800,
  "backlog": 1000,
  "direction": "API→Web reply方向だけ遮断"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：専有隔離loopback API→Web reply方向だけ遮断。待機：最大45分/SC、復帰未完で勝手にrestart連打/queuepurge0。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 300秒warmup→正常600秒→90秒指定通信故障→解除後1800秒を別窓で実測、同source正常対照と比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "最終release/config/schema/protocol/master hashをrun manifestへfreeze",
  "hardware": "16GB/256GB、本番CPU型番/core/周波数/OS/JDKを固定",
  "clients": "USER8+ADMIN2各1inflight/think0 closed loop",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全HTTP/MQ/DB span、OS/PG/JVM/MQ/FD1秒。採取overhead無負荷対照を別保存",
  "statistics": "route/windowごとの全試行raw、p95=昇順ceil(.95*N)番、失敗/timeout/censoredを別件数として全issued分母に保持し成功選別0",
  "sla": "通常10名同期E2Ep95<=2.5s/MQwait各<=2.0s/取り違え0、未規定throughput/error許容率/劣化%を新設0",
  "stop": "所有/source/env変更/証拠欠落/仕様資源上限/安全停止境界で新規発行停止、inflightと未知commitを保全",
  "drain": "120秒の観測終了で残件を0補完0、各ID状態/最古/解消見通しを保全し承認復旧へ",
  "mass_balance": "issued=terminal+outstanding、accepted ID集合=確定unique+明示残件、二重業務更新0/拒否要求の更新0",
  "overrides": {
    "clients": 10,
    "mix": "search60/game20/QSB10/NTS10",
    "fault_seconds": 90,
    "normal_before_sec": 600,
    "recovery_measure_sec": 1800,
    "backlog": 1000,
    "direction": "API→Web reply方向だけ遮断"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A04 | IT-PERF-044-S02/http.jsonl, IT-PERF-044-S02/wire.jsonl, IT-PERF-044-S02/db.jsonl, IT-PERF-044-S02/mq.jsonl, IT-PERF-044-S02/os.jsonl, IT-PERF-044-S02/metric.jsonl, IT-PERF-044-S02/time.jsonl | 共通retryinterval1s/multiplier2/cap30s、failurecheck10s/TTL30s。runtime reconnectはprocess稼働中unlimited、initial3試行と取り違え0。実schedule/config/観測点を記録、未知timerjitterを新許容差で合格0。 |
| A05 | IT-PERF-044-S02/http.jsonl, IT-PERF-044-S02/wire.jsonl, IT-PERF-044-S02/db.jsonl, IT-PERF-044-S02/mq.jsonl, IT-PERF-044-S02/os.jsonl, IT-PERF-044-S02/metric.jsonl, IT-PERF-044-S02/time.jsonl | 故障中Web2秒timeout/9000と失敗率を全件保存、既確定QSBは同tokenで回復/二重question0、late replyは元相関だけACK/metric。復帰後outbox同ID送信、SENT確認/queue収束/通常10名SLAを別窓判定。 |
| A06 | IT-PERF-044-S02/http.jsonl, IT-PERF-044-S02/wire.jsonl, IT-PERF-044-S02/db.jsonl, IT-PERF-044-S02/mq.jsonl, IT-PERF-044-S02/os.jsonl, IT-PERF-044-S02/metric.jsonl, IT-PERF-044-S02/time.jsonl | message欠落/未確定ACK成功化/permit registry FD残留0。journal実復旧/全6Queue/security/durability確認後だけ公開、回線復帰だけで成功0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-044-s03"></a>
#### IT-PERF-044-S03 / request_loss

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "clients": 10,
  "mix": "search60/game20/QSB10/NTS10",
  "fault_seconds": 90,
  "normal_before_sec": 600,
  "recovery_measure_sec": 1800,
  "backlog": 1000,
  "direction": "Web→Broker request方向だけ遮断"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：専有隔離loopback Web→Broker request方向だけ遮断。待機：最大45分/SC、復帰未完で勝手にrestart連打/queuepurge0。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 300秒warmup→正常600秒→90秒指定通信故障→解除後1800秒を別窓で実測、同source正常対照と比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "最終release/config/schema/protocol/master hashをrun manifestへfreeze",
  "hardware": "16GB/256GB、本番CPU型番/core/周波数/OS/JDKを固定",
  "clients": "USER8+ADMIN2各1inflight/think0 closed loop",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全HTTP/MQ/DB span、OS/PG/JVM/MQ/FD1秒。採取overhead無負荷対照を別保存",
  "statistics": "route/windowごとの全試行raw、p95=昇順ceil(.95*N)番、失敗/timeout/censoredを別件数として全issued分母に保持し成功選別0",
  "sla": "通常10名同期E2Ep95<=2.5s/MQwait各<=2.0s/取り違え0、未規定throughput/error許容率/劣化%を新設0",
  "stop": "所有/source/env変更/証拠欠落/仕様資源上限/安全停止境界で新規発行停止、inflightと未知commitを保全",
  "drain": "120秒の観測終了で残件を0補完0、各ID状態/最古/解消見通しを保全し承認復旧へ",
  "mass_balance": "issued=terminal+outstanding、accepted ID集合=確定unique+明示残件、二重業務更新0/拒否要求の更新0",
  "overrides": {
    "clients": 10,
    "mix": "search60/game20/QSB10/NTS10",
    "fault_seconds": 90,
    "normal_before_sec": 600,
    "recovery_measure_sec": 1800,
    "backlog": 1000,
    "direction": "Web→Broker request方向だけ遮断"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A07 | IT-PERF-044-S03/http.jsonl, IT-PERF-044-S03/wire.jsonl, IT-PERF-044-S03/db.jsonl, IT-PERF-044-S03/mq.jsonl, IT-PERF-044-S03/os.jsonl, IT-PERF-044-S03/metric.jsonl, IT-PERF-044-S03/time.jsonl | 共通retryinterval1s/multiplier2/cap30s、failurecheck10s/TTL30s。runtime reconnectはprocess稼働中unlimited、initial3試行と取り違え0。実schedule/config/観測点を記録、未知timerjitterを新許容差で合格0。 |
| A08 | IT-PERF-044-S03/http.jsonl, IT-PERF-044-S03/wire.jsonl, IT-PERF-044-S03/db.jsonl, IT-PERF-044-S03/mq.jsonl, IT-PERF-044-S03/os.jsonl, IT-PERF-044-S03/metric.jsonl, IT-PERF-044-S03/time.jsonl | 故障中Web2秒timeout/9000と失敗率を全件保存、既確定QSBは同tokenで回復/二重question0、late replyは元相関だけACK/metric。復帰後outbox同ID送信、SENT確認/queue収束/通常10名SLAを別窓判定。 |
| A09 | IT-PERF-044-S03/http.jsonl, IT-PERF-044-S03/wire.jsonl, IT-PERF-044-S03/db.jsonl, IT-PERF-044-S03/mq.jsonl, IT-PERF-044-S03/os.jsonl, IT-PERF-044-S03/metric.jsonl, IT-PERF-044-S03/time.jsonl | message欠落/未確定ACK成功化/permit registry FD残留0。journal実復旧/全6Queue/security/durability確認後だけ公開、回線復帰だけで成功0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-045"></a>
## IT-PERF-045 最大inline snapshot・鍵世代とDB/MQ資源

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

file48MB代表だけでは最大inline snapshotの暗号/圧縮/DB保存増幅と鍵借用を検証できない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | 最大inline snapshot・鍵世代とDB/MQ資源 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 2 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 5. Decode algorithm ／ 固定承認本文 ／ commit `7147c428bb9d`
- [324_Outbox・Inbox・冪等性・再送設計.md](<../../300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md>) Outbox・Inbox・冪等性・再送設計 > 6. Response保存・再構成 > 保存元Message binding（SSC-033） ／ ['SSC-033'] ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 4. Large-result判定・レイアウト ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-045"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | SCNinline200/total961984byte、plaintext&lt;=1000000/保存cipher&lt;=1050000、固定header/data/record全byteは独立表と一致、再送DATA不変/headerfresh。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 圧縮Deflater3/NKENC1/AAD/currentwrite/previousreadを独立標準decoder/JCEで検証、JDK再圧縮byteや乱数nonce/ciphertext完全一致をoracleへ使わない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | E2Ep95&lt;=2.5s/MQwait&lt;=2.0s、DBpool/heap/direct/FD/借用鍵残留0、drain後borrower0確認前の旧鍵退役0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | plaintext961984/上限1000000/cipher&lt;=1050000、独立decode/JCEで全record/順序一致。圧縮率に最低条件を新設0、Deflater3とJDK生成差をbyte完全一致へ誤適用0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 対象通常10名SLA/E2Ep95&lt;=2.5s/MQwait&lt;=2s、再送二重業務更新0/原snapshotDATA不変、全borrower/FD/poolは終端回収。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

file48MB代表だけでは最大inline snapshotの暗号/圧縮/DB保存増幅と鍵借用を検証できない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-045`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-045-s01"></a>
#### IT-PERF-045-S01 / inline200

種類：境界、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN_records": 200,
  "fixed_total_bytes": 961984,
  "body_pattern": "各fieldmax付近の低圧縮deterministic seed20261102、Unicode/byte境界維持",
  "clients": 10,
  "mix": "SCNinline50/search30/Game20",
  "key_profile": "currentwrite/previousread"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実200recordをinline返却しsnapshot保存/再送、300秒warmup→1800秒×2で資源測定。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "最終release/config/schema/protocol/master hashをrun manifestへfreeze",
  "hardware": "16GB/256GB、本番CPU型番/core/周波数/OS/JDKを固定",
  "clients": "USER8+ADMIN2各1inflight/think0 closed loop",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全HTTP/MQ/DB span、OS/PG/JVM/MQ/FD1秒。採取overhead無負荷対照を別保存",
  "statistics": "route/windowごとの全試行raw、p95=昇順ceil(.95*N)番、失敗/timeout/censoredを別件数として全issued分母に保持し成功選別0",
  "sla": "通常10名同期E2Ep95<=2.5s/MQwait各<=2.0s/取り違え0、未規定throughput/error許容率/劣化%を新設0",
  "stop": "所有/source/env変更/証拠欠落/仕様資源上限/安全停止境界で新規発行停止、inflightと未知commitを保全",
  "drain": "120秒の観測終了で残件を0補完0、各ID状態/最古/解消見通しを保全し承認復旧へ",
  "mass_balance": "issued=terminal+outstanding、accepted ID集合=確定unique+明示残件、二重業務更新0/拒否要求の更新0",
  "overrides": {
    "SCN_records": 200,
    "fixed_total_bytes": 961984,
    "body_pattern": "各fieldmax付近の低圧縮deterministic seed20261102、Unicode/byte境界維持",
    "clients": 10,
    "mix": "SCNinline50/search30/Game20",
    "key_profile": "currentwrite/previousread"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-045-S01/http.jsonl, IT-PERF-045-S01/wire.jsonl, IT-PERF-045-S01/db.jsonl, IT-PERF-045-S01/mq.jsonl, IT-PERF-045-S01/metric.jsonl, IT-PERF-045-S01/time.jsonl | SCNinline200/total961984byte、plaintext&lt;=1000000/保存cipher&lt;=1050000、固定header/data/record全byteは独立表と一致、再送DATA不変/headerfresh。 |
| A02 | IT-PERF-045-S01/http.jsonl, IT-PERF-045-S01/wire.jsonl, IT-PERF-045-S01/db.jsonl, IT-PERF-045-S01/mq.jsonl, IT-PERF-045-S01/metric.jsonl, IT-PERF-045-S01/time.jsonl | 圧縮Deflater3/NKENC1/AAD/currentwrite/previousreadを独立標準decoder/JCEで検証、JDK再圧縮byteや乱数nonce/ciphertext完全一致をoracleへ使わない。 |
| A03 | IT-PERF-045-S01/http.jsonl, IT-PERF-045-S01/wire.jsonl, IT-PERF-045-S01/db.jsonl, IT-PERF-045-S01/mq.jsonl, IT-PERF-045-S01/metric.jsonl, IT-PERF-045-S01/time.jsonl | E2Ep95&lt;=2.5s/MQwait&lt;=2.0s、DBpool/heap/direct/FD/借用鍵残留0、drain後borrower0確認前の旧鍵退役0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-045-s02"></a>
#### IT-PERF-045-S02 / inline200_compressible

種類：境界、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN_records": 200,
  "fixed_total_bytes": 961984,
  "body_pattern": "全record反復ASCII A、ID/sequenceだけ独立表の正値",
  "clients": 10,
  "mix": "SCNinline50/search30/Game20"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実最大inlineを返却保存/再送、300秒warmup→1800秒×2で暗号/DB/MQ/資源を採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "mode": "STANDARD",
  "artifact": "最終release/config/schema/protocol/master hashをrun manifestへfreeze",
  "hardware": "16GB/256GB、本番CPU型番/core/周波数/OS/JDKを固定",
  "clients": "USER8+ADMIN2各1inflight/think0 closed loop",
  "warmup_seconds": 300,
  "measurement_seconds": 1800,
  "repetitions": 2,
  "sampling": "全HTTP/MQ/DB span、OS/PG/JVM/MQ/FD1秒。採取overhead無負荷対照を別保存",
  "statistics": "route/windowごとの全試行raw、p95=昇順ceil(.95*N)番、失敗/timeout/censoredを別件数として全issued分母に保持し成功選別0",
  "sla": "通常10名同期E2Ep95<=2.5s/MQwait各<=2.0s/取り違え0、未規定throughput/error許容率/劣化%を新設0",
  "stop": "所有/source/env変更/証拠欠落/仕様資源上限/安全停止境界で新規発行停止、inflightと未知commitを保全",
  "drain": "120秒の観測終了で残件を0補完0、各ID状態/最古/解消見通しを保全し承認復旧へ",
  "mass_balance": "issued=terminal+outstanding、accepted ID集合=確定unique+明示残件、二重業務更新0/拒否要求の更新0",
  "overrides": {
    "SCN_records": 200,
    "fixed_total_bytes": 961984,
    "body_pattern": "全record反復ASCII A、ID/sequenceだけ独立表の正値",
    "clients": 10,
    "mix": "SCNinline50/search30/Game20"
  }
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A04 | IT-PERF-045-S02/http.jsonl, IT-PERF-045-S02/wire.jsonl, IT-PERF-045-S02/db.jsonl, IT-PERF-045-S02/mq.jsonl, IT-PERF-045-S02/metric.jsonl, IT-PERF-045-S02/time.jsonl | plaintext961984/上限1000000/cipher&lt;=1050000、独立decode/JCEで全record/順序一致。圧縮率に最低条件を新設0、Deflater3とJDK生成差をbyte完全一致へ誤適用0。 |
| A05 | IT-PERF-045-S02/http.jsonl, IT-PERF-045-S02/wire.jsonl, IT-PERF-045-S02/db.jsonl, IT-PERF-045-S02/mq.jsonl, IT-PERF-045-S02/metric.jsonl, IT-PERF-045-S02/time.jsonl | 対象通常10名SLA/E2Ep95&lt;=2.5s/MQwait&lt;=2s、再送二重業務更新0/原snapshotDATA不変、全borrower/FD/poolは終端回収。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-perf-046"></a>
## IT-PERF-046 JVM heap OOMとcgroup MemoryMaxの実終了・durable復旧

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

平常時RSS上限とheap90%alertだけでは実OOM/MemoryMax時のExitOnOOM・PID1再起動・dump非生成と確定済DB/MQの保全を検出できない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-OPS |
| 確認契約 | JVM heap OOMとcgroup MemoryMaxの実終了・durable復旧 |
| 必要環境 | E-OPS |
| artifact/設定/schema/data版 | F-AUDIT-v2: 独立clone、schema/config/protocolは最終manifest固定。各SCの入力と初期状態を適用。fixture-spec-v2参照。 |
| 事前条件・依存 | 他case結果への依存なし。source/environment/active jobs/所有とHOLDの照合、namespace予約成功後のみ準備。各SCごと初期cloneへ戻す。業務経路は実Login/CSRFをsetup内で取得。 |
| 同期・待機 | SCの一回barrier receiptにより到達を確認。観測不能ならBLOCKED、sleepで確定点を推測しない。 |
| 故障注入・並行・再現 | 各SCのinjection。専有隔離環境の所有部品だけ。PG/PT/現用環境へ注入禁止。 |
| 反復 | 2 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [342_Caddy・systemd・PostgreSQL・Java設定設計.md](<../../300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md>) Caddy・systemd・PostgreSQL・Java設定設計 > 5. Java/JVM・Spring process > 5.1 Resource ／ 固定承認本文 ／ commit `7147c428bb9d`
- [353_障害検知・復旧runbook.md](<../../300_SS/350_運用・品質/353_障害検知・復旧runbook.md>) 障害検知・復旧runbook > 9. RB-006 Disk・memory・resource枯渇 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) Log・metric・alert・error code設計 > 7. Alert condition ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-PERF-046"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | ExitOnOutOfMemoryError有効のactualJVM heap枯渇でprocess非0終端。manual new OutOfMemoryErrorやproxythrowはこの実OOMEの代用0。numeric exitはJDK実値として保存し未規定固定値を期待0。 | O-OS, O-DB, O-MQ, O-FS, O-WIRE, O-METRIC, O-LOG, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | criticalalert同condition/service1/heapdump・core・credentialdump新規0、failurecode/bootINV/PIDticks/cgroup/GC/実memory.eventsを私有保全。operator SIGKILL/上限拡大/timeout延長/全purge0。 | O-OS, O-DB, O-MQ, O-FS, O-WIRE, O-METRIC, O-LOG, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 旧process消失を旧close正常へ補完0。on-failureの再起動要求は既5秒/600秒内5回を維持、Root/permit/世代の正規gateが不成立なら停止/HOLDし、旧permit偽装や再start反復で通さない。新sourceの正規回復所有・全readyが成立後だけ通常復帰判定。 | O-OS, O-DB, O-MQ, O-FS, O-WIRE, O-METRIC, O-LOG, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 確定M0は同Message/tokenでInboxreplay、User1001の新規は合計1/業務監査追加0、W1は同Wのworker1/FIFOでanswer1/STUB空文字、Outbox再送と物理送信重複を論理更新1へ照合。未commitの更新を成功補完0。 | O-OS, O-DB, O-MQ, O-FS, O-WIRE, O-METRIC, O-LOG, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | post全routeSLA/2秒MQ/2.5秒E2E・pool/FD/thread/lease回収とqueue減少を正常対照と別記録。障害窓timeoutを率の分母から除外0、未規定復旧秒数を合格閾値に新設0。計測buildだけで正式releaseの性能適合認定0。 | O-OS, O-DB, O-MQ, O-FS, O-WIRE, O-METRIC, O-LOG, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A06 | cgroup MemoryMax到達をmemory.eventsのoom/oom_kill増加と対象PIDの実kernel終端へ結合。外部からSIGKILL送信0、kernelOOMをSendSIGKILL=noのtimeout強制kill禁止と混同0。host全体OOMを起こすprofileは開始不可。 | O-OS, O-DB, O-MQ, O-FS, O-WIRE, O-METRIC, O-LOG, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A07 | criticalalert同condition/service1/heapdump・core・credentialdump新規0、failurecode/bootINV/PIDticks/cgroup/GC/実memory.eventsを私有保全。operator SIGKILL/上限拡大/timeout延長/全purge0。 | O-OS, O-DB, O-MQ, O-FS, O-WIRE, O-METRIC, O-LOG, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A08 | 旧process消失を旧close正常へ補完0。on-failureの再起動要求は既5秒/600秒内5回を維持、Root/permit/世代の正規gateが不成立なら停止/HOLDし、旧permit偽装や再start反復で通さない。新sourceの正規回復所有・全readyが成立後だけ通常復帰判定。 | O-OS, O-DB, O-MQ, O-FS, O-WIRE, O-METRIC, O-LOG, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A09 | 確定M0は同Message/tokenでInboxreplay、User1001の新規は合計1/業務監査追加0、W1は同Wのworker1/FIFOでanswer1/STUB空文字、Outbox再送と物理送信重複を論理更新1へ照合。未commitの更新を成功補完0。 | O-OS, O-DB, O-MQ, O-FS, O-WIRE, O-METRIC, O-LOG, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A10 | post全routeSLA/2秒MQ/2.5秒E2E・pool/FD/thread/lease回収とqueue減少を正常対照と別記録。障害窓timeoutを率の分母から除外0、未規定復旧秒数を合格閾値に新設0。計測buildだけで正式releaseの性能適合認定0。 | O-OS, O-DB, O-MQ, O-FS, O-WIRE, O-METRIC, O-LOG, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, DEP-OPS-HOLD を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

平常時RSS上限とheap90%alertだけでは実OOM/MemoryMax時のExitOnOOM・PID1再起動・dump非生成と確定済DB/MQの保全を検出できない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-046`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-046-s01"></a>
#### IT-PERF-046-S01 / heap

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "target": "専有API ordinary実Unit/同source署名試験build",
  "limits": "Xmx1024m/MemoryMax2048M・Direct256m/Metaspace256m不変更",
  "initial": "M0 UCR DB/User1001/Inbox/criticalaudit commit確認、reply/ACK前barrier。W1QuestionRECEIVEDとOutboxSENT1も保全",
  "fault": "T-MEMORY-v3:8MiB実heap retained allocationを最大128回、actualOOMEを誘発",
  "normal_load": "10clients(8USER2ADMIN)closedloop/100slot search70/game20/Log10・515割当、warmup300s/pre600s/post1800s、同source正常対照2反復"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：T-MEMORY-v3:8MiB実heap retained allocationを最大128回、actualOOMEを誘発。待機：T-MEMORY最大128heap又は32native割当で終了、120秒watchdog。元Unitstart120s/stop60s/5sretryを延長0。元job未知は再発行0、回復/測定1800s窓と通常対象SLAを分離。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 独立commitreceipt採取→有限一回メモリ故障→JVM/PID1/cgroup終端→次正規起動の入場gate→同ID再配送→通常負荷復帰を全時系列で観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "warmup_seconds": 300,
  "pre_seconds": 600,
  "post_seconds": 1800,
  "clients": 10,
  "arrival": "closed-loop/1inflight perclient",
  "mix_100slots": {
    "search": 70,
    "game": 20,
    "ADMIN_Log": 10
  },
  "counterpart": "同source/fixture/profile・同期間の非故障対照2回",
  "failure_window": "全raw・失敗分母に残す、正常SLA範囲の区分はSS/UIのまま",
  "max_allocations": 128,
  "tool_state": "UNIMPLEMENTED",
  "restriction": "専有16GB/256GBとhost安全収支/全既存HOLD確認後。PGPTVM/現用環境へ接続0。"
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-PERF-046-S01/os.jsonl, IT-PERF-046-S01/db.jsonl, IT-PERF-046-S01/mq.jsonl, IT-PERF-046-S01/fs.jsonl, IT-PERF-046-S01/wire.jsonl, IT-PERF-046-S01/metric.jsonl, IT-PERF-046-S01/log.jsonl, IT-PERF-046-S01/time.jsonl | ExitOnOutOfMemoryError有効のactualJVM heap枯渇でprocess非0終端。manual new OutOfMemoryErrorやproxythrowはこの実OOMEの代用0。numeric exitはJDK実値として保存し未規定固定値を期待0。 |
| A02 | IT-PERF-046-S01/os.jsonl, IT-PERF-046-S01/db.jsonl, IT-PERF-046-S01/mq.jsonl, IT-PERF-046-S01/fs.jsonl, IT-PERF-046-S01/wire.jsonl, IT-PERF-046-S01/metric.jsonl, IT-PERF-046-S01/log.jsonl, IT-PERF-046-S01/time.jsonl | criticalalert同condition/service1/heapdump・core・credentialdump新規0、failurecode/bootINV/PIDticks/cgroup/GC/実memory.eventsを私有保全。operator SIGKILL/上限拡大/timeout延長/全purge0。 |
| A03 | IT-PERF-046-S01/os.jsonl, IT-PERF-046-S01/db.jsonl, IT-PERF-046-S01/mq.jsonl, IT-PERF-046-S01/fs.jsonl, IT-PERF-046-S01/wire.jsonl, IT-PERF-046-S01/metric.jsonl, IT-PERF-046-S01/log.jsonl, IT-PERF-046-S01/time.jsonl | 旧process消失を旧close正常へ補完0。on-failureの再起動要求は既5秒/600秒内5回を維持、Root/permit/世代の正規gateが不成立なら停止/HOLDし、旧permit偽装や再start反復で通さない。新sourceの正規回復所有・全readyが成立後だけ通常復帰判定。 |
| A04 | IT-PERF-046-S01/os.jsonl, IT-PERF-046-S01/db.jsonl, IT-PERF-046-S01/mq.jsonl, IT-PERF-046-S01/fs.jsonl, IT-PERF-046-S01/wire.jsonl, IT-PERF-046-S01/metric.jsonl, IT-PERF-046-S01/log.jsonl, IT-PERF-046-S01/time.jsonl | 確定M0は同Message/tokenでInboxreplay、User1001の新規は合計1/業務監査追加0、W1は同Wのworker1/FIFOでanswer1/STUB空文字、Outbox再送と物理送信重複を論理更新1へ照合。未commitの更新を成功補完0。 |
| A05 | IT-PERF-046-S01/os.jsonl, IT-PERF-046-S01/db.jsonl, IT-PERF-046-S01/mq.jsonl, IT-PERF-046-S01/fs.jsonl, IT-PERF-046-S01/wire.jsonl, IT-PERF-046-S01/metric.jsonl, IT-PERF-046-S01/log.jsonl, IT-PERF-046-S01/time.jsonl | post全routeSLA/2秒MQ/2.5秒E2E・pool/FD/thread/lease回収とqueue減少を正常対照と別記録。障害窓timeoutを率の分母から除外0、未規定復旧秒数を合格閾値に新設0。計測buildだけで正式releaseの性能適合認定0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-046-s02"></a>
#### IT-PERF-046-S02 / memorymax

種類：復旧、反復：2、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "target": "専有API ordinary実Unit/同source署名試験build",
  "limits": "Xmx1024m/MemoryMax2048M・Direct256m/Metaspace256m不変更",
  "initial": "M0 UCR DB/User1001/Inbox/criticalaudit commit確認、reply/ACK前barrier。W1QuestionRECEIVEDとOutboxSENT1も保全",
  "fault": "T-MEMORY-v3:同cgroup内API所有native匿名領域64MiBを最大32回実touch",
  "normal_load": "10clients(8USER2ADMIN)closedloop/100slot search70/game20/Log10・515割当、warmup300s/pre600s/post1800s、同source正常対照2反復"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：T-MEMORY-v3:同cgroup内API所有native匿名領域64MiBを最大32回実touch。待機：T-MEMORY最大128heap又は32native割当で終了、120秒watchdog。元Unitstart120s/stop60s/5sretryを延長0。元job未知は再発行0、回復/測定1800s窓と通常対象SLAを分離。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 独立commitreceipt採取→有限一回メモリ故障→JVM/PID1/cgroup終端→次正規起動の入場gate→同ID再配送→通常負荷復帰を全時系列で観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

負荷計画（値は共通計画にこのSC入力を優先）：

```json
{
  "warmup_seconds": 300,
  "pre_seconds": 600,
  "post_seconds": 1800,
  "clients": 10,
  "arrival": "closed-loop/1inflight perclient",
  "mix_100slots": {
    "search": 70,
    "game": 20,
    "ADMIN_Log": 10
  },
  "counterpart": "同source/fixture/profile・同期間の非故障対照2回",
  "failure_window": "全raw・失敗分母に残す、正常SLA範囲の区分はSS/UIのまま",
  "max_allocations": 32,
  "tool_state": "UNIMPLEMENTED",
  "restriction": "専有16GB/256GBとhost安全収支/全既存HOLD確認後。PGPTVM/現用環境へ接続0。"
}
```

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A06 | IT-PERF-046-S02/os.jsonl, IT-PERF-046-S02/db.jsonl, IT-PERF-046-S02/mq.jsonl, IT-PERF-046-S02/fs.jsonl, IT-PERF-046-S02/wire.jsonl, IT-PERF-046-S02/metric.jsonl, IT-PERF-046-S02/log.jsonl, IT-PERF-046-S02/time.jsonl | cgroup MemoryMax到達をmemory.eventsのoom/oom_kill増加と対象PIDの実kernel終端へ結合。外部からSIGKILL送信0、kernelOOMをSendSIGKILL=noのtimeout強制kill禁止と混同0。host全体OOMを起こすprofileは開始不可。 |
| A07 | IT-PERF-046-S02/os.jsonl, IT-PERF-046-S02/db.jsonl, IT-PERF-046-S02/mq.jsonl, IT-PERF-046-S02/fs.jsonl, IT-PERF-046-S02/wire.jsonl, IT-PERF-046-S02/metric.jsonl, IT-PERF-046-S02/log.jsonl, IT-PERF-046-S02/time.jsonl | criticalalert同condition/service1/heapdump・core・credentialdump新規0、failurecode/bootINV/PIDticks/cgroup/GC/実memory.eventsを私有保全。operator SIGKILL/上限拡大/timeout延長/全purge0。 |
| A08 | IT-PERF-046-S02/os.jsonl, IT-PERF-046-S02/db.jsonl, IT-PERF-046-S02/mq.jsonl, IT-PERF-046-S02/fs.jsonl, IT-PERF-046-S02/wire.jsonl, IT-PERF-046-S02/metric.jsonl, IT-PERF-046-S02/log.jsonl, IT-PERF-046-S02/time.jsonl | 旧process消失を旧close正常へ補完0。on-failureの再起動要求は既5秒/600秒内5回を維持、Root/permit/世代の正規gateが不成立なら停止/HOLDし、旧permit偽装や再start反復で通さない。新sourceの正規回復所有・全readyが成立後だけ通常復帰判定。 |
| A09 | IT-PERF-046-S02/os.jsonl, IT-PERF-046-S02/db.jsonl, IT-PERF-046-S02/mq.jsonl, IT-PERF-046-S02/fs.jsonl, IT-PERF-046-S02/wire.jsonl, IT-PERF-046-S02/metric.jsonl, IT-PERF-046-S02/log.jsonl, IT-PERF-046-S02/time.jsonl | 確定M0は同Message/tokenでInboxreplay、User1001の新規は合計1/業務監査追加0、W1は同Wのworker1/FIFOでanswer1/STUB空文字、Outbox再送と物理送信重複を論理更新1へ照合。未commitの更新を成功補完0。 |
| A10 | IT-PERF-046-S02/os.jsonl, IT-PERF-046-S02/db.jsonl, IT-PERF-046-S02/mq.jsonl, IT-PERF-046-S02/fs.jsonl, IT-PERF-046-S02/wire.jsonl, IT-PERF-046-S02/metric.jsonl, IT-PERF-046-S02/log.jsonl, IT-PERF-046-S02/time.jsonl | post全routeSLA/2秒MQ/2.5秒E2E・pool/FD/thread/lease回収とqueue減少を正常対照と別記録。障害窓timeoutを率の分母から除外0、未規定復旧秒数を合格閾値に新設0。計測buildだけで正式releaseの性能適合認定0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。
