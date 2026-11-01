# 性能・資源・Logout混在 結合テストケース

編集正本は [cases.json](../data/cases.json)。この巻は自動生成。全件NOT_EXECUTED。SUPERSEDEDは旧ID履歴。PENDING_REAUDITは具体シナリオ再監査待ちで、仕様確定・実行可能へ算入しない。

全ケースは [512](../510_方針・準備/512_結合構成・環境・データ.md) の経路・環境・fixture・観測・C-ISOLATE と [541](../540_実行・管理/541_Codex実行・判定・証跡・再開.md) を参照する。共通CP-BASEの入力以外の初期状態・証跡・中断・後片付けは cases.json.profiles に一元化し、個別追加条件と併せて必須とする。

他巻：[インターフェース](521_インターフェース.md) / [トランザクション・データ](522_トランザクション・データ.md) / [認証・権限・セキュリティ](523_認証・権限・セキュリティ.md) / [ファイル・メディア・Range](524_ファイル・メディア・Range.md) / [運用・復旧・監視](525_運用・復旧・監視.md) / [MQ・非同期・容量](526_MQ・非同期・容量.md) / [性能・資源・Logout混在](527_性能・資源・Logout混在.md)

<a id="it-perf-001"></a>
## IT-PERF-001 STANDARD10名・同期p95/MQ待ち

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

STANDARD10名・同期p95/MQ待ちによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SYNC |
| 確認契約 | STANDARD10名・同期p95/MQ待ち |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 故障なし。負荷generatorとserverの時計相関・collector overheadを事前校正。 |
| 反復 | 1 |
| timeout・中断 | case45分。最低sample不足は不足扱い、新窓を事前固定して追加し同窓へ偽合算しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [342_Caddy・systemd・PostgreSQL・Java設定設計.md](<../../300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md>) §8 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [362_PG・PT・IT工程引継ぎ事項.md](<../../300_SS/360_引継ぎ・監査/362_PG・PT・IT工程引継ぎ事項.md>) §7 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "mode": "STANDARD",
  "users": 10,
  "inflight_per_user": 1,
  "warmup_minutes": 5,
  "measure_minutes": 30,
  "workload": "Login/Scenario検索/明細/Logを各独立窓、USER8+ADMIN2、最悪検索100件、各user think0で1完了後次。route別sample最低1000。"
}
```

**操作順序・入口**

同じ正規release/fixtureを各窓へ復元→5分warmup（窓外と明示）→barrier10userを解放→30分の全試行をraw CSVへ記録。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 各同期routeのp95=sort全試行elapsedのceil(.95*N)番&lt;=2.5秒、Web打鍵→描画完了まで。MQ待ち各要求&lt;=2.0秒、取り違え0、業務後条件一致。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A02 | timeout/error試行を分母から落とさず率を併記し失敗試行は非合格。計画停止/起動直後/故障中/media全体転送時間はRD151の明示範囲だけ除外し別窓保存。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | OS/PG/API/Web/Artemis CPU/RSS/heap/direct/metaspace/thread/GC/FD/DBpool/lock/queue/disk/walを同窓で採取、設定上限内。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | instrumentation/DEBUG計測負荷付き窓を正式STANDARD値へ混在しない、raw値から都合の良い試行だけ採用0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-perf-002"></a>
## IT-PERF-002 20stream混在とScenario/DB上限

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

20stream混在とScenario/DB上限によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | 20stream混在とScenario/DB上限 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 45分、全raw latency/retentionを保全。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §13 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [342_Caddy・systemd・PostgreSQL・Java設定設計.md](<../../300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md>) §5/8 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "users": 10,
  "streams": 20,
  "range_bytes": 1048576,
  "scenario_records": 10000,
  "log_page": 100,
  "user_notification_question_page": 50,
  "measurement_minutes": 30
}
```

**操作順序・入口**

PERF001と同じ窓へ20Range stream/10000record SCNを重ね、各機能単独窓とも比較。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | Range開始応答と通常同期p95&lt;=2.5秒/MQ待ち&lt;=2.0秒、media全長完了をp95対象へ混ぜ0、最大stream20/21はRANGE020判定。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | SCN48000000byte/10000record、worst検索100/log100/新一覧50、最大wire&lt;=1000000byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | FD/thread/direct/heap/pool/lock/Query ID/planを実採取、N+1/無制限sortやstream完了時permit leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-perf-003"></a>
## IT-PERF-003 16GB/256GB資源予算

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

16GB/256GB資源予算によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-OPS |
| 確認契約 | 16GB/256GB資源予算 |
| 必要環境 | E-OPS |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 個別45分、backup組合せは1800秒の親deadline不変更。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [342_Caddy・systemd・PostgreSQL・Java設定設計.md](<../../300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md>) §5.1/8 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [321_Artemis物理構成・JMS設定設計.md](<../../300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md>) §3/5.3 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "RAM_GB": 16,
  "SSD_GB": [
    45,
    35,
    30,
    10,
    5,
    10,
    80,
    5,
    36
  ],
  "budget_RAM_GB": {
    "PG": 4,
    "Artemis": 2,
    "API": 2,
    "Web": 1.5,
    "OS_Caddy_cache": 3,
    "safety_DEBUG": 3.5
  }
}
```

**操作順序・入口**

通常/同期10/stream20/SCN10000/backup-cleanupの個別と許された組合せでresource peakを同窓測定。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 全16GB・SSD配分256GB内、Web MemoryMax1536M/API2048M/Batch1536M/Artemis2048M、heap/direct/metaspaceのSS342表値一致。 | O-UNIT, O-FILE, O-DB, O-TIME, O-MQ, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | Artemis journal/paging&lt;=10GiB予算、metadata/consumer buffer overhead別計測。DB WAL/temp、backup7世代80GB、DEBUG停止を確認。 | O-UNIT, O-FILE, O-DB, O-TIME, O-MQ, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | effective_cache_size6GBをallocationと二重計数0、native/thread/codecache headroomを0にせず過負荷時9001/ready制御・既受付保全。 | O-UNIT, O-FILE, O-DB, O-TIME, O-MQ, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

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
| 反復 | 1 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `8b91944df582`

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
| A02 | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 開始時warning=true、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A04 | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 開始時warning=true、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A06 | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A07 | 開始時warning=true、critical=true。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A08 | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A09 | 開始時warning=true、critical=true。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A10 | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：ISS-TRANSFER。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧5caseの値差を1familyへ統合。scan値/新規拒否/既受付非破壊を各入力行で追跡。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-010`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-010-s01"></a>
#### IT-PERF-010-S01 / 3499999999

種類：境界、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "root_bytes": 3499999999,
  "SCN_records": 201,
  "other_axis": "非支配:files<500/bytes<3.5GB"
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
| A02 | IT-PERF-010-S01/fs.jsonl, IT-PERF-010-S01/db.jsonl, IT-PERF-010-S01/wire.jsonl, IT-PERF-010-S01/metric.jsonl | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-010-s02"></a>
#### IT-PERF-010-S02 / 3500000000

種類：境界、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "root_bytes": 3500000000,
  "SCN_records": 201,
  "other_axis": "非支配:files<500/bytes<3.5GB"
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
| A04 | IT-PERF-010-S02/fs.jsonl, IT-PERF-010-S02/db.jsonl, IT-PERF-010-S02/wire.jsonl, IT-PERF-010-S02/metric.jsonl | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-010-s03"></a>
#### IT-PERF-010-S03 / 4499999999

種類：境界、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "root_bytes": 4499999999,
  "SCN_records": 201,
  "other_axis": "非支配:files<500/bytes<3.5GB"
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

種類：境界、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "root_bytes": 4500000000,
  "SCN_records": 201,
  "other_axis": "非支配:files<500/bytes<3.5GB"
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
| A08 | IT-PERF-010-S04/fs.jsonl, IT-PERF-010-S04/db.jsonl, IT-PERF-010-S04/wire.jsonl, IT-PERF-010-S04/metric.jsonl | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-010-s05"></a>
#### IT-PERF-010-S05 / 5000000000

種類：境界、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "root_bytes": 5000000000,
  "SCN_records": 201,
  "other_axis": "非支配:files<500/bytes<3.5GB"
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
| A10 | IT-PERF-010-S05/fs.jsonl, IT-PERF-010-S05/db.jsonl, IT-PERF-010-S05/wire.jsonl, IT-PERF-010-S05/metric.jsonl | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 |

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
| 反復 | 1 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 13. Capacity・metric・alert ／ 固定承認本文 ／ commit `8b91944df582`

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
| A02 | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 開始時warning=true、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A04 | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 開始時warning=true、critical=false。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A06 | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A07 | 開始時warning=true、critical=true。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A08 | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A09 | 開始時warning=true、critical=true。criticalなら9001/ready新規0。既存ready自動削除0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A10 | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 | O-FS, O-DB, O-WIRE, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：ISS-TRANSFER。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧5caseの値差を1familyへ統合。scan値/新規拒否/既受付非破壊を各入力行で追跡。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-020`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-020-s01"></a>
#### IT-PERF-020-S01 / 4999

種類：境界、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "root_count": 4999,
  "SCN_records": 201,
  "other_axis": "非支配:files<500/bytes<3.5GB"
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
| A02 | IT-PERF-020-S01/fs.jsonl, IT-PERF-020-S01/db.jsonl, IT-PERF-020-S01/wire.jsonl, IT-PERF-020-S01/metric.jsonl | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-020-s02"></a>
#### IT-PERF-020-S02 / 5000

種類：境界、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "root_count": 5000,
  "SCN_records": 201,
  "other_axis": "非支配:files<500/bytes<3.5GB"
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
| A04 | IT-PERF-020-S02/fs.jsonl, IT-PERF-020-S02/db.jsonl, IT-PERF-020-S02/wire.jsonl, IT-PERF-020-S02/metric.jsonl | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-020-s03"></a>
#### IT-PERF-020-S03 / 8999

種類：境界、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "root_count": 8999,
  "SCN_records": 201,
  "other_axis": "非支配:files<500/bytes<3.5GB"
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

種類：境界、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "root_count": 9000,
  "SCN_records": 201,
  "other_axis": "非支配:files<500/bytes<3.5GB"
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
| A08 | IT-PERF-020-S04/fs.jsonl, IT-PERF-020-S04/db.jsonl, IT-PERF-020-S04/wire.jsonl, IT-PERF-020-S04/metric.jsonl | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-perf-020-s05"></a>
#### IT-PERF-020-S05 / 10000

種類：境界、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "root_count": 10000,
  "SCN_records": 201,
  "other_axis": "非支配:files<500/bytes<3.5GB"
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
| A10 | IT-PERF-020-S05/fs.jsonl, IT-PERF-020-S05/db.jsonl, IT-PERF-020-S05/wire.jsonl, IT-PERF-020-S05/metric.jsonl | critical未満から要求分を加算して跨ぐ判定/同時予約の扱いはISS-TRANSFER解消前NOT_JUDGED。hard上限超過許可0。 |

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
| 反復 | 1 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > QA-050承認反映：再試行のPT・IT/STと間隔調整（2026-10-03） ／ ['QA-050'] ／ commit `8b91944df582`

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
| 反復 | 1 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `8b91944df582`

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

種類：競合、反復：2、状態：CONFIRMED/NOT_EXECUTED。

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
| 反復 | 1 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `8b91944df582`

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

種類：競合、反復：2、状態：CONFIRMED/NOT_EXECUTED。

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
| 反復 | 1 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 4. Large-result判定・レイアウト ／ 固定承認本文 ／ commit `8b91944df582`

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

種類：競合、反復：2、状態：CONFIRMED/NOT_EXECUTED。

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
| 反復 | 1 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `8b91944df582`

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
| 反復 | 1 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `8b91944df582`

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
| 反復 | 1 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) PT・IT試験観点詳細設計 > 5. IT詳細観点 > 5.5 IT-PERFORMANCE・CAPACITY ／ 固定承認本文 ／ commit `8b91944df582`
- [342_Caddy・systemd・PostgreSQL・Java設定設計.md](<../../300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md>) Caddy・systemd・PostgreSQL・Java設定設計 > 5. Java/JVM・Spring process > 5.1 Resource ／ 固定承認本文 ／ commit `8b91944df582`
- [341_朝batch・backup・削除・再実行設計.md](<../../300_SS/340_batch・基盤/341_朝batch・backup・削除・再実行設計.md>) 朝batch・backup・削除・再実行設計 ／ ['SSC278'] ／ commit `8b91944df582`

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

仕様：**PENDING_DECISION** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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
| 反復 | 1 |
| timeout・中断 | SC.waitを適用。通常SC watchdog120秒、運用SC1800秒。性能SCはload_planの有限窓＋後処理120秒。 |
| 副作用禁止 | SCの非更新条件を全field比較。秘密canaryを公開ログ/HTTP/証跡索引へ出さない。原失敗・未知のready・不明jobを削除しない。 |
| 観測方法 | SC別assertion_evidenceのfield predicateと独立readback。observerは別接続・別process、対象の計算関数/SQLをoracleに使わない。 |
| 判定式 | SCごと全assertion真かつ証跡欠落0。UNKNOWN/未確定oracle/到達未確認はPASS不可。 |
| 失敗保全 | 541/542継承。注入解除前に入力・ID・monotonic時刻・source・設定hash・DB/MQ/FS/Unit状態を保全。commit不明はread-only照合まで再実行禁止。 |
| 後片付け・再実行 | 予約namespaceのwriter停止→接続・lease・FD解放確認→隔離clone廃棄。公開ready/既存成功/UNKNOWNは削除せず保全。新attemptで再初期化し原結果を保持。 |
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) SQL・transaction・lock・削除設計 > 13. Query plan・性能確認 ／ 固定承認本文 ／ commit `8b91944df582`

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
| A01 | selective query全試行elapsedのceil(.95*N)番&lt;=1.5秒、stable order/count/list100。E2E&lt;=2.5秒とは別assertion。 | O-DB, O-WIRE, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | planの不要seq scanなしをpredicate/index/cardinalityと併せレビュー。query名だけから使用indexを推測0、trace対象関数から期待IDを計算0。 | O-DB, O-WIRE, O-METRIC, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：ISS-SELECTIVITY。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧IT-PERF-001のE2E2.5秒だけではSS332のSQL単独1.5秒条件を判定できない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-PERF-036`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-perf-036-s01"></a>
#### IT-PERF-036-S01 / query_plan

種類：正常、反復：2、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "entries": 99661,
  "page_size": 100,
  "filters": "選択性manifest固定、match100件・非match99561件",
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
| A01 | IT-PERF-036-S01/db.jsonl, IT-PERF-036-S01/wire.jsonl, IT-PERF-036-S01/metric.jsonl, IT-PERF-036-S01/time.jsonl | selective query全試行elapsedのceil(.95*N)番&lt;=1.5秒、stable order/count/list100。E2E&lt;=2.5秒とは別assertion。 |
| A02 | IT-PERF-036-S01/db.jsonl, IT-PERF-036-S01/wire.jsonl, IT-PERF-036-S01/metric.jsonl, IT-PERF-036-S01/time.jsonl | planの不要seq scanなしをpredicate/index/cardinalityと併せレビュー。query名だけから使用indexを推測0、trace対象関数から期待IDを計算0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。
