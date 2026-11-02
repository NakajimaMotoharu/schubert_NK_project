# ファイル・メディア・Range 結合テストケース

編集正本は [cases.json](../data/cases.json)。この巻は自動生成。全件NOT_EXECUTED。SUPERSEDEDは旧ID履歴。PENDING_REAUDITは具体シナリオ再監査待ちで、仕様確定・実行可能へ算入しない。

全ケースは [512](../510_方針・準備/512_結合構成・環境・データ.md) の経路・環境・fixture・観測・C-ISOLATE と [541](../540_実行・管理/541_Codex実行・判定・証跡・再開.md) を参照する。共通CP-BASEの入力以外の初期状態・証跡・中断・後片付けは cases.json.profiles に一元化し、個別追加条件と併せて必須とする。

他巻：[インターフェース](521_インターフェース.md) / [トランザクション・データ](522_トランザクション・データ.md) / [認証・権限・セキュリティ](523_認証・権限・セキュリティ.md) / [ファイル・メディア・Range](524_ファイル・メディア・Range.md) / [運用・復旧・監視](525_運用・復旧・監視.md) / [MQ・非同期・容量](526_MQ・非同期・容量.md) / [性能・資源・Logout混在](527_性能・資源・Logout混在.md)

<a id="it-file-001"></a>
## IT-FILE-001 Scenario音声展開後0recordの結合境界

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧record値だけのcaseを実展開入力/byte数/FS/最終認証まで具体化。既存IDは保持し新規追加数へ加算しない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Scenario音声展開後0recordの結合境界 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 4. Large-result判定・レイアウト ／ 固定承認本文 ／ commit `7147c428bb9d`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) SQL・transaction・lock・削除設計 > 4. Scenario・Speaker・Media query > 4.2 Scenario file/detail（IF-003/004） ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-001"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 存在する0entry Scenario fileはUI234§10.2によりSCNRSP01 I/record0/body1984byte。descriptorは未設定/0、Transfer生成0。対象file不存在0104とは別fixture。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 順序はentry_index/display_order/idとaudio link display_order/audio_file_id、DB ID大小を順序へ代用0。size/hash/各recordは独立4800byte表で比較。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | fileI/O中DBTX/rowlock0、最終write現在auth/owner/Inbox確認。終端FD/lock/poolはbefore、日中成功/失敗でready削除0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧record値だけのcaseを実展開入力/byte数/FS/最終認証まで具体化。既存IDは保持し新規追加数へ加算しない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-001`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-001-s01"></a>
#### IT-FILE-001-S01 / 0

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entry": "SCN明細：fixture script_file SF1",
  "expanded_records": 0,
  "fixture": "count<=200はnentry各音声0、201はentry1にvoice2＋entry2..200音声1で計201",
  "record_order": "EntrySeq1開始/同entryAudioSeq1開始、音声なし0",
  "record_bytes": 4800,
  "body_literal": "IT本文<entry_no>、他metadataは独立UI234 field表"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実master fixtureを独立順序表へ固定→BrowserのSCN要求→DB snapshot→inline又は実Transfer→Web decode/表示。201以上はreadTX終了とI/O後final verifyを観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-001-S01/http.jsonl, IT-FILE-001-S01/wire.jsonl, IT-FILE-001-S01/db.jsonl, IT-FILE-001-S01/fs.jsonl, IT-FILE-001-S01/lock.jsonl, IT-FILE-001-S01/time.jsonl | 存在する0entry Scenario fileはUI234§10.2によりSCNRSP01 I/record0/body1984byte。descriptorは未設定/0、Transfer生成0。対象file不存在0104とは別fixture。 |
| A02 | IT-FILE-001-S01/http.jsonl, IT-FILE-001-S01/wire.jsonl, IT-FILE-001-S01/db.jsonl, IT-FILE-001-S01/fs.jsonl, IT-FILE-001-S01/lock.jsonl, IT-FILE-001-S01/time.jsonl | 順序はentry_index/display_order/idとaudio link display_order/audio_file_id、DB ID大小を順序へ代用0。size/hash/各recordは独立4800byte表で比較。 |
| A03 | IT-FILE-001-S01/http.jsonl, IT-FILE-001-S01/wire.jsonl, IT-FILE-001-S01/db.jsonl, IT-FILE-001-S01/fs.jsonl, IT-FILE-001-S01/lock.jsonl, IT-FILE-001-S01/time.jsonl | fileI/O中DBTX/rowlock0、最終write現在auth/owner/Inbox確認。終端FD/lock/poolはbefore、日中成功/失敗でready削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-002"></a>
## IT-FILE-002 Scenario音声展開後1recordの結合境界

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧record値だけのcaseを実展開入力/byte数/FS/最終認証まで具体化。既存IDは保持し新規追加数へ加算しない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Scenario音声展開後1recordの結合境界 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 4. Large-result判定・レイアウト ／ 固定承認本文 ／ commit `7147c428bb9d`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) SQL・transaction・lock・削除設計 > 4. Scenario・Speaker・Media query > 4.2 Scenario file/detail（IF-003/004） ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-002"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | SCNRSP01 modeI/records1/body6784byte、descriptor未設定、Transfer公開0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 順序はentry_index/display_order/idとaudio link display_order/audio_file_id、DB ID大小を順序へ代用0。size/hash/各recordは独立4800byte表で比較。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | fileI/O中DBTX/rowlock0、最終write現在auth/owner/Inbox確認。終端FD/lock/poolはbefore、日中成功/失敗でready削除0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧record値だけのcaseを実展開入力/byte数/FS/最終認証まで具体化。既存IDは保持し新規追加数へ加算しない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-002`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-002-s01"></a>
#### IT-FILE-002-S01 / 1

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entry": "SCN明細：fixture script_file SF1",
  "expanded_records": 1,
  "fixture": "count<=200はnentry各音声0、201はentry1にvoice2＋entry2..200音声1で計201",
  "record_order": "EntrySeq1開始/同entryAudioSeq1開始、音声なし0",
  "record_bytes": 4800,
  "body_literal": "IT本文<entry_no>、他metadataは独立UI234 field表"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実master fixtureを独立順序表へ固定→BrowserのSCN要求→DB snapshot→inline又は実Transfer→Web decode/表示。201以上はreadTX終了とI/O後final verifyを観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-002-S01/http.jsonl, IT-FILE-002-S01/wire.jsonl, IT-FILE-002-S01/db.jsonl, IT-FILE-002-S01/fs.jsonl, IT-FILE-002-S01/lock.jsonl, IT-FILE-002-S01/time.jsonl | SCNRSP01 modeI/records1/body6784byte、descriptor未設定、Transfer公開0。 |
| A02 | IT-FILE-002-S01/http.jsonl, IT-FILE-002-S01/wire.jsonl, IT-FILE-002-S01/db.jsonl, IT-FILE-002-S01/fs.jsonl, IT-FILE-002-S01/lock.jsonl, IT-FILE-002-S01/time.jsonl | 順序はentry_index/display_order/idとaudio link display_order/audio_file_id、DB ID大小を順序へ代用0。size/hash/各recordは独立4800byte表で比較。 |
| A03 | IT-FILE-002-S01/http.jsonl, IT-FILE-002-S01/wire.jsonl, IT-FILE-002-S01/db.jsonl, IT-FILE-002-S01/fs.jsonl, IT-FILE-002-S01/lock.jsonl, IT-FILE-002-S01/time.jsonl | fileI/O中DBTX/rowlock0、最終write現在auth/owner/Inbox確認。終端FD/lock/poolはbefore、日中成功/失敗でready削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-003"></a>
## IT-FILE-003 Scenario音声展開後200recordの結合境界

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧record値だけのcaseを実展開入力/byte数/FS/最終認証まで具体化。既存IDは保持し新規追加数へ加算しない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Scenario音声展開後200recordの結合境界 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 4. Large-result判定・レイアウト ／ 固定承認本文 ／ commit `7147c428bb9d`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) SQL・transaction・lock・削除設計 > 4. Scenario・Speaker・Media query > 4.2 Scenario file/detail（IF-003/004） ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-003"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | SCNRSP01 modeI/records200/body961984byte、descriptor未設定、Transfer公開0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 順序はentry_index/display_order/idとaudio link display_order/audio_file_id、DB ID大小を順序へ代用0。size/hash/各recordは独立4800byte表で比較。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | fileI/O中DBTX/rowlock0、最終write現在auth/owner/Inbox確認。終端FD/lock/poolはbefore、日中成功/失敗でready削除0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧record値だけのcaseを実展開入力/byte数/FS/最終認証まで具体化。既存IDは保持し新規追加数へ加算しない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-003`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-003-s01"></a>
#### IT-FILE-003-S01 / 200

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entry": "SCN明細：fixture script_file SF1",
  "expanded_records": 200,
  "fixture": "count<=200はnentry各音声0、201はentry1にvoice2＋entry2..200音声1で計201",
  "record_order": "EntrySeq1開始/同entryAudioSeq1開始、音声なし0",
  "record_bytes": 4800,
  "body_literal": "IT本文<entry_no>、他metadataは独立UI234 field表"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実master fixtureを独立順序表へ固定→BrowserのSCN要求→DB snapshot→inline又は実Transfer→Web decode/表示。201以上はreadTX終了とI/O後final verifyを観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-003-S01/http.jsonl, IT-FILE-003-S01/wire.jsonl, IT-FILE-003-S01/db.jsonl, IT-FILE-003-S01/fs.jsonl, IT-FILE-003-S01/lock.jsonl, IT-FILE-003-S01/time.jsonl | SCNRSP01 modeI/records200/body961984byte、descriptor未設定、Transfer公開0。 |
| A02 | IT-FILE-003-S01/http.jsonl, IT-FILE-003-S01/wire.jsonl, IT-FILE-003-S01/db.jsonl, IT-FILE-003-S01/fs.jsonl, IT-FILE-003-S01/lock.jsonl, IT-FILE-003-S01/time.jsonl | 順序はentry_index/display_order/idとaudio link display_order/audio_file_id、DB ID大小を順序へ代用0。size/hash/各recordは独立4800byte表で比較。 |
| A03 | IT-FILE-003-S01/http.jsonl, IT-FILE-003-S01/wire.jsonl, IT-FILE-003-S01/db.jsonl, IT-FILE-003-S01/fs.jsonl, IT-FILE-003-S01/lock.jsonl, IT-FILE-003-S01/time.jsonl | fileI/O中DBTX/rowlock0、最終write現在auth/owner/Inbox確認。終端FD/lock/poolはbefore、日中成功/失敗でready削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-004"></a>
## IT-FILE-004 Scenario音声展開後201recordの結合境界

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧record値だけのcaseを実展開入力/byte数/FS/最終認証まで具体化。既存IDは保持し新規追加数へ加算しない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Scenario音声展開後201recordの結合境界 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 4. Large-result判定・レイアウト ／ 固定承認本文 ／ commit `7147c428bb9d`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) SQL・transaction・lock・削除設計 > 4. Scenario・Speaker・Media query > 4.2 Scenario file/detail（IF-003/004） ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-004"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | SCNRSP01 modeF/inline0/body1984byte、ready1/size964800byte/count201、header/BOM/newline無し。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 順序はentry_index/display_order/idとaudio link display_order/audio_file_id、DB ID大小を順序へ代用0。size/hash/各recordは独立4800byte表で比較。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | fileI/O中DBTX/rowlock0、最終write現在auth/owner/Inbox確認。終端FD/lock/poolはbefore、日中成功/失敗でready削除0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧record値だけのcaseを実展開入力/byte数/FS/最終認証まで具体化。既存IDは保持し新規追加数へ加算しない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-004`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-004-s01"></a>
#### IT-FILE-004-S01 / 201

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entry": "SCN明細：fixture script_file SF1",
  "expanded_records": 201,
  "fixture": "count<=200はnentry各音声0、201はentry1にvoice2＋entry2..200音声1で計201",
  "record_order": "EntrySeq1開始/同entryAudioSeq1開始、音声なし0",
  "record_bytes": 4800,
  "body_literal": "IT本文<entry_no>、他metadataは独立UI234 field表"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実master fixtureを独立順序表へ固定→BrowserのSCN要求→DB snapshot→inline又は実Transfer→Web decode/表示。201以上はreadTX終了とI/O後final verifyを観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-004-S01/http.jsonl, IT-FILE-004-S01/wire.jsonl, IT-FILE-004-S01/db.jsonl, IT-FILE-004-S01/fs.jsonl, IT-FILE-004-S01/lock.jsonl, IT-FILE-004-S01/time.jsonl | SCNRSP01 modeF/inline0/body1984byte、ready1/size964800byte/count201、header/BOM/newline無し。 |
| A02 | IT-FILE-004-S01/http.jsonl, IT-FILE-004-S01/wire.jsonl, IT-FILE-004-S01/db.jsonl, IT-FILE-004-S01/fs.jsonl, IT-FILE-004-S01/lock.jsonl, IT-FILE-004-S01/time.jsonl | 順序はentry_index/display_order/idとaudio link display_order/audio_file_id、DB ID大小を順序へ代用0。size/hash/各recordは独立4800byte表で比較。 |
| A03 | IT-FILE-004-S01/http.jsonl, IT-FILE-004-S01/wire.jsonl, IT-FILE-004-S01/db.jsonl, IT-FILE-004-S01/fs.jsonl, IT-FILE-004-S01/lock.jsonl, IT-FILE-004-S01/time.jsonl | fileI/O中DBTX/rowlock0、最終write現在auth/owner/Inbox確認。終端FD/lock/poolはbefore、日中成功/失敗でready削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-005"></a>
## IT-FILE-005 Scenario音声展開後10000recordの結合境界

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧record値だけのcaseを実展開入力/byte数/FS/最終認証まで具体化。既存IDは保持し新規追加数へ加算しない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Scenario音声展開後10000recordの結合境界 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 4. Large-result判定・レイアウト ／ 固定承認本文 ／ commit `7147c428bb9d`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) SQL・transaction・lock・削除設計 > 4. Scenario・Speaker・Media query > 4.2 Scenario file/detail（IF-003/004） ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-005"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | SCNRSP01 modeF/inline0/body1984byte、ready1/size48000000byte/count10000、header/BOM/newline無し。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 順序はentry_index/display_order/idとaudio link display_order/audio_file_id、DB ID大小を順序へ代用0。size/hash/各recordは独立4800byte表で比較。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | fileI/O中DBTX/rowlock0、最終write現在auth/owner/Inbox確認。終端FD/lock/poolはbefore、日中成功/失敗でready削除0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧record値だけのcaseを実展開入力/byte数/FS/最終認証まで具体化。既存IDは保持し新規追加数へ加算しない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-005`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-005-s01"></a>
#### IT-FILE-005-S01 / 10000

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entry": "SCN明細：fixture script_file SF1",
  "expanded_records": 10000,
  "fixture": "entry1..5000の各voice2、展開後10000record/各4800byte",
  "record_order": "EntrySeq1開始/同entryAudioSeq1開始、音声なし0",
  "record_bytes": 4800,
  "body_literal": "IT本文<entry_no>、他metadataは独立UI234 field表"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実master fixtureを独立順序表へ固定→BrowserのSCN要求→DB snapshot→inline又は実Transfer→Web decode/表示。201以上はreadTX終了とI/O後final verifyを観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-005-S01/http.jsonl, IT-FILE-005-S01/wire.jsonl, IT-FILE-005-S01/db.jsonl, IT-FILE-005-S01/fs.jsonl, IT-FILE-005-S01/lock.jsonl, IT-FILE-005-S01/time.jsonl | SCNRSP01 modeF/inline0/body1984byte、ready1/size48000000byte/count10000、header/BOM/newline無し。 |
| A02 | IT-FILE-005-S01/http.jsonl, IT-FILE-005-S01/wire.jsonl, IT-FILE-005-S01/db.jsonl, IT-FILE-005-S01/fs.jsonl, IT-FILE-005-S01/lock.jsonl, IT-FILE-005-S01/time.jsonl | 順序はentry_index/display_order/idとaudio link display_order/audio_file_id、DB ID大小を順序へ代用0。size/hash/各recordは独立4800byte表で比較。 |
| A03 | IT-FILE-005-S01/http.jsonl, IT-FILE-005-S01/wire.jsonl, IT-FILE-005-S01/db.jsonl, IT-FILE-005-S01/fs.jsonl, IT-FILE-005-S01/lock.jsonl, IT-FILE-005-S01/time.jsonl | fileI/O中DBTX/rowlock0、最終write現在auth/owner/Inbox確認。終端FD/lock/poolはbefore、日中成功/失敗でready削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-006"></a>
## IT-FILE-006 Scenario音声展開後10001recordの結合境界

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧record値だけのcaseを実展開入力/byte数/FS/最終認証まで具体化。既存IDは保持し新規追加数へ加算しない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Scenario音声展開後10001recordの結合境界 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 4. Large-result判定・レイアウト ／ 固定承認本文 ／ commit `7147c428bb9d`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) SQL・transaction・lock・削除設計 > 4. Scenario・Speaker・Media query > 4.2 Scenario file/detail（IF-003/004） ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-006"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 9001/HTTP503、部分成功record/descriptor0、ready公開0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 順序はentry_index/display_order/idとaudio link display_order/audio_file_id、DB ID大小を順序へ代用0。size/hash/各recordは独立4800byte表で比較。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | fileI/O中DBTX/rowlock0、最終write現在auth/owner/Inbox確認。終端FD/lock/poolはbefore、日中成功/失敗でready削除0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧record値だけのcaseを実展開入力/byte数/FS/最終認証まで具体化。既存IDは保持し新規追加数へ加算しない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-006`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-006-s01"></a>
#### IT-FILE-006-S01 / 10001

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entry": "SCN明細：fixture script_file SF1",
  "expanded_records": 10001,
  "fixture": "entry1..5000の各voice2＋entry5001音声なし1で展開10001",
  "record_order": "EntrySeq1開始/同entryAudioSeq1開始、音声なし0",
  "record_bytes": 4800,
  "body_literal": "IT本文<entry_no>、他metadataは独立UI234 field表"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実master fixtureを独立順序表へ固定→BrowserのSCN要求→DB snapshot→inline又は実Transfer→Web decode/表示。201以上はreadTX終了とI/O後final verifyを観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-006-S01/http.jsonl, IT-FILE-006-S01/wire.jsonl, IT-FILE-006-S01/db.jsonl, IT-FILE-006-S01/fs.jsonl, IT-FILE-006-S01/lock.jsonl, IT-FILE-006-S01/time.jsonl | 9001/HTTP503、部分成功record/descriptor0、ready公開0。 |
| A02 | IT-FILE-006-S01/http.jsonl, IT-FILE-006-S01/wire.jsonl, IT-FILE-006-S01/db.jsonl, IT-FILE-006-S01/fs.jsonl, IT-FILE-006-S01/lock.jsonl, IT-FILE-006-S01/time.jsonl | 順序はentry_index/display_order/idとaudio link display_order/audio_file_id、DB ID大小を順序へ代用0。size/hash/各recordは独立4800byte表で比較。 |
| A03 | IT-FILE-006-S01/http.jsonl, IT-FILE-006-S01/wire.jsonl, IT-FILE-006-S01/db.jsonl, IT-FILE-006-S01/fs.jsonl, IT-FILE-006-S01/lock.jsonl, IT-FILE-006-S01/time.jsonl | fileI/O中DBTX/rowlock0、最終write現在auth/owner/Inbox確認。終端FD/lock/poolはbefore、日中成功/失敗でready削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-010"></a>
## IT-FILE-010 Large-result record2のwrite失敗の所有後条件

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧公開前/後の同一assertionを、未公開part清掃と公開済ready保全の異なる後条件へ具体化。collisionは新FILE062へ分離。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Large-result record2のwrite失敗の所有後条件 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 5. Large-result生成algorithm ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（1件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-010"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 公開前失敗503/一時型、owned partだけbest-effort清掃。清掃失敗はsecondaryを非秘密保全、元障害で隠さない。ready新規0。 | O-HTTP, O-DB, O-WIRE, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 既存U0と他part/readyは不変、root自動修復/追加権限0。元close/commit不明を解放/未実行へ補完0。 | O-HTTP, O-DB, O-WIRE, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 再実行は原入力/failed attemptを保持して新attempt。公開済なら同tokenの保存状態/現在file/元snapshotを照合してから復旧、無条件新file生成0。 | O-HTTP, O-DB, O-WIRE, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧公開前/後の同一assertionを、未公開part清掃と公開済ready保全の異なる後条件へ具体化。collisionは新FILE062へ分離。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-010`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-010-s01"></a>
#### IT-FILE-010-S01 / io_fail

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN_records": 201,
  "expected_bytes": 964800,
  "failpoint": "record2のwrite",
  "unrelated_file": "U0 before inode/hash"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：record2のwrite一回failure。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実SCNをrecord2のwriteへ進め、一回I/O/構築失敗。DB/MQ/FS/HTTP/ownedFDを採取して原失敗を保全。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-010-S01/http.jsonl, IT-FILE-010-S01/db.jsonl, IT-FILE-010-S01/wire.jsonl, IT-FILE-010-S01/fs.jsonl, IT-FILE-010-S01/os.jsonl, IT-FILE-010-S01/log.jsonl | 公開前失敗503/一時型、owned partだけbest-effort清掃。清掃失敗はsecondaryを非秘密保全、元障害で隠さない。ready新規0。 |
| A02 | IT-FILE-010-S01/http.jsonl, IT-FILE-010-S01/db.jsonl, IT-FILE-010-S01/wire.jsonl, IT-FILE-010-S01/fs.jsonl, IT-FILE-010-S01/os.jsonl, IT-FILE-010-S01/log.jsonl | 既存U0と他part/readyは不変、root自動修復/追加権限0。元close/commit不明を解放/未実行へ補完0。 |
| A03 | IT-FILE-010-S01/http.jsonl, IT-FILE-010-S01/db.jsonl, IT-FILE-010-S01/wire.jsonl, IT-FILE-010-S01/fs.jsonl, IT-FILE-010-S01/os.jsonl, IT-FILE-010-S01/log.jsonl | 再実行は原入力/failed attemptを保持して新attempt。公開済なら同tokenの保存状態/現在file/元snapshotを照合してから復旧、無条件新file生成0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-011"></a>
## IT-FILE-011 Large-result 全recordwrite後FileChannel.force(true)失敗の所有後条件

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧公開前/後の同一assertionを、未公開part清掃と公開済ready保全の異なる後条件へ具体化。collisionは新FILE062へ分離。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Large-result 全recordwrite後FileChannel.force(true)失敗の所有後条件 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 5. Large-result生成algorithm ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（1件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-011"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 公開前失敗503/一時型、owned partだけbest-effort清掃。清掃失敗はsecondaryを非秘密保全、元障害で隠さない。ready新規0。 | O-HTTP, O-DB, O-WIRE, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 既存U0と他part/readyは不変、root自動修復/追加権限0。元close/commit不明を解放/未実行へ補完0。 | O-HTTP, O-DB, O-WIRE, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 再実行は原入力/failed attemptを保持して新attempt。公開済なら同tokenの保存状態/現在file/元snapshotを照合してから復旧、無条件新file生成0。 | O-HTTP, O-DB, O-WIRE, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧公開前/後の同一assertionを、未公開part清掃と公開済ready保全の異なる後条件へ具体化。collisionは新FILE062へ分離。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-011`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-011-s01"></a>
#### IT-FILE-011-S01 / io_fail

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN_records": 201,
  "expected_bytes": 964800,
  "failpoint": "全recordwrite後FileChannel.force(true)",
  "unrelated_file": "U0 before inode/hash"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：全recordwrite後FileChannel.force(true)一回failure。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実SCNを全recordwrite後FileChannel.force(true)へ進め、一回I/O/構築失敗。DB/MQ/FS/HTTP/ownedFDを採取して原失敗を保全。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-011-S01/http.jsonl, IT-FILE-011-S01/db.jsonl, IT-FILE-011-S01/wire.jsonl, IT-FILE-011-S01/fs.jsonl, IT-FILE-011-S01/os.jsonl, IT-FILE-011-S01/log.jsonl | 公開前失敗503/一時型、owned partだけbest-effort清掃。清掃失敗はsecondaryを非秘密保全、元障害で隠さない。ready新規0。 |
| A02 | IT-FILE-011-S01/http.jsonl, IT-FILE-011-S01/db.jsonl, IT-FILE-011-S01/wire.jsonl, IT-FILE-011-S01/fs.jsonl, IT-FILE-011-S01/os.jsonl, IT-FILE-011-S01/log.jsonl | 既存U0と他part/readyは不変、root自動修復/追加権限0。元close/commit不明を解放/未実行へ補完0。 |
| A03 | IT-FILE-011-S01/http.jsonl, IT-FILE-011-S01/db.jsonl, IT-FILE-011-S01/wire.jsonl, IT-FILE-011-S01/fs.jsonl, IT-FILE-011-S01/os.jsonl, IT-FILE-011-S01/log.jsonl | 再実行は原入力/failed attemptを保持して新attempt。公開済なら同tokenの保存状態/現在file/元snapshotを照合してから復旧、無条件新file生成0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-012"></a>
## IT-FILE-012 Large-result renameat2公開成功後response構築失敗の所有後条件

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧公開前/後の同一assertionを、未公開part清掃と公開済ready保全の異なる後条件へ具体化。collisionは新FILE062へ分離。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Large-result renameat2公開成功後response構築失敗の所有後条件 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 5. Large-result生成algorithm ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（1件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-012"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 公開済readyは964800byte/hashとinodeを保全、delete/逆rename0。response失敗を成功descriptor/ACKにしない。 | O-HTTP, O-DB, O-WIRE, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 既存U0と他part/readyは不変、root自動修復/追加権限0。元close/commit不明を解放/未実行へ補完0。 | O-HTTP, O-DB, O-WIRE, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 再実行は原入力/failed attemptを保持して新attempt。公開済なら同tokenの保存状態/現在file/元snapshotを照合してから復旧、無条件新file生成0。 | O-HTTP, O-DB, O-WIRE, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧公開前/後の同一assertionを、未公開part清掃と公開済ready保全の異なる後条件へ具体化。collisionは新FILE062へ分離。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-012`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-012-s01"></a>
#### IT-FILE-012-S01 / io_fail

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN_records": 201,
  "expected_bytes": 964800,
  "failpoint": "renameat2公開成功後response構築",
  "unrelated_file": "U0 before inode/hash"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：renameat2公開成功後response構築一回failure。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実SCNをrenameat2公開成功後response構築へ進め、一回I/O/構築失敗。DB/MQ/FS/HTTP/ownedFDを採取して原失敗を保全。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-012-S01/http.jsonl, IT-FILE-012-S01/db.jsonl, IT-FILE-012-S01/wire.jsonl, IT-FILE-012-S01/fs.jsonl, IT-FILE-012-S01/os.jsonl, IT-FILE-012-S01/log.jsonl | 公開済readyは964800byte/hashとinodeを保全、delete/逆rename0。response失敗を成功descriptor/ACKにしない。 |
| A02 | IT-FILE-012-S01/http.jsonl, IT-FILE-012-S01/db.jsonl, IT-FILE-012-S01/wire.jsonl, IT-FILE-012-S01/fs.jsonl, IT-FILE-012-S01/os.jsonl, IT-FILE-012-S01/log.jsonl | 既存U0と他part/readyは不変、root自動修復/追加権限0。元close/commit不明を解放/未実行へ補完0。 |
| A03 | IT-FILE-012-S01/http.jsonl, IT-FILE-012-S01/db.jsonl, IT-FILE-012-S01/wire.jsonl, IT-FILE-012-S01/fs.jsonl, IT-FILE-012-S01/os.jsonl, IT-FILE-012-S01/log.jsonl | 再実行は原入力/failed attemptを保持して新attempt。公開済なら同tokenの保存状態/現在file/元snapshotを照合してから復旧、無条件新file生成0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-020"></a>
## IT-FILE-020 descriptor.size変異の到達点と非露出

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor.size変異の到達点と非露出 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-020"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 | O-HTTP, O-WIRE, O-DB, O-FS。実測/path/SHA/判定式はattemptへ記録 |
| A02 | descriptor byte長がrecordLength×countと一致せず、Web取得検証はHTTP503/FILE_DESCRIPTOR_INVALID、stream/DOMrecord0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-020`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-020-s01"></a>
#### IT-FILE-020-S01 / positive_control

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN": "201record/964800byte",
  "descriptor": "全field正常",
  "filesystem": "保持root/date/entry正常 regular0640/nlink1"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実APIresponseを実broker/Web/FSへ通して独立201record表を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-020-S01/http.jsonl, IT-FILE-020-S01/wire.jsonl, IT-FILE-020-S01/db.jsonl, IT-FILE-020-S01/fs.jsonl | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-020-s02"></a>
#### IT-FILE-020-S02 / one_mutation

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "baseline": "positive_controlの新独立clone",
  "after_startup_mutation": {
    "descriptor.size": 964801
  },
  "expected_stage": "descriptor arithmetic before FS",
  "wire_source": "実API資格の隔離reply driver、属性/長さ/context/correlationは指定以外合法"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：descriptor.size one mutation。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 通常startup/認証後、指定1変異をdescriptor arithmetic before FSへ届くよう配置。record順変異はhash正当を先に保証しhash失敗で代用しない。実Webbroker受信→FS→表示を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-020-S02/http.jsonl, IT-FILE-020-S02/wire.jsonl, IT-FILE-020-S02/db.jsonl, IT-FILE-020-S02/fs.jsonl, IT-FILE-020-S02/os.jsonl, IT-FILE-020-S02/log.jsonl | descriptor byte長がrecordLength×countと一致せず、Web取得検証はHTTP503/FILE_DESCRIPTOR_INVALID、stream/DOMrecord0。 |
| A03 | IT-FILE-020-S02/http.jsonl, IT-FILE-020-S02/wire.jsonl, IT-FILE-020-S02/db.jsonl, IT-FILE-020-S02/fs.jsonl, IT-FILE-020-S02/os.jsonl, IT-FILE-020-S02/log.jsonl | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 |
| A04 | IT-FILE-020-S02/http.jsonl, IT-FILE-020-S02/wire.jsonl, IT-FILE-020-S02/db.jsonl, IT-FILE-020-S02/fs.jsonl, IT-FILE-020-S02/os.jsonl, IT-FILE-020-S02/log.jsonl | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-021"></a>
## IT-FILE-021 descriptor.hash変異の到達点と非露出

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor.hash変異の到達点と非露出 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-021"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 | O-HTTP, O-WIRE, O-DB, O-FS。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 503/FILE_INTEGRITY_MISMATCH分類、成功ViewModel/不正本文DOM表示0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-021`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-021-s01"></a>
#### IT-FILE-021-S01 / positive_control

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN": "201record/964800byte",
  "descriptor": "全field正常",
  "filesystem": "保持root/date/entry正常 regular0640/nlink1"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実APIresponseを実broker/Web/FSへ通して独立201record表を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-021-S01/http.jsonl, IT-FILE-021-S01/wire.jsonl, IT-FILE-021-S01/db.jsonl, IT-FILE-021-S01/fs.jsonl | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-021-s02"></a>
#### IT-FILE-021-S02 / one_mutation

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "baseline": "positive_controlの新独立clone",
  "after_startup_mutation": {
    "descriptor.hash": "元64hexの先頭1桁だけ変更"
  },
  "expected_stage": "保持inode hash read後",
  "wire_source": "実API資格の隔離reply driver、属性/長さ/context/correlationは指定以外合法"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：descriptor.hash one mutation。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 通常startup/認証後、指定1変異を保持inode hash read後へ届くよう配置。record順変異はhash正当を先に保証しhash失敗で代用しない。実Webbroker受信→FS→表示を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-021-S02/http.jsonl, IT-FILE-021-S02/wire.jsonl, IT-FILE-021-S02/db.jsonl, IT-FILE-021-S02/fs.jsonl, IT-FILE-021-S02/os.jsonl, IT-FILE-021-S02/log.jsonl | 503/FILE_INTEGRITY_MISMATCH分類、成功ViewModel/不正本文DOM表示0。 |
| A03 | IT-FILE-021-S02/http.jsonl, IT-FILE-021-S02/wire.jsonl, IT-FILE-021-S02/db.jsonl, IT-FILE-021-S02/fs.jsonl, IT-FILE-021-S02/os.jsonl, IT-FILE-021-S02/log.jsonl | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 |
| A04 | IT-FILE-021-S02/http.jsonl, IT-FILE-021-S02/wire.jsonl, IT-FILE-021-S02/db.jsonl, IT-FILE-021-S02/fs.jsonl, IT-FILE-021-S02/os.jsonl, IT-FILE-021-S02/log.jsonl | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-022"></a>
## IT-FILE-022 descriptor.path変異の到達点と非露出

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor.path変異の到達点と非露出 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-022"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 | O-HTTP, O-WIRE, O-DB, O-FS。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 共通X文字列としてdecode可能な../outside.readyをWeb論理path検証が拒否しHTTP503/FILE_DESCRIPTOR_INVALID。outside inode open0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-022`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-022-s01"></a>
#### IT-FILE-022-S01 / positive_control

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN": "201record/964800byte",
  "descriptor": "全field正常",
  "filesystem": "保持root/date/entry正常 regular0640/nlink1"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実APIresponseを実broker/Web/FSへ通して独立201record表を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-022-S01/http.jsonl, IT-FILE-022-S01/wire.jsonl, IT-FILE-022-S01/db.jsonl, IT-FILE-022-S01/fs.jsonl | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-022-s02"></a>
#### IT-FILE-022-S02 / one_mutation

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "baseline": "positive_controlの新独立clone",
  "after_startup_mutation": {
    "descriptor.path": "../outside.ready"
  },
  "expected_stage": "path grammar before FS",
  "wire_source": "実API資格の隔離reply driver、属性/長さ/context/correlationは指定以外合法"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：descriptor.path one mutation。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 通常startup/認証後、指定1変異をpath grammar before FSへ届くよう配置。record順変異はhash正当を先に保証しhash失敗で代用しない。実Webbroker受信→FS→表示を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-022-S02/http.jsonl, IT-FILE-022-S02/wire.jsonl, IT-FILE-022-S02/db.jsonl, IT-FILE-022-S02/fs.jsonl, IT-FILE-022-S02/os.jsonl, IT-FILE-022-S02/log.jsonl | 共通X文字列としてdecode可能な../outside.readyをWeb論理path検証が拒否しHTTP503/FILE_DESCRIPTOR_INVALID。outside inode open0。 |
| A03 | IT-FILE-022-S02/http.jsonl, IT-FILE-022-S02/wire.jsonl, IT-FILE-022-S02/db.jsonl, IT-FILE-022-S02/fs.jsonl, IT-FILE-022-S02/os.jsonl, IT-FILE-022-S02/log.jsonl | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 |
| A04 | IT-FILE-022-S02/http.jsonl, IT-FILE-022-S02/wire.jsonl, IT-FILE-022-S02/db.jsonl, IT-FILE-022-S02/fs.jsonl, IT-FILE-022-S02/os.jsonl, IT-FILE-022-S02/log.jsonl | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-023"></a>
## IT-FILE-023 descriptor.UUID変異の到達点と非露出

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor.UUID変異の到達点と非露出 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-023"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 | O-HTTP, O-WIRE, O-DB, O-FS。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 双方canonicalUUIDでもpath内IDとFileIDの不一致をWebdescriptor検証が拒否しHTTP503/FILE_DESCRIPTOR_INVALID。FS内容open0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-023`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-023-s01"></a>
#### IT-FILE-023-S01 / positive_control

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN": "201record/964800byte",
  "descriptor": "全field正常",
  "filesystem": "保持root/date/entry正常 regular0640/nlink1"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実APIresponseを実broker/Web/FSへ通して独立201record表を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-023-S01/http.jsonl, IT-FILE-023-S01/wire.jsonl, IT-FILE-023-S01/db.jsonl, IT-FILE-023-S01/fs.jsonl | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-023-s02"></a>
#### IT-FILE-023-S02 / one_mutation

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "baseline": "positive_controlの新独立clone",
  "after_startup_mutation": {
    "descriptor.UUID": "path内UUIDと別のcanonicalUUID"
  },
  "expected_stage": "descriptor cross-field before FS",
  "wire_source": "実API資格の隔離reply driver、属性/長さ/context/correlationは指定以外合法"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：descriptor.UUID one mutation。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 通常startup/認証後、指定1変異をdescriptor cross-field before FSへ届くよう配置。record順変異はhash正当を先に保証しhash失敗で代用しない。実Webbroker受信→FS→表示を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-023-S02/http.jsonl, IT-FILE-023-S02/wire.jsonl, IT-FILE-023-S02/db.jsonl, IT-FILE-023-S02/fs.jsonl, IT-FILE-023-S02/os.jsonl, IT-FILE-023-S02/log.jsonl | 双方canonicalUUIDでもpath内IDとFileIDの不一致をWebdescriptor検証が拒否しHTTP503/FILE_DESCRIPTOR_INVALID。FS内容open0。 |
| A03 | IT-FILE-023-S02/http.jsonl, IT-FILE-023-S02/wire.jsonl, IT-FILE-023-S02/db.jsonl, IT-FILE-023-S02/fs.jsonl, IT-FILE-023-S02/os.jsonl, IT-FILE-023-S02/log.jsonl | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 |
| A04 | IT-FILE-023-S02/http.jsonl, IT-FILE-023-S02/wire.jsonl, IT-FILE-023-S02/db.jsonl, IT-FILE-023-S02/fs.jsonl, IT-FILE-023-S02/os.jsonl, IT-FILE-023-S02/log.jsonl | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-024"></a>
## IT-FILE-024 descriptor.recordLength変異の到達点と非露出

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor.recordLength変異の到達点と非露出 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-024"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 | O-HTTP, O-WIRE, O-DB, O-FS。実測/path/SHA/判定式はattemptへ記録 |
| A02 | UI234 FのFile record長は004800固定。4799は共通codecのsemantic検証で恒久protocolerror、SS322/SS321のWebreply隔離・ACK後非0停止、正常descriptor/stream0。HTTP安全終端は既timeout/503、成功HTTP200応答は0件。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-024`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-024-s01"></a>
#### IT-FILE-024-S01 / positive_control

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN": "201record/964800byte",
  "descriptor": "全field正常",
  "filesystem": "保持root/date/entry正常 regular0640/nlink1"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実APIresponseを実broker/Web/FSへ通して独立201record表を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-024-S01/http.jsonl, IT-FILE-024-S01/wire.jsonl, IT-FILE-024-S01/db.jsonl, IT-FILE-024-S01/fs.jsonl | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-024-s02"></a>
#### IT-FILE-024-S02 / one_mutation

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "baseline": "positive_controlの新独立clone",
  "after_startup_mutation": {
    "descriptor.recordLength": 4799
  },
  "expected_stage": "recordLength check before FS",
  "wire_source": "実API資格の隔離reply driver、属性/長さ/context/correlationは指定以外合法"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：descriptor.recordLength one mutation。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 通常startup/認証後、指定1変異をrecordLength check before FSへ届くよう配置。record順変異はhash正当を先に保証しhash失敗で代用しない。実Webbroker受信→FS→表示を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-024-S02/http.jsonl, IT-FILE-024-S02/wire.jsonl, IT-FILE-024-S02/db.jsonl, IT-FILE-024-S02/fs.jsonl, IT-FILE-024-S02/os.jsonl, IT-FILE-024-S02/log.jsonl | UI234 FのFile record長は004800固定。4799は共通codecのsemantic検証で恒久protocolerror、SS322/SS321のWebreply隔離・ACK後非0停止、正常descriptor/stream0。HTTP安全終端は既timeout/503、成功HTTP200応答は0件。 |
| A03 | IT-FILE-024-S02/http.jsonl, IT-FILE-024-S02/wire.jsonl, IT-FILE-024-S02/db.jsonl, IT-FILE-024-S02/fs.jsonl, IT-FILE-024-S02/os.jsonl, IT-FILE-024-S02/log.jsonl | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 |
| A04 | IT-FILE-024-S02/http.jsonl, IT-FILE-024-S02/wire.jsonl, IT-FILE-024-S02/db.jsonl, IT-FILE-024-S02/fs.jsonl, IT-FILE-024-S02/os.jsonl, IT-FILE-024-S02/log.jsonl | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-025"></a>
## IT-FILE-025 descriptor.count変異の到達点と非露出

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor.count変異の到達点と非露出 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-025"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 | O-HTTP, O-WIRE, O-DB, O-FS。実測/path/SHA/判定式はattemptへ記録 |
| A02 | UI234 FのFile record件数上限10000。10001は共通codecのsemantic検証で恒久protocolerror、Webreply隔離・ACK後非0停止、stream0。成功HTTP200応答は0件。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-025`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-025-s01"></a>
#### IT-FILE-025-S01 / positive_control

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN": "201record/964800byte",
  "descriptor": "全field正常",
  "filesystem": "保持root/date/entry正常 regular0640/nlink1"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実APIresponseを実broker/Web/FSへ通して独立201record表を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-025-S01/http.jsonl, IT-FILE-025-S01/wire.jsonl, IT-FILE-025-S01/db.jsonl, IT-FILE-025-S01/fs.jsonl | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-025-s02"></a>
#### IT-FILE-025-S02 / one_mutation

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "baseline": "positive_controlの新独立clone",
  "after_startup_mutation": {
    "descriptor.count": 10001
  },
  "expected_stage": "count upper before FS",
  "wire_source": "実API資格の隔離reply driver、属性/長さ/context/correlationは指定以外合法"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：descriptor.count one mutation。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 通常startup/認証後、指定1変異をcount upper before FSへ届くよう配置。record順変異はhash正当を先に保証しhash失敗で代用しない。実Webbroker受信→FS→表示を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-025-S02/http.jsonl, IT-FILE-025-S02/wire.jsonl, IT-FILE-025-S02/db.jsonl, IT-FILE-025-S02/fs.jsonl, IT-FILE-025-S02/os.jsonl, IT-FILE-025-S02/log.jsonl | UI234 FのFile record件数上限10000。10001は共通codecのsemantic検証で恒久protocolerror、Webreply隔離・ACK後非0停止、stream0。成功HTTP200応答は0件。 |
| A03 | IT-FILE-025-S02/http.jsonl, IT-FILE-025-S02/wire.jsonl, IT-FILE-025-S02/db.jsonl, IT-FILE-025-S02/fs.jsonl, IT-FILE-025-S02/os.jsonl, IT-FILE-025-S02/log.jsonl | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 |
| A04 | IT-FILE-025-S02/http.jsonl, IT-FILE-025-S02/wire.jsonl, IT-FILE-025-S02/db.jsonl, IT-FILE-025-S02/fs.jsonl, IT-FILE-025-S02/os.jsonl, IT-FILE-025-S02/log.jsonl | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-026"></a>
## IT-FILE-026 configured Transfer root symlinkの起動拒否

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧caseはroot symlinkを全てHTTP503としたがstartupで不合格なら通常requestへ到達しない。初期gateと保持後差替えFILE060を分離。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-OPS |
| 確認契約 | configured Transfer root symlinkの起動拒否 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 2. Root・OS権限・責務 ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（1件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-026"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | root検査不合格/readiness false、業務producer/HTTP成功受付0。symlink追従/outsidefile read/write0、自動mkdir/chmod/chown0。 | O-OS, O-FS, O-MQ, O-DB, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A02 | startup失敗の既ownedresourceは正規close、未確認はUNKNOWN保持。HTTP503を観測したことにせず未起動状態を記録。 | O-OS, O-FS, O-MQ, O-DB, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, DEP-OPS-HOLD を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧caseはroot symlinkを全てHTTP503としたがstartupで不合格なら通常requestへ到達しない。初期gateと保持後差替えFILE060を分離。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-026`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-026-s01"></a>
#### IT-FILE-026-S01 / startup_root_link

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "configured_Transfer_root": "outsideへのsymlink",
  "outside": "正規属性を持つが所有scope外",
  "entry": "通常API Unitの新起動"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 隔離ordinary API startupを行う計画としroot gate/ready/producer開始を採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-026-S01/os.jsonl, IT-FILE-026-S01/fs.jsonl, IT-FILE-026-S01/mq.jsonl, IT-FILE-026-S01/db.jsonl, IT-FILE-026-S01/log.jsonl | root検査不合格/readiness false、業務producer/HTTP成功受付0。symlink追従/outsidefile read/write0、自動mkdir/chmod/chown0。 |
| A02 | IT-FILE-026-S01/os.jsonl, IT-FILE-026-S01/fs.jsonl, IT-FILE-026-S01/mq.jsonl, IT-FILE-026-S01/db.jsonl, IT-FILE-026-S01/log.jsonl | startup失敗の既ownedresourceは正規close、未確認はUNKNOWN保持。HTTP503を観測したことにせず未起動状態を記録。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-027"></a>
## IT-FILE-027 FS date変異の到達点と非露出

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | FS date変異の到達点と非露出 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-027"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 | O-HTTP, O-WIRE, O-DB, O-FS。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 503/FILE_INTEGRITY_MISMATCH分類、成功ViewModel/不正本文DOM表示0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-027`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-027-s01"></a>
#### IT-FILE-027-S01 / positive_control

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN": "201record/964800byte",
  "descriptor": "全field正常",
  "filesystem": "保持root/date/entry正常 regular0640/nlink1"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実APIresponseを実broker/Web/FSへ通して独立201record表を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-027-S01/http.jsonl, IT-FILE-027-S01/wire.jsonl, IT-FILE-027-S01/db.jsonl, IT-FILE-027-S01/fs.jsonl | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-027-s02"></a>
#### IT-FILE-027-S02 / one_mutation

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "baseline": "positive_controlの新独立clone",
  "after_startup_mutation": {
    "FS date": "正規date名をoutside symlinkへ置換"
  },
  "expected_stage": "date NOFOLLOW open",
  "wire_source": "実API資格の隔離reply driver、属性/長さ/context/correlationは指定以外合法"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：FS date one mutation。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 通常startup/認証後、指定1変異をdate NOFOLLOW openへ届くよう配置。record順変異はhash正当を先に保証しhash失敗で代用しない。実Webbroker受信→FS→表示を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-027-S02/http.jsonl, IT-FILE-027-S02/wire.jsonl, IT-FILE-027-S02/db.jsonl, IT-FILE-027-S02/fs.jsonl, IT-FILE-027-S02/os.jsonl, IT-FILE-027-S02/log.jsonl | 503/FILE_INTEGRITY_MISMATCH分類、成功ViewModel/不正本文DOM表示0。 |
| A03 | IT-FILE-027-S02/http.jsonl, IT-FILE-027-S02/wire.jsonl, IT-FILE-027-S02/db.jsonl, IT-FILE-027-S02/fs.jsonl, IT-FILE-027-S02/os.jsonl, IT-FILE-027-S02/log.jsonl | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 |
| A04 | IT-FILE-027-S02/http.jsonl, IT-FILE-027-S02/wire.jsonl, IT-FILE-027-S02/db.jsonl, IT-FILE-027-S02/fs.jsonl, IT-FILE-027-S02/os.jsonl, IT-FILE-027-S02/log.jsonl | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-028"></a>
## IT-FILE-028 FS entry変異の到達点と非露出

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | FS entry変異の到達点と非露出 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-028"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 | O-HTTP, O-WIRE, O-DB, O-FS。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 503/FILE_INTEGRITY_MISMATCH分類、成功ViewModel/不正本文DOM表示0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-028`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-028-s01"></a>
#### IT-FILE-028-S01 / positive_control

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN": "201record/964800byte",
  "descriptor": "全field正常",
  "filesystem": "保持root/date/entry正常 regular0640/nlink1"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実APIresponseを実broker/Web/FSへ通して独立201record表を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-028-S01/http.jsonl, IT-FILE-028-S01/wire.jsonl, IT-FILE-028-S01/db.jsonl, IT-FILE-028-S01/fs.jsonl | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-028-s02"></a>
#### IT-FILE-028-S02 / one_mutation

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "baseline": "positive_controlの新独立clone",
  "after_startup_mutation": {
    "FS entry": "正規UUID.readyをoutside symlinkへ置換"
  },
  "expected_stage": "entry O_PATH/NOFOLLOW attrs",
  "wire_source": "実API資格の隔離reply driver、属性/長さ/context/correlationは指定以外合法"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：FS entry one mutation。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 通常startup/認証後、指定1変異をentry O_PATH/NOFOLLOW attrsへ届くよう配置。record順変異はhash正当を先に保証しhash失敗で代用しない。実Webbroker受信→FS→表示を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-028-S02/http.jsonl, IT-FILE-028-S02/wire.jsonl, IT-FILE-028-S02/db.jsonl, IT-FILE-028-S02/fs.jsonl, IT-FILE-028-S02/os.jsonl, IT-FILE-028-S02/log.jsonl | 503/FILE_INTEGRITY_MISMATCH分類、成功ViewModel/不正本文DOM表示0。 |
| A03 | IT-FILE-028-S02/http.jsonl, IT-FILE-028-S02/wire.jsonl, IT-FILE-028-S02/db.jsonl, IT-FILE-028-S02/fs.jsonl, IT-FILE-028-S02/os.jsonl, IT-FILE-028-S02/log.jsonl | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 |
| A04 | IT-FILE-028-S02/http.jsonl, IT-FILE-028-S02/wire.jsonl, IT-FILE-028-S02/db.jsonl, IT-FILE-028-S02/fs.jsonl, IT-FILE-028-S02/os.jsonl, IT-FILE-028-S02/log.jsonl | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-029"></a>
## IT-FILE-029 FS hardlink変異の到達点と非露出

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | FS hardlink変異の到達点と非露出 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-029"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 | O-HTTP, O-WIRE, O-DB, O-FS。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 503/FILE_INTEGRITY_MISMATCH分類、成功ViewModel/不正本文DOM表示0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-029`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-029-s01"></a>
#### IT-FILE-029-S01 / positive_control

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN": "201record/964800byte",
  "descriptor": "全field正常",
  "filesystem": "保持root/date/entry正常 regular0640/nlink1"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実APIresponseを実broker/Web/FSへ通して独立201record表を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-029-S01/http.jsonl, IT-FILE-029-S01/wire.jsonl, IT-FILE-029-S01/db.jsonl, IT-FILE-029-S01/fs.jsonl | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-029-s02"></a>
#### IT-FILE-029-S02 / one_mutation

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "baseline": "positive_controlの新独立clone",
  "after_startup_mutation": {
    "FS hardlink": "正規readyへ別名hardlink1追加/nlink2"
  },
  "expected_stage": "保持inode attrs before read channel",
  "wire_source": "実API資格の隔離reply driver、属性/長さ/context/correlationは指定以外合法"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：FS hardlink one mutation。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 通常startup/認証後、指定1変異を保持inode attrs before read channelへ届くよう配置。record順変異はhash正当を先に保証しhash失敗で代用しない。実Webbroker受信→FS→表示を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-029-S02/http.jsonl, IT-FILE-029-S02/wire.jsonl, IT-FILE-029-S02/db.jsonl, IT-FILE-029-S02/fs.jsonl, IT-FILE-029-S02/os.jsonl, IT-FILE-029-S02/log.jsonl | 503/FILE_INTEGRITY_MISMATCH分類、成功ViewModel/不正本文DOM表示0。 |
| A03 | IT-FILE-029-S02/http.jsonl, IT-FILE-029-S02/wire.jsonl, IT-FILE-029-S02/db.jsonl, IT-FILE-029-S02/fs.jsonl, IT-FILE-029-S02/os.jsonl, IT-FILE-029-S02/log.jsonl | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 |
| A04 | IT-FILE-029-S02/http.jsonl, IT-FILE-029-S02/wire.jsonl, IT-FILE-029-S02/db.jsonl, IT-FILE-029-S02/fs.jsonl, IT-FILE-029-S02/os.jsonl, IT-FILE-029-S02/log.jsonl | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-030"></a>
## IT-FILE-030 FS same-inode content変異の到達点と非露出

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | FS same-inode content変異の到達点と非露出 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-030"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 | O-HTTP, O-WIRE, O-DB, O-FS。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 503/FILE_INTEGRITY_MISMATCH分類、成功ViewModel/不正本文DOM表示0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-030`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-030-s01"></a>
#### IT-FILE-030-S01 / positive_control

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN": "201record/964800byte",
  "descriptor": "全field正常",
  "filesystem": "保持root/date/entry正常 regular0640/nlink1"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実APIresponseを実broker/Web/FSへ通して独立201record表を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-030-S01/http.jsonl, IT-FILE-030-S01/wire.jsonl, IT-FILE-030-S01/db.jsonl, IT-FILE-030-S01/fs.jsonl | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-030-s02"></a>
#### IT-FILE-030-S02 / one_mutation

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "baseline": "positive_controlの新独立clone",
  "after_startup_mutation": {
    "FS same-inode content": "初回hash後にrecord末尾byte変更/size不変"
  },
  "expected_stage": "decode/end hash+post attrs",
  "wire_source": "実API資格の隔離reply driver、属性/長さ/context/correlationは指定以外合法"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：FS same-inode content one mutation。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 通常startup/認証後、指定1変異をdecode/end hash+post attrsへ届くよう配置。record順変異はhash正当を先に保証しhash失敗で代用しない。実Webbroker受信→FS→表示を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-030-S02/http.jsonl, IT-FILE-030-S02/wire.jsonl, IT-FILE-030-S02/db.jsonl, IT-FILE-030-S02/fs.jsonl, IT-FILE-030-S02/os.jsonl, IT-FILE-030-S02/log.jsonl | 503/FILE_INTEGRITY_MISMATCH分類、成功ViewModel/不正本文DOM表示0。 |
| A03 | IT-FILE-030-S02/http.jsonl, IT-FILE-030-S02/wire.jsonl, IT-FILE-030-S02/db.jsonl, IT-FILE-030-S02/fs.jsonl, IT-FILE-030-S02/os.jsonl, IT-FILE-030-S02/log.jsonl | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 |
| A04 | IT-FILE-030-S02/http.jsonl, IT-FILE-030-S02/wire.jsonl, IT-FILE-030-S02/db.jsonl, IT-FILE-030-S02/fs.jsonl, IT-FILE-030-S02/os.jsonl, IT-FILE-030-S02/log.jsonl | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-031"></a>
## IT-FILE-031 FS record order変異の到達点と非露出

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | FS record order変異の到達点と非露出 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) 固定長電文codec実装設計 > 9. Cross-field validator ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-031"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 | O-HTTP, O-WIRE, O-DB, O-FS。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 503/FILE_INTEGRITY_MISMATCH分類、成功ViewModel/不正本文DOM表示0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧全件同じ拒否期待を、decode前metadata/属性前open/hash後/sequence検査の到達点へ分解。必要な検証readまで禁止する誤期待を修正。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-031`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-031-s01"></a>
#### IT-FILE-031-S01 / positive_control

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "SCN": "201record/964800byte",
  "descriptor": "全field正常",
  "filesystem": "保持root/date/entry正常 regular0640/nlink1"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実APIresponseを実broker/Web/FSへ通して独立201record表を比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-031-S01/http.jsonl, IT-FILE-031-S01/wire.jsonl, IT-FILE-031-S01/db.jsonl, IT-FILE-031-S01/fs.jsonl | 201record完全表示、size/count/hash/順序一致。read-only取得にFS書込/削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-031-s02"></a>
#### IT-FILE-031-S02 / one_mutation

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "baseline": "positive_controlの新独立clone",
  "after_startup_mutation": {
    "FS record order": "record1/2入替え、独立SHAでdescriptor hashだけ再計算"
  },
  "expected_stage": "hash合格後record sequence",
  "wire_source": "実API資格の隔離reply driver、属性/長さ/context/correlationは指定以外合法"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：FS record order one mutation。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 通常startup/認証後、指定1変異をhash合格後record sequenceへ届くよう配置。record順変異はhash正当を先に保証しhash失敗で代用しない。実Webbroker受信→FS→表示を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-031-S02/http.jsonl, IT-FILE-031-S02/wire.jsonl, IT-FILE-031-S02/db.jsonl, IT-FILE-031-S02/fs.jsonl, IT-FILE-031-S02/os.jsonl, IT-FILE-031-S02/log.jsonl | 503/FILE_INTEGRITY_MISMATCH分類、成功ViewModel/不正本文DOM表示0。 |
| A03 | IT-FILE-031-S02/http.jsonl, IT-FILE-031-S02/wire.jsonl, IT-FILE-031-S02/db.jsonl, IT-FILE-031-S02/fs.jsonl, IT-FILE-031-S02/os.jsonl, IT-FILE-031-S02/log.jsonl | descriptor/attrs不適合は次段FSreadを行わない。hash/sequence検証のための正規保持inode readは許可し、outside symlink先/属性不適合inodeの内容read0。 |
| A04 | IT-FILE-031-S02/http.jsonl, IT-FILE-031-S02/wire.jsonl, IT-FILE-031-S02/db.jsonl, IT-FILE-031-S02/fs.jsonl, IT-FILE-031-S02/os.jsonl, IT-FILE-031-S02/log.jsonl | 既存file/Inbox/snapshotの書換え・削除0、原inode/hash/変異前後証拠保全。終端FD/permit全回収、UNKNOWNは保全して正常0件へ補完しない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-040"></a>
## IT-FILE-040 SCN F replayの存在/再生成/最終認証統合

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧5variantを5SCとして追跡。FILE050/051/TX051の単独契約を同じ実service経路で通し責務の結線を確認。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | SCN F replayの存在/再生成/最終認証統合 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 > 6.1 APIの再送file確認と再生成（SSC-027） ／ ['SSC-027'] ／ commit `7147c428bb9d`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) SQL・transaction・lock・削除設計 > 4. Scenario・Speaker・Media query > 4.2 Scenario file/detail（IF-003/004） ／ ['PT-IDEM-SR01', 'SSC-027'] ／ commit `7147c428bb9d`
- [324_Outbox・Inbox・冪等性・再送設計.md](<../../300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md>) Outbox・Inbox・冪等性・再送設計 > 7. Inbox transaction/crash > 7.1 Scenario段階処理と同Message排他（SSC-027） ／ ['SSC-027'] ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-040"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 存在正常は検証readだけ/publisher0/同descriptor。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 正規再生成で変えられるdescriptorはkey/date/UUIDだけ、DB暗号body/key_version以外17列/初回completed/expiry不変。元内容不一致は生成0。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 最終auth失効時0102/成功descriptor0、既存成功ERROR上書き0、公開ready削除0。I/O中DBTX/lock0。各variantの故障到達はFILE050/051/TX051の個別receiptと対応。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | native ENOENT確定だけ再生成候補、元metadata8/count/hash一致時publisher1。hash不正/close不明をMISSINGへ補完0。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 正規再生成で変えられるdescriptorはkey/date/UUIDだけ、DB暗号body/key_version以外17列/初回completed/expiry不変。元内容不一致は生成0。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A06 | 最終auth失効時0102/成功descriptor0、既存成功ERROR上書き0、公開ready削除0。I/O中DBTX/lock0。各variantの故障到達はFILE050/051/TX051の個別receiptと対応。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A07 | native ENOENT確定だけ再生成候補、元metadata8/count/hash一致時publisher1。hash不正/close不明をMISSINGへ補完0。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A08 | 正規再生成で変えられるdescriptorはkey/date/UUIDだけ、DB暗号body/key_version以外17列/初回completed/expiry不変。元内容不一致は生成0。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A09 | 最終auth失効時0102/成功descriptor0、既存成功ERROR上書き0、公開ready削除0。I/O中DBTX/lock0。各variantの故障到達はFILE050/051/TX051の個別receiptと対応。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A10 | native ENOENT確定だけ再生成候補、元metadata8/count/hash一致時publisher1。hash不正/close不明をMISSINGへ補完0。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A11 | 正規再生成で変えられるdescriptorはkey/date/UUIDだけ、DB暗号body/key_version以外17列/初回completed/expiry不変。元内容不一致は生成0。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A12 | 最終auth失効時0102/成功descriptor0、既存成功ERROR上書き0、公開ready削除0。I/O中DBTX/lock0。各variantの故障到達はFILE050/051/TX051の個別receiptと対応。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A13 | native ENOENT確定だけ再生成候補、元metadata8/count/hash一致時publisher1。hash不正/close不明をMISSINGへ補完0。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A14 | 正規再生成で変えられるdescriptorはkey/date/UUIDだけ、DB暗号body/key_version以外17列/初回completed/expiry不変。元内容不一致は生成0。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A15 | 最終auth失効時0102/成功descriptor0、既存成功ERROR上書き0、公開ready削除0。I/O中DBTX/lock0。各variantの故障到達はFILE050/051/TX051の個別receiptと対応。 | O-DB, O-FS, O-WIRE, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧5variantを5SCとして追跡。FILE050/051/TX051の単独契約を同じ実service経路で通し責務の結線を確認。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-040`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-040-s01"></a>
#### IT-FILE-040-S01 / ready_exists

種類：復旧、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "Inbox": "元SCN F201 COMPLETED",
  "variant": "ready_exists",
  "metadata8": "元固定表",
  "count/hash": "201/独立record SHA256"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：variantに対応する一回file状態又はrevoke（詳細SC表）。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 元token replayを実APIで実行し、native存在確認→snapshot取得→必要時publisher→最終writeをbarrierで採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-040-S01/db.jsonl, IT-FILE-040-S01/fs.jsonl, IT-FILE-040-S01/wire.jsonl, IT-FILE-040-S01/lock.jsonl, IT-FILE-040-S01/time.jsonl | 存在正常は検証readだけ/publisher0/同descriptor。 |
| A02 | IT-FILE-040-S01/db.jsonl, IT-FILE-040-S01/fs.jsonl, IT-FILE-040-S01/wire.jsonl, IT-FILE-040-S01/lock.jsonl, IT-FILE-040-S01/time.jsonl | 正規再生成で変えられるdescriptorはkey/date/UUIDだけ、DB暗号body/key_version以外17列/初回completed/expiry不変。元内容不一致は生成0。 |
| A03 | IT-FILE-040-S01/db.jsonl, IT-FILE-040-S01/fs.jsonl, IT-FILE-040-S01/wire.jsonl, IT-FILE-040-S01/lock.jsonl, IT-FILE-040-S01/time.jsonl | 最終auth失効時0102/成功descriptor0、既存成功ERROR上書き0、公開ready削除0。I/O中DBTX/lock0。各variantの故障到達はFILE050/051/TX051の個別receiptと対応。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-040-s02"></a>
#### IT-FILE-040-S02 / native_missing

種類：復旧、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "Inbox": "元SCN F201 COMPLETED",
  "variant": "native_missing",
  "metadata8": "元固定表",
  "count/hash": "201/独立record SHA256",
  "physical": "root検査成功後date又はready nativeENOENT",
  "expected_publisher_calls": 1
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：variantに対応する一回file状態又はrevoke（詳細SC表）。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 元token replayを実APIで実行し、native存在確認→snapshot取得→必要時publisher→最終writeをbarrierで採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A04 | IT-FILE-040-S02/db.jsonl, IT-FILE-040-S02/fs.jsonl, IT-FILE-040-S02/wire.jsonl, IT-FILE-040-S02/lock.jsonl, IT-FILE-040-S02/time.jsonl | native ENOENT確定だけ再生成候補、元metadata8/count/hash一致時publisher1。hash不正/close不明をMISSINGへ補完0。 |
| A05 | IT-FILE-040-S02/db.jsonl, IT-FILE-040-S02/fs.jsonl, IT-FILE-040-S02/wire.jsonl, IT-FILE-040-S02/lock.jsonl, IT-FILE-040-S02/time.jsonl | 正規再生成で変えられるdescriptorはkey/date/UUIDだけ、DB暗号body/key_version以外17列/初回completed/expiry不変。元内容不一致は生成0。 |
| A06 | IT-FILE-040-S02/db.jsonl, IT-FILE-040-S02/fs.jsonl, IT-FILE-040-S02/wire.jsonl, IT-FILE-040-S02/lock.jsonl, IT-FILE-040-S02/time.jsonl | 最終auth失効時0102/成功descriptor0、既存成功ERROR上書き0、公開ready削除0。I/O中DBTX/lock0。各variantの故障到達はFILE050/051/TX051の個別receiptと対応。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-040-s03"></a>
#### IT-FILE-040-S03 / hash_bad

種類：復旧、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "Inbox": "元SCN F201 COMPLETED",
  "variant": "hash_bad",
  "metadata8": "元固定表",
  "count/hash": "201/独立record SHA256",
  "physical": "通常inodeだが1byte改変/元descriptor SHA不一致",
  "expected_publisher_calls": 0
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：variantに対応する一回file状態又はrevoke（詳細SC表）。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 元token replayを実APIで実行し、native存在確認→snapshot取得→必要時publisher→最終writeをbarrierで採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A07 | IT-FILE-040-S03/db.jsonl, IT-FILE-040-S03/fs.jsonl, IT-FILE-040-S03/wire.jsonl, IT-FILE-040-S03/lock.jsonl, IT-FILE-040-S03/time.jsonl | native ENOENT確定だけ再生成候補、元metadata8/count/hash一致時publisher1。hash不正/close不明をMISSINGへ補完0。 |
| A08 | IT-FILE-040-S03/db.jsonl, IT-FILE-040-S03/fs.jsonl, IT-FILE-040-S03/wire.jsonl, IT-FILE-040-S03/lock.jsonl, IT-FILE-040-S03/time.jsonl | 正規再生成で変えられるdescriptorはkey/date/UUIDだけ、DB暗号body/key_version以外17列/初回completed/expiry不変。元内容不一致は生成0。 |
| A09 | IT-FILE-040-S03/db.jsonl, IT-FILE-040-S03/fs.jsonl, IT-FILE-040-S03/wire.jsonl, IT-FILE-040-S03/lock.jsonl, IT-FILE-040-S03/time.jsonl | 最終auth失効時0102/成功descriptor0、既存成功ERROR上書き0、公開ready削除0。I/O中DBTX/lock0。各variantの故障到達はFILE050/051/TX051の個別receiptと対応。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-040-s04"></a>
#### IT-FILE-040-S04 / regeneration_revoke

種類：復旧、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "Inbox": "元SCN F201 COMPLETED",
  "variant": "regeneration_revoke",
  "metadata8": "元固定表",
  "count/hash": "201/独立record SHA256",
  "physical": "native不在、再生成内容は元と一致",
  "fault_point": "新ready公開後/最終write verify前にS0正規失効"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：variantに対応する一回file状態又はrevoke（詳細SC表）。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 元metadata8/count/hash一致で新ready公開まで進める。最終verify直前barrier中に別正規操作でS0失効commit→再開。0102/Inbox不変とready保全を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A10 | IT-FILE-040-S04/db.jsonl, IT-FILE-040-S04/fs.jsonl, IT-FILE-040-S04/wire.jsonl, IT-FILE-040-S04/lock.jsonl, IT-FILE-040-S04/time.jsonl | native ENOENT確定だけ再生成候補、元metadata8/count/hash一致時publisher1。hash不正/close不明をMISSINGへ補完0。 |
| A11 | IT-FILE-040-S04/db.jsonl, IT-FILE-040-S04/fs.jsonl, IT-FILE-040-S04/wire.jsonl, IT-FILE-040-S04/lock.jsonl, IT-FILE-040-S04/time.jsonl | 正規再生成で変えられるdescriptorはkey/date/UUIDだけ、DB暗号body/key_version以外17列/初回completed/expiry不変。元内容不一致は生成0。 |
| A12 | IT-FILE-040-S04/db.jsonl, IT-FILE-040-S04/fs.jsonl, IT-FILE-040-S04/wire.jsonl, IT-FILE-040-S04/lock.jsonl, IT-FILE-040-S04/time.jsonl | 最終auth失効時0102/成功descriptor0、既存成功ERROR上書き0、公開ready削除0。I/O中DBTX/lock0。各variantの故障到達はFILE050/051/TX051の個別receiptと対応。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-040-s05"></a>
#### IT-FILE-040-S05 / snapshot_changed

種類：復旧、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "Inbox": "元SCN F201 COMPLETED",
  "variant": "snapshot_changed",
  "metadata8": "元固定表",
  "count/hash": "201/独立record SHA256",
  "physical": "native不在",
  "master_mutation": "元8metadata中game_codeだけ不一致",
  "expected_publisher_calls": 0
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：variantに対応する一回file状態又はrevoke（詳細SC表）。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 元token replayを実APIで実行し、native存在確認→snapshot取得→必要時publisher→最終writeをbarrierで採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A13 | IT-FILE-040-S05/db.jsonl, IT-FILE-040-S05/fs.jsonl, IT-FILE-040-S05/wire.jsonl, IT-FILE-040-S05/lock.jsonl, IT-FILE-040-S05/time.jsonl | native ENOENT確定だけ再生成候補、元metadata8/count/hash一致時publisher1。hash不正/close不明をMISSINGへ補完0。 |
| A14 | IT-FILE-040-S05/db.jsonl, IT-FILE-040-S05/fs.jsonl, IT-FILE-040-S05/wire.jsonl, IT-FILE-040-S05/lock.jsonl, IT-FILE-040-S05/time.jsonl | 正規再生成で変えられるdescriptorはkey/date/UUIDだけ、DB暗号body/key_version以外17列/初回completed/expiry不変。元内容不一致は生成0。 |
| A15 | IT-FILE-040-S05/db.jsonl, IT-FILE-040-S05/fs.jsonl, IT-FILE-040-S05/wire.jsonl, IT-FILE-040-S05/lock.jsonl, IT-FILE-040-S05/time.jsonl | 最終auth失効時0102/成功descriptor0、既存成功ERROR上書き0、公開ready削除0。I/O中DBTX/lock0。各variantの故障到達はFILE050/051/TX051の個別receiptと対応。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-range-001"></a>
## IT-RANGE-001 Range/HEAD first-spec・1MiB上限parameter表

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧15caseは値だけの違い。GET/HEADと全入力/期待byte範囲を30実行単位へ明示してcaseを統合。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | Range/HEAD first-spec・1MiB上限parameter表 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 3. Class・method責務 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 10. Range解析・応答 > 10.2 範囲計算 ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（2件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-RANGE-001"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP 200。actual body length=2097169。Content-Length=2097169。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET body&#91;j&#93;=(start+j)%251、start=0、全byte一致。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A03 | HTTP 200。actual body length=0。Content-Length=2097169。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A04 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A05 | HTTP 206。actual body length=1。Content-Range bytes 0-0/2097169、Content-Length=1。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A06 | GET body&#91;j&#93;=(start+j)%251、start=0、全byte一致。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A07 | HTTP 206。actual body length=0。Content-Range bytes 0-0/2097169、Content-Length=1。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A08 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A09 | HTTP 206。actual body length=1048576。Content-Range bytes 0-1048575/2097169、Content-Length=1048576。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A10 | GET body&#91;j&#93;=(start+j)%251、start=0、全byte一致。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A11 | HTTP 206。actual body length=0。Content-Range bytes 0-1048575/2097169、Content-Length=1048576。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A12 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A13 | HTTP 206。actual body length=1048576。Content-Range bytes 0-1048575/2097169、Content-Length=1048576。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A14 | GET body&#91;j&#93;=(start+j)%251、start=0、全byte一致。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A15 | HTTP 206。actual body length=0。Content-Range bytes 0-1048575/2097169、Content-Length=1048576。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A16 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A17 | HTTP 206。actual body length=1048576。Content-Range bytes 1048576-2097151/2097169、Content-Length=1048576。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A18 | GET body&#91;j&#93;=(start+j)%251、start=1048576、全byte一致。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A19 | HTTP 206。actual body length=0。Content-Range bytes 1048576-2097151/2097169、Content-Length=1048576。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A20 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A21 | HTTP 206。actual body length=1。Content-Range bytes 2097168-2097168/2097169、Content-Length=1。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A22 | GET body&#91;j&#93;=(start+j)%251、start=2097168、全byte一致。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A23 | HTTP 206。actual body length=0。Content-Range bytes 2097168-2097168/2097169、Content-Length=1。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A24 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A25 | HTTP 206。actual body length=1048576。Content-Range bytes 0-1048575/2097169、Content-Length=1048576。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A26 | GET body&#91;j&#93;=(start+j)%251、start=0、全byte一致。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A27 | HTTP 206。actual body length=0。Content-Range bytes 0-1048575/2097169、Content-Length=1048576。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A28 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A29 | HTTP 206。actual body length=1。Content-Range bytes 2097168-2097168/2097169、Content-Length=1。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A30 | GET body&#91;j&#93;=(start+j)%251、start=2097168、全byte一致。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A31 | HTTP 206。actual body length=0。Content-Range bytes 2097168-2097168/2097169、Content-Length=1。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A32 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A33 | HTTP 416。actual body length=0。Content-Range bytes */2097169。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A34 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A35 | HTTP 416。actual body length=0。Content-Range bytes */2097169。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A36 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A37 | HTTP 416。actual body length=0。Content-Range bytes */2097169。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A38 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A39 | HTTP 416。actual body length=0。Content-Range bytes */2097169。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A40 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A41 | HTTP 416。actual body length=0。Content-Range bytes */2097169。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A42 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A43 | HTTP 416。actual body length=0。Content-Range bytes */2097169。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A44 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A45 | HTTP 416。actual body length=0。Content-Range bytes */2097169。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A46 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A47 | HTTP 416。actual body length=0。Content-Range bytes */2097169。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A48 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A49 | HTTP 206。actual body length=1。Content-Range bytes 0-0/2097169、Content-Length=1。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A50 | GET body&#91;j&#93;=(start+j)%251、start=0、全byte一致。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A51 | HTTP 206。actual body length=0。Content-Range bytes 0-0/2097169、Content-Length=1。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A52 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A53 | HTTP 416。actual body length=0。Content-Range bytes */2097169。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A54 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A55 | HTTP 416。actual body length=0。Content-Range bytes */2097169。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A56 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A57 | HTTP 416。actual body length=0。Content-Range bytes */2097169。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A58 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A59 | HTTP 416。actual body length=0。Content-Range bytes */2097169。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A60 | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 | O-HTTP, O-FS, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧15caseは値だけの違い。GET/HEADと全入力/期待byte範囲を30実行単位へ明示してcaseを統合。

同一Range配信契約のparameter差なので独立15caseの必要なし。各HTTPは別SCで追跡、反復やbyte数をcaseへ加算しない。

契約：`ITC-RANGE-001`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-range-001-s01"></a>
#### IT-RANGE-001-S01 / none_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": null,
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-RANGE-001-S01/http.jsonl, IT-RANGE-001-S01/fs.jsonl, IT-RANGE-001-S01/metric.jsonl | HTTP 200。actual body length=2097169。Content-Length=2097169。 |
| A02 | IT-RANGE-001-S01/http.jsonl, IT-RANGE-001-S01/fs.jsonl, IT-RANGE-001-S01/metric.jsonl | GET body[j]=(start+j)%251、start=0、全byte一致。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s02"></a>
#### IT-RANGE-001-S02 / none_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": null,
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A03 | IT-RANGE-001-S02/http.jsonl, IT-RANGE-001-S02/fs.jsonl, IT-RANGE-001-S02/metric.jsonl | HTTP 200。actual body length=0。Content-Length=2097169。 |
| A04 | IT-RANGE-001-S02/http.jsonl, IT-RANGE-001-S02/fs.jsonl, IT-RANGE-001-S02/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s03"></a>
#### IT-RANGE-001-S03 / one_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": "bytes=0-0",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A05 | IT-RANGE-001-S03/http.jsonl, IT-RANGE-001-S03/fs.jsonl, IT-RANGE-001-S03/metric.jsonl | HTTP 206。actual body length=1。Content-Range bytes 0-0/2097169、Content-Length=1。 |
| A06 | IT-RANGE-001-S03/http.jsonl, IT-RANGE-001-S03/fs.jsonl, IT-RANGE-001-S03/metric.jsonl | GET body[j]=(start+j)%251、start=0、全byte一致。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s04"></a>
#### IT-RANGE-001-S04 / one_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": "bytes=0-0",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A07 | IT-RANGE-001-S04/http.jsonl, IT-RANGE-001-S04/fs.jsonl, IT-RANGE-001-S04/metric.jsonl | HTTP 206。actual body length=0。Content-Range bytes 0-0/2097169、Content-Length=1。 |
| A08 | IT-RANGE-001-S04/http.jsonl, IT-RANGE-001-S04/fs.jsonl, IT-RANGE-001-S04/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s05"></a>
#### IT-RANGE-001-S05 / 1MiB_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": "bytes=0-1048575",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A09 | IT-RANGE-001-S05/http.jsonl, IT-RANGE-001-S05/fs.jsonl, IT-RANGE-001-S05/metric.jsonl | HTTP 206。actual body length=1048576。Content-Range bytes 0-1048575/2097169、Content-Length=1048576。 |
| A10 | IT-RANGE-001-S05/http.jsonl, IT-RANGE-001-S05/fs.jsonl, IT-RANGE-001-S05/metric.jsonl | GET body[j]=(start+j)%251、start=0、全byte一致。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s06"></a>
#### IT-RANGE-001-S06 / 1MiB_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": "bytes=0-1048575",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A11 | IT-RANGE-001-S06/http.jsonl, IT-RANGE-001-S06/fs.jsonl, IT-RANGE-001-S06/metric.jsonl | HTTP 206。actual body length=0。Content-Range bytes 0-1048575/2097169、Content-Length=1048576。 |
| A12 | IT-RANGE-001-S06/http.jsonl, IT-RANGE-001-S06/fs.jsonl, IT-RANGE-001-S06/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s07"></a>
#### IT-RANGE-001-S07 / over1MiB_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": "bytes=0-1048576",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A13 | IT-RANGE-001-S07/http.jsonl, IT-RANGE-001-S07/fs.jsonl, IT-RANGE-001-S07/metric.jsonl | HTTP 206。actual body length=1048576。Content-Range bytes 0-1048575/2097169、Content-Length=1048576。 |
| A14 | IT-RANGE-001-S07/http.jsonl, IT-RANGE-001-S07/fs.jsonl, IT-RANGE-001-S07/metric.jsonl | GET body[j]=(start+j)%251、start=0、全byte一致。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s08"></a>
#### IT-RANGE-001-S08 / over1MiB_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": "bytes=0-1048576",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A15 | IT-RANGE-001-S08/http.jsonl, IT-RANGE-001-S08/fs.jsonl, IT-RANGE-001-S08/metric.jsonl | HTTP 206。actual body length=0。Content-Range bytes 0-1048575/2097169、Content-Length=1048576。 |
| A16 | IT-RANGE-001-S08/http.jsonl, IT-RANGE-001-S08/fs.jsonl, IT-RANGE-001-S08/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s09"></a>
#### IT-RANGE-001-S09 / open_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": "bytes=1048576-",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A17 | IT-RANGE-001-S09/http.jsonl, IT-RANGE-001-S09/fs.jsonl, IT-RANGE-001-S09/metric.jsonl | HTTP 206。actual body length=1048576。Content-Range bytes 1048576-2097151/2097169、Content-Length=1048576。 |
| A18 | IT-RANGE-001-S09/http.jsonl, IT-RANGE-001-S09/fs.jsonl, IT-RANGE-001-S09/metric.jsonl | GET body[j]=(start+j)%251、start=1048576、全byte一致。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s10"></a>
#### IT-RANGE-001-S10 / open_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": "bytes=1048576-",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A19 | IT-RANGE-001-S10/http.jsonl, IT-RANGE-001-S10/fs.jsonl, IT-RANGE-001-S10/metric.jsonl | HTTP 206。actual body length=0。Content-Range bytes 1048576-2097151/2097169、Content-Length=1048576。 |
| A20 | IT-RANGE-001-S10/http.jsonl, IT-RANGE-001-S10/fs.jsonl, IT-RANGE-001-S10/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s11"></a>
#### IT-RANGE-001-S11 / suffix1_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": "bytes=-1",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A21 | IT-RANGE-001-S11/http.jsonl, IT-RANGE-001-S11/fs.jsonl, IT-RANGE-001-S11/metric.jsonl | HTTP 206。actual body length=1。Content-Range bytes 2097168-2097168/2097169、Content-Length=1。 |
| A22 | IT-RANGE-001-S11/http.jsonl, IT-RANGE-001-S11/fs.jsonl, IT-RANGE-001-S11/metric.jsonl | GET body[j]=(start+j)%251、start=2097168、全byte一致。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s12"></a>
#### IT-RANGE-001-S12 / suffix1_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": "bytes=-1",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A23 | IT-RANGE-001-S12/http.jsonl, IT-RANGE-001-S12/fs.jsonl, IT-RANGE-001-S12/metric.jsonl | HTTP 206。actual body length=0。Content-Range bytes 2097168-2097168/2097169、Content-Length=1。 |
| A24 | IT-RANGE-001-S12/http.jsonl, IT-RANGE-001-S12/fs.jsonl, IT-RANGE-001-S12/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s13"></a>
#### IT-RANGE-001-S13 / suffixbig_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": "bytes=-3000000",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A25 | IT-RANGE-001-S13/http.jsonl, IT-RANGE-001-S13/fs.jsonl, IT-RANGE-001-S13/metric.jsonl | HTTP 206。actual body length=1048576。Content-Range bytes 0-1048575/2097169、Content-Length=1048576。 |
| A26 | IT-RANGE-001-S13/http.jsonl, IT-RANGE-001-S13/fs.jsonl, IT-RANGE-001-S13/metric.jsonl | GET body[j]=(start+j)%251、start=0、全byte一致。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s14"></a>
#### IT-RANGE-001-S14 / suffixbig_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": "bytes=-3000000",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A27 | IT-RANGE-001-S14/http.jsonl, IT-RANGE-001-S14/fs.jsonl, IT-RANGE-001-S14/metric.jsonl | HTTP 206。actual body length=0。Content-Range bytes 0-1048575/2097169、Content-Length=1048576。 |
| A28 | IT-RANGE-001-S14/http.jsonl, IT-RANGE-001-S14/fs.jsonl, IT-RANGE-001-S14/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s15"></a>
#### IT-RANGE-001-S15 / last_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": "bytes=2097168-2097168",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A29 | IT-RANGE-001-S15/http.jsonl, IT-RANGE-001-S15/fs.jsonl, IT-RANGE-001-S15/metric.jsonl | HTTP 206。actual body length=1。Content-Range bytes 2097168-2097168/2097169、Content-Length=1。 |
| A30 | IT-RANGE-001-S15/http.jsonl, IT-RANGE-001-S15/fs.jsonl, IT-RANGE-001-S15/metric.jsonl | GET body[j]=(start+j)%251、start=2097168、全byte一致。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s16"></a>
#### IT-RANGE-001-S16 / last_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": "bytes=2097168-2097168",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A31 | IT-RANGE-001-S16/http.jsonl, IT-RANGE-001-S16/fs.jsonl, IT-RANGE-001-S16/metric.jsonl | HTTP 206。actual body length=0。Content-Range bytes 2097168-2097168/2097169、Content-Length=1。 |
| A32 | IT-RANGE-001-S16/http.jsonl, IT-RANGE-001-S16/fs.jsonl, IT-RANGE-001-S16/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s17"></a>
#### IT-RANGE-001-S17 / atTotal_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": "bytes=2097169-",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A33 | IT-RANGE-001-S17/http.jsonl, IT-RANGE-001-S17/fs.jsonl, IT-RANGE-001-S17/metric.jsonl | HTTP 416。actual body length=0。Content-Range bytes */2097169。 |
| A34 | IT-RANGE-001-S17/http.jsonl, IT-RANGE-001-S17/fs.jsonl, IT-RANGE-001-S17/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s18"></a>
#### IT-RANGE-001-S18 / atTotal_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": "bytes=2097169-",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A35 | IT-RANGE-001-S18/http.jsonl, IT-RANGE-001-S18/fs.jsonl, IT-RANGE-001-S18/metric.jsonl | HTTP 416。actual body length=0。Content-Range bytes */2097169。 |
| A36 | IT-RANGE-001-S18/http.jsonl, IT-RANGE-001-S18/fs.jsonl, IT-RANGE-001-S18/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s19"></a>
#### IT-RANGE-001-S19 / reverse_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": "bytes=10-9",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A37 | IT-RANGE-001-S19/http.jsonl, IT-RANGE-001-S19/fs.jsonl, IT-RANGE-001-S19/metric.jsonl | HTTP 416。actual body length=0。Content-Range bytes */2097169。 |
| A38 | IT-RANGE-001-S19/http.jsonl, IT-RANGE-001-S19/fs.jsonl, IT-RANGE-001-S19/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s20"></a>
#### IT-RANGE-001-S20 / reverse_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": "bytes=10-9",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A39 | IT-RANGE-001-S20/http.jsonl, IT-RANGE-001-S20/fs.jsonl, IT-RANGE-001-S20/metric.jsonl | HTTP 416。actual body length=0。Content-Range bytes */2097169。 |
| A40 | IT-RANGE-001-S20/http.jsonl, IT-RANGE-001-S20/fs.jsonl, IT-RANGE-001-S20/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s21"></a>
#### IT-RANGE-001-S21 / invalid_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": "bytes=a-b",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A41 | IT-RANGE-001-S21/http.jsonl, IT-RANGE-001-S21/fs.jsonl, IT-RANGE-001-S21/metric.jsonl | HTTP 416。actual body length=0。Content-Range bytes */2097169。 |
| A42 | IT-RANGE-001-S21/http.jsonl, IT-RANGE-001-S21/fs.jsonl, IT-RANGE-001-S21/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s22"></a>
#### IT-RANGE-001-S22 / invalid_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": "bytes=a-b",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A43 | IT-RANGE-001-S22/http.jsonl, IT-RANGE-001-S22/fs.jsonl, IT-RANGE-001-S22/metric.jsonl | HTTP 416。actual body length=0。Content-Range bytes */2097169。 |
| A44 | IT-RANGE-001-S22/http.jsonl, IT-RANGE-001-S22/fs.jsonl, IT-RANGE-001-S22/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s23"></a>
#### IT-RANGE-001-S23 / overflow_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": "bytes=9223372036854775808-",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A45 | IT-RANGE-001-S23/http.jsonl, IT-RANGE-001-S23/fs.jsonl, IT-RANGE-001-S23/metric.jsonl | HTTP 416。actual body length=0。Content-Range bytes */2097169。 |
| A46 | IT-RANGE-001-S23/http.jsonl, IT-RANGE-001-S23/fs.jsonl, IT-RANGE-001-S23/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s24"></a>
#### IT-RANGE-001-S24 / overflow_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": "bytes=9223372036854775808-",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A47 | IT-RANGE-001-S24/http.jsonl, IT-RANGE-001-S24/fs.jsonl, IT-RANGE-001-S24/metric.jsonl | HTTP 416。actual body length=0。Content-Range bytes */2097169。 |
| A48 | IT-RANGE-001-S24/http.jsonl, IT-RANGE-001-S24/fs.jsonl, IT-RANGE-001-S24/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s25"></a>
#### IT-RANGE-001-S25 / multiValidFirst_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": "bytes=0-0,a-b",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A49 | IT-RANGE-001-S25/http.jsonl, IT-RANGE-001-S25/fs.jsonl, IT-RANGE-001-S25/metric.jsonl | HTTP 206。actual body length=1。Content-Range bytes 0-0/2097169、Content-Length=1。 |
| A50 | IT-RANGE-001-S25/http.jsonl, IT-RANGE-001-S25/fs.jsonl, IT-RANGE-001-S25/metric.jsonl | GET body[j]=(start+j)%251、start=0、全byte一致。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s26"></a>
#### IT-RANGE-001-S26 / multiValidFirst_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": "bytes=0-0,a-b",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A51 | IT-RANGE-001-S26/http.jsonl, IT-RANGE-001-S26/fs.jsonl, IT-RANGE-001-S26/metric.jsonl | HTTP 206。actual body length=0。Content-Range bytes 0-0/2097169、Content-Length=1。 |
| A52 | IT-RANGE-001-S26/http.jsonl, IT-RANGE-001-S26/fs.jsonl, IT-RANGE-001-S26/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s27"></a>
#### IT-RANGE-001-S27 / multiInvalidFirst_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": "bytes=a-b,0-0",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A53 | IT-RANGE-001-S27/http.jsonl, IT-RANGE-001-S27/fs.jsonl, IT-RANGE-001-S27/metric.jsonl | HTTP 416。actual body length=0。Content-Range bytes */2097169。 |
| A54 | IT-RANGE-001-S27/http.jsonl, IT-RANGE-001-S27/fs.jsonl, IT-RANGE-001-S27/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s28"></a>
#### IT-RANGE-001-S28 / multiInvalidFirst_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": "bytes=a-b,0-0",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A55 | IT-RANGE-001-S28/http.jsonl, IT-RANGE-001-S28/fs.jsonl, IT-RANGE-001-S28/metric.jsonl | HTTP 416。actual body length=0。Content-Range bytes */2097169。 |
| A56 | IT-RANGE-001-S28/http.jsonl, IT-RANGE-001-S28/fs.jsonl, IT-RANGE-001-S28/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s29"></a>
#### IT-RANGE-001-S29 / unknownUnit_GET

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "GET",
  "Range": "items=0-0",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A57 | IT-RANGE-001-S29/http.jsonl, IT-RANGE-001-S29/fs.jsonl, IT-RANGE-001-S29/metric.jsonl | HTTP 416。actual body length=0。Content-Range bytes */2097169。 |
| A58 | IT-RANGE-001-S29/http.jsonl, IT-RANGE-001-S29/fs.jsonl, IT-RANGE-001-S29/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-001-s30"></a>
#### IT-RANGE-001-S30 / unknownUnit_HEAD

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "method": "HEAD",
  "Range": "items=0-0",
  "total": 2097169,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実descriptor認証後、実AssetをHTTPで一回取得。独立生成したbyte列とwire/headerを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A59 | IT-RANGE-001-S30/http.jsonl, IT-RANGE-001-S30/fs.jsonl, IT-RANGE-001-S30/metric.jsonl | HTTP 416。actual body length=0。Content-Range bytes */2097169。 |
| A60 | IT-RANGE-001-S30/http.jsonl, IT-RANGE-001-S30/fs.jsonl, IT-RANGE-001-S30/metric.jsonl | body bytes=0、extra response/body送信0。同inode保持、pool/FDは終端後before値。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-range-002"></a>
## IT-RANGE-002（統合済・実行対象外）

継続先：[IT-RANGE-001](524_ファイル・メディア・Range.md#it-range-001)。同一Range契約のparameter表へ。旧入力差/変更はcase-changesで追跡、SCが実行単位。

<a id="it-range-003"></a>
## IT-RANGE-003（統合済・実行対象外）

継続先：[IT-RANGE-001](524_ファイル・メディア・Range.md#it-range-001)。同一Range契約のparameter表へ。旧入力差/変更はcase-changesで追跡、SCが実行単位。

<a id="it-range-004"></a>
## IT-RANGE-004（統合済・実行対象外）

継続先：[IT-RANGE-001](524_ファイル・メディア・Range.md#it-range-001)。同一Range契約のparameter表へ。旧入力差/変更はcase-changesで追跡、SCが実行単位。

<a id="it-range-005"></a>
## IT-RANGE-005（統合済・実行対象外）

継続先：[IT-RANGE-001](524_ファイル・メディア・Range.md#it-range-001)。同一Range契約のparameter表へ。旧入力差/変更はcase-changesで追跡、SCが実行単位。

<a id="it-range-006"></a>
## IT-RANGE-006（統合済・実行対象外）

継続先：[IT-RANGE-001](524_ファイル・メディア・Range.md#it-range-001)。同一Range契約のparameter表へ。旧入力差/変更はcase-changesで追跡、SCが実行単位。

<a id="it-range-007"></a>
## IT-RANGE-007（統合済・実行対象外）

継続先：[IT-RANGE-001](524_ファイル・メディア・Range.md#it-range-001)。同一Range契約のparameter表へ。旧入力差/変更はcase-changesで追跡、SCが実行単位。

<a id="it-range-008"></a>
## IT-RANGE-008（統合済・実行対象外）

継続先：[IT-RANGE-001](524_ファイル・メディア・Range.md#it-range-001)。同一Range契約のparameter表へ。旧入力差/変更はcase-changesで追跡、SCが実行単位。

<a id="it-range-009"></a>
## IT-RANGE-009（統合済・実行対象外）

継続先：[IT-RANGE-001](524_ファイル・メディア・Range.md#it-range-001)。同一Range契約のparameter表へ。旧入力差/変更はcase-changesで追跡、SCが実行単位。

<a id="it-range-010"></a>
## IT-RANGE-010（統合済・実行対象外）

継続先：[IT-RANGE-001](524_ファイル・メディア・Range.md#it-range-001)。同一Range契約のparameter表へ。旧入力差/変更はcase-changesで追跡、SCが実行単位。

<a id="it-range-011"></a>
## IT-RANGE-011（統合済・実行対象外）

継続先：[IT-RANGE-001](524_ファイル・メディア・Range.md#it-range-001)。同一Range契約のparameter表へ。旧入力差/変更はcase-changesで追跡、SCが実行単位。

<a id="it-range-012"></a>
## IT-RANGE-012（統合済・実行対象外）

継続先：[IT-RANGE-001](524_ファイル・メディア・Range.md#it-range-001)。同一Range契約のparameter表へ。旧入力差/変更はcase-changesで追跡、SCが実行単位。

<a id="it-range-013"></a>
## IT-RANGE-013（統合済・実行対象外）

継続先：[IT-RANGE-001](524_ファイル・メディア・Range.md#it-range-001)。同一Range契約のparameter表へ。旧入力差/変更はcase-changesで追跡、SCが実行単位。

<a id="it-range-014"></a>
## IT-RANGE-014（統合済・実行対象外）

継続先：[IT-RANGE-001](524_ファイル・メディア・Range.md#it-range-001)。同一Range契約のparameter表へ。旧入力差/変更はcase-changesで追跡、SCが実行単位。

<a id="it-range-015"></a>
## IT-RANGE-015（統合済・実行対象外）

継続先：[IT-RANGE-001](524_ファイル・メディア・Range.md#it-range-001)。同一Range契約のparameter表へ。旧入力差/変更はcase-changesで追跡、SCが実行単位。

<a id="it-range-020"></a>
## IT-RANGE-020 download全長・20permit・abort・read失敗

仕様：**PENDING_DECISION** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧複合caseの4異なる終端を4SCへ明示し、未確定拒否statusだけISS-STREAMへ分離。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | download全長・20permit・abort・read失敗 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 10. Range解析・応答 > 10.2 範囲計算 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 11. Streaming中の異常 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 11. Streaming中の異常 ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-RANGE-020"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | Range無視200/Content-Length2097169/application/octet-stream/attachment。全bodyを独立pattern/hashと比較、2060。 | O-HTTP, O-WIRE, O-FS。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 20までは同時許可、21は待機0/Retry-After1/rejectioncount1。503又は429の設計選択はISS-STREAM、推測採用0。 | O-HTTP, O-WIRE, O-FS, O-METRIC, O-OS。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 全解放後新stream成功、FD/permitはbefore値。permit取得前の21本目fileopen0。 | O-HTTP, O-WIRE, O-FS, O-METRIC, O-OS。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 追加response0/INFO又はDEBUG/erroralert対象外。origin successfulwrite実数を記録しclientACKと同値必須にしない。全FD/permit解放。 | O-HTTP, O-FS, O-LOG, O-METRIC。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 接続close/追加errorbody0、既知sentbytes/errorcode、physicalpath0。全FD/permit解放、未確認closeは保全。 | O-HTTP, O-FS, O-LOG, O-OS。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, ISS-DATA を全解除。判断待ち：ISS-STREAM。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧複合caseの4異なる終端を4SCへ明示し、未確定拒否statusだけISS-STREAMへ分離。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-RANGE-020`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-range-020-s01"></a>
#### IT-RANGE-020-S01 / download

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entry": "GET /music/download/401",
  "asset_size": 2097169,
  "pattern": "i mod251",
  "Range": "bytes=0-0"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実API descriptor/認証からWeb full download。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-RANGE-020-S01/http.jsonl, IT-RANGE-020-S01/wire.jsonl, IT-RANGE-020-S01/fs.jsonl | Range無視200/Content-Length2097169/application/octet-stream/attachment。全bodyを独立pattern/hashと比較、2060。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-020-s02"></a>
#### IT-RANGE-020-S02 / stream21

種類：境界、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "streams": 20,
  "attempt": 21,
  "acquire_wait_ms": 0,
  "entry": "/animation/media/301",
  "body_hold": "既存20をreadbarrierで保持"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：20stream responseをbarrier保持。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 20streamは1本ずつ認証/descriptorを完了しbodybarrierで保持して積み上げる。全20保持後21本目を要求し、20を解放後新streamを要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-RANGE-020-S02/http.jsonl, IT-RANGE-020-S02/wire.jsonl, IT-RANGE-020-S02/fs.jsonl, IT-RANGE-020-S02/metric.jsonl, IT-RANGE-020-S02/os.jsonl | 20までは同時許可、21は待機0/Retry-After1/rejectioncount1。503又は429の設計選択はISS-STREAM、推測採用0。 |
| A03 | IT-RANGE-020-S02/http.jsonl, IT-RANGE-020-S02/wire.jsonl, IT-RANGE-020-S02/fs.jsonl, IT-RANGE-020-S02/metric.jsonl, IT-RANGE-020-S02/os.jsonl | 全解放後新stream成功、FD/permitはbefore値。permit取得前の21本目fileopen0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-020-s03"></a>
#### IT-RANGE-020-S03 / client_abort

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entry": "GET /audio/201",
  "abort": "headercommit直後"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：client abort。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. clientだけ切断しorigin送信既知byteと清掃を採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A04 | IT-RANGE-020-S03/http.jsonl, IT-RANGE-020-S03/fs.jsonl, IT-RANGE-020-S03/log.jsonl, IT-RANGE-020-S03/metric.jsonl | 追加response0/INFO又はDEBUG/erroralert対象外。origin successfulwrite実数を記録しclientACKと同値必須にしない。全FD/permit解放。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-range-020-s04"></a>
#### IT-RANGE-020-S04 / read_failure

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entry": "GET /audio/201",
  "fault": "headercommit後readI/O"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：held channel read I/O failure。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. headercommit後の保持channelreadを失敗。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A05 | IT-RANGE-020-S04/http.jsonl, IT-RANGE-020-S04/fs.jsonl, IT-RANGE-020-S04/log.jsonl, IT-RANGE-020-S04/os.jsonl | 接続close/追加errorbody0、既知sentbytes/errorcode、physicalpath0。全FD/permit解放、未確認closeは保全。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-050"></a>
## IT-FILE-050 native ENOENTとUNAVAILABLEの再生成分離

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

IT-FILE-040は不在をまとめており、close/crypto/保持inode内NoSuchFileを誤って再生成していないことを確認できない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | native ENOENTとUNAVAILABLEの再生成分離 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 > 6.1 APIの再送file確認と再生成（SSC-027） ／ ['SSC-027'] ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 > 6.1 APIの再送file確認と再生成（SSC-027） ／ ['SSC-027'] ／ commit `7147c428bb9d`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) SQL・transaction・lock・削除設計 > 4. Scenario・Speaker・Media query > 4.2 Scenario file/detail（IF-003/004） ／ ['PT-IDEM-SR01', 'SSC-027'] ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-050"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | root検査成功後native date ENOENTのみMISSING。元count/hash/metadata8一致時だけpublisher1。 | O-DB, O-FS, O-WIRE。実測/path/SHA/判定式はattemptへ記録 |
| A02 | descriptor更新は暗号body/keyVersionのみ。元completed_at/expires_at/state/ref不変。 | O-DB, O-FS, O-WIRE。実測/path/SHA/判定式はattemptへ記録 |
| A03 | UNAVAILABLE、publisher0、元Inbox/ready不変、MISSING補完0。 | O-DB, O-FS, O-WIRE。実測/path/SHA/判定式はattemptへ記録 |
| A04 | MISSINGへ確定0、publisher0、所有不明資源保全、成功reply0。 | O-DB, O-FS, O-WIRE, O-OS。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

IT-FILE-040は不在をまとめており、close/crypto/保持inode内NoSuchFileを誤って再生成していないことを確認できない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-050`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-050-s01"></a>
#### IT-FILE-050-S01 / missing_date

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "Inbox": "SCN COMPLETED F201",
  "physical": "root valid/date absent"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 元snapshot同tokenで再送。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-050-S01/db.jsonl, IT-FILE-050-S01/fs.jsonl, IT-FILE-050-S01/wire.jsonl | root検査成功後native date ENOENTのみMISSING。元count/hash/metadata8一致時だけpublisher1。 |
| A02 | IT-FILE-050-S01/db.jsonl, IT-FILE-050-S01/fs.jsonl, IT-FILE-050-S01/wire.jsonl | descriptor更新は暗号body/keyVersionのみ。元completed_at/expires_at/state/ref不変。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-050-s02"></a>
#### IT-FILE-050-S02 / held_nosuch

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "Inbox": "同上",
  "physical": "保持inode有",
  "fault": "callback NoSuchFile"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：held-inode callback error。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 保持inode取得後にreaderだけNoSuchFileを注入し再送。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A03 | IT-FILE-050-S02/db.jsonl, IT-FILE-050-S02/fs.jsonl, IT-FILE-050-S02/wire.jsonl | UNAVAILABLE、publisher0、元Inbox/ready不変、MISSING補完0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-050-s03"></a>
#### IT-FILE-050-S03 / missing_close_unknown

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "physical": "date ENOENT + root close failed"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：root close-after ENOENT failure。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 不在検出後close失敗を注入。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A04 | IT-FILE-050-S03/db.jsonl, IT-FILE-050-S03/fs.jsonl, IT-FILE-050-S03/wire.jsonl, IT-FILE-050-S03/os.jsonl | MISSINGへ確定0、publisher0、所有不明資源保全、成功reply0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-051"></a>
## IT-FILE-051 再生成metadata8/hash不一致と非公開

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧再生成caseは元snapshotからDBが変わった時の生成禁止/非更新を十分指定していない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | 再生成metadata8/hash不一致と非公開 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 > 6.1 APIの再送file確認と再生成（SSC-027） ／ ['SSC-027'] ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（1件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-051"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | publisher呼出0、ready新規0。元COMPLETEDをERRORへ上書き0、snapshot/期限不変。 | O-DB, O-FS, O-WIRE。実測/path/SHA/判定式はattemptへ記録 |
| A02 | stream SHA256不一致、publisher0。件数一致だけで合格0、元ready/snapshot保全。 | O-DB, O-FS, O-WIRE。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧再生成caseは元snapshotからDBが変わった時の生成禁止/非更新を十分指定していない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-051`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-051-s01"></a>
#### IT-FILE-051-S01 / metadata_changed

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "original_records": 201,
  "physical": "native missing",
  "DB": "8metadata中1field変更"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 元tokenで再送しpublisher入口を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-051-S01/db.jsonl, IT-FILE-051-S01/fs.jsonl, IT-FILE-051-S01/wire.jsonl | publisher呼出0、ready新規0。元COMPLETEDをERRORへ上書き0、snapshot/期限不変。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-051-s02"></a>
#### IT-FILE-051-S02 / body_changed

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "original_records": 201,
  "physical": "native missing",
  "DB": "record201のbyte1だけ変更・件数不変"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同token再送。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-051-S02/db.jsonl, IT-FILE-051-S02/fs.jsonl, IT-FILE-051-S02/wire.jsonl | stream SHA256不一致、publisher0。件数一致だけで合格0、元ready/snapshot保全。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-052"></a>
## IT-FILE-052 公開後fsync/close失敗のready保全

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

rename後の失敗を公開前rollbackと同一視しないため、再処理禁止/起動拒否を独立化。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | 公開後fsync/close失敗のready保全 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 > 6.1 APIの再送file確認と再生成（SSC-027） ／ ['SSC-027'] ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.3 API writerのdirectory capability（SSC-019） ／ ['SSC-019', 'SSC-049'] ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（2件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-052"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | readyは存在/hash一致のまま保全、delete/rename再試行0、成功descriptor送信0。 | O-FS, O-DB, O-WIRE, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A02 | UNKNOWNとして所有/公開receipt保持。再開前inode/DBを独立照合、無条件再公開0。 | O-FS, O-DB, O-WIRE, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | ready保全、close成功の捏造0。成功/readyを確定0、FD番号再利用を元ownerと誤認0。 | O-FS, O-OS, O-DB, O-WIRE。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

rename後の失敗を公開前rollbackと同一視しないため、再処理禁止/起動拒否を独立化。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-052`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-052-s01"></a>
#### IT-FILE-052-S01 / dirsync

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "file": "201*4800 bytes",
  "publish": "native no-replace succeeded"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：native publish-after/directory fsync fail。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 公開成功後directory fsyncを失敗させる。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-052-S01/fs.jsonl, IT-FILE-052-S01/db.jsonl, IT-FILE-052-S01/wire.jsonl, IT-FILE-052-S01/log.jsonl | readyは存在/hash一致のまま保全、delete/rename再試行0、成功descriptor送信0。 |
| A02 | IT-FILE-052-S01/fs.jsonl, IT-FILE-052-S01/db.jsonl, IT-FILE-052-S01/wire.jsonl, IT-FILE-052-S01/log.jsonl | UNKNOWNとして所有/公開receipt保持。再開前inode/DBを独立照合、無条件再公開0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-052-s02"></a>
#### IT-FILE-052-S02 / close

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "file": "同上",
  "publish": "success"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：published handle close unknown。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 公開成功後owned FD closeの確認を失敗させる。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A03 | IT-FILE-052-S02/fs.jsonl, IT-FILE-052-S02/os.jsonl, IT-FILE-052-S02/db.jsonl, IT-FILE-052-S02/wire.jsonl | ready保全、close成功の捏造0。成功/readyを確定0、FD番号再利用を元ownerと誤認0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-053"></a>
## IT-FILE-053 起動診断A/B collisionと所有限定清掃

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

既存起動/ファイルcaseに実no-replaceの二重公開診断と自分以外を消さない証拠がない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | 起動診断A/B collisionと所有限定清掃 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.4 起動時の診断専用probe（SSC-022） ／ ['SSC-022'] ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.4 起動時の診断専用probe（SSC-022） ／ ['SSC-022'] ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.4 起動時の診断専用probe（SSC-022） ／ ['SSC-022'] ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-053"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 2回目COLLISION、A/Bのbytes/hash不変、置換fallback0。診断descriptor/Inbox/業務message0。 | O-FS, O-OS, O-MQ, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 清掃対象はowned part/確認済診断Aだけ、other_ready保全。完全scanと全close後だけready。 | O-FS, O-OS, O-MQ, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 所有/公開不確定ready削除0、起動不合格、全root scan成功への算入0。 | O-FS, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

既存起動/ファイルcaseに実no-replaceの二重公開診断と自分以外を消さない証拠がない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-053`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-053-s01"></a>
#### IT-FILE-053-S01 / collision

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "startup": "exclusive probe実入口",
  "A_expected_bytes": 4800,
  "A_oracle": "公開前に独立採取したraw A/hashを固定",
  "B_oracle": "同UUID、Aと異なる固定pattern B。raw beforeを独立採取",
  "other_ready": "既存 unrelated1（before inode/hash固定）"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. exclusive startupでA公開→同UUID B公開→診断所有物だけ清掃。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-053-S01/fs.jsonl, IT-FILE-053-S01/os.jsonl, IT-FILE-053-S01/mq.jsonl, IT-FILE-053-S01/db.jsonl | 2回目COLLISION、A/Bのbytes/hash不変、置換fallback0。診断descriptor/Inbox/業務message0。 |
| A02 | IT-FILE-053-S01/fs.jsonl, IT-FILE-053-S01/os.jsonl, IT-FILE-053-S01/mq.jsonl, IT-FILE-053-S01/db.jsonl | 清掃対象はowned part/確認済診断Aだけ、other_ready保全。完全scanと全close後だけready。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-053-s02"></a>
#### IT-FILE-053-S02 / unknown

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "A": "published result unknown",
  "other_ready": "既存1"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：publication receipt loss。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 公開確認だけ喪失し起動診断を終える。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A03 | IT-FILE-053-S02/fs.jsonl, IT-FILE-053-S02/os.jsonl, IT-FILE-053-S02/log.jsonl | 所有/公開不確定ready削除0、起動不合格、全root scan成功への算入0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-054"></a>
## IT-FILE-054 Media N12とTransfer48MBの別上限

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧容量caseはTransfer専用上限をMediaへ誤適用する不備を検出できない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | Media N12とTransfer48MBの別上限 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.2 OS・TOCTOU対策 ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（1件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-054"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 206/body1 byte=15（0x0f、48000000 mod251の独立計算）、Content-Range bytes 48000000-48000000/48000001。48MBを理由に拒否0。 | O-HTTP, O-FS, O-WIRE。実測/path/SHA/判定式はattemptへ記録 |
| A02 | Transfer size/count不一致または48MB超過を拒否、本文送出0。Media許可でTransfer上限を緩めない。 | O-HTTP, O-FS, O-WIRE。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧容量caseはTransfer専用上限をMediaへ誤適用する不備を検出できない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-054`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-054-s01"></a>
#### IT-FILE-054-S01 / asset_large

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "Asset_size": 48000001,
  "bytes": "byte[i]=i%251",
  "descriptor": "positive N12",
  "auth": "valid owner"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実Assetをdescriptor経由でGET Range bytes=48000000-48000000。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-054-S01/http.jsonl, IT-FILE-054-S01/fs.jsonl, IT-FILE-054-S01/wire.jsonl | 206/body1 byte=15（0x0f、48000000 mod251の独立計算）、Content-Range bytes 48000000-48000000/48000001。48MBを理由に拒否0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-054-s02"></a>
#### IT-FILE-054-S02 / transfer_large

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "Transfer_size": 48000001,
  "descriptor_count": 10000,
  "record_length": 4800
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. Transfer descriptorを通常Web readerへ渡す。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-054-S02/http.jsonl, IT-FILE-054-S02/fs.jsonl, IT-FILE-054-S02/wire.jsonl | Transfer size/count不一致または48MB超過を拒否、本文送出0。Media許可でTransfer上限を緩めない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-055"></a>
## IT-FILE-055 表示filename256byteと実segment255byte

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧path攻撃caseとContent-Dispositionの表示metadataを分離し、実filename上限の誤流用を検出する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | 表示filename256byteと実segment255byte |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 9. Endpoint・HTTP header ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（1件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-055"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | attachmentのsafe ASCII fallbackとRFC5987 percent-encoded filename*。256byte表示metadataをpath解決に使用0。 | O-HTTP, O-FS。実測/path/SHA/判定式はattemptへ記録 |
| A02 | raw header連結/追加X-Injection header0、本文送出前拒否。storage inode不変更。 | O-HTTP, O-FS。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧path攻撃caseとContent-Dispositionの表示metadataを分離し、実filename上限の誤流用を検出する。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-055`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-055-s01"></a>
#### IT-FILE-055-S01 / display256

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "display": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "storage_segment": "asset.bin"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 正規descriptorの表示名だけ256ASCIIでdownload。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-055-S01/http.jsonl, IT-FILE-055-S01/fs.jsonl | attachmentのsafe ASCII fallbackとRFC5987 percent-encoded filename*。256byte表示metadataをpath解決に使用0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-055-s02"></a>
#### IT-FILE-055-S02 / CRLF

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "display": "a\r\nX-Injection: x",
  "storage_segment": "asset.bin"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 不正表示metadataを処理。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-055-S02/http.jsonl, IT-FILE-055-S02/fs.jsonl | raw header連結/追加X-Injection header0、本文送出前拒否。storage inode不変更。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-060"></a>
## IT-FILE-060 保持inode取得後のnamespace差替えと外部非参照

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧symlink拒否はopen前。open済capability後に名前を差替えるTOCTOUで別fileを読まない契約を独立判定。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | 保持inode取得後のnamespace差替えと外部非参照 |
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

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.3 API writerのdirectory capability（SSC-019） ／ ['SSC-019'] ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.2 OS・TOCTOU対策 ／ ['SSC-028'] ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（2件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-060"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | read channelは元保持inodeだけ。元path/同名evilへの再open/read0、E canaryがHTTP/DOM/logへ出現0。 | O-FS, O-HTTP, O-WIRE, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 保持metadata検証が成立して継続した場合のbodyは元G、変化/所有検証不成立なら503/非配信。いずれもevilを正常データへ採用0。未知のentry削除/自動repair0、ownedFD1回close。 | O-FS, O-HTTP, O-WIRE, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 既保持childは自分のinode能力だけ使用、差替えた親name再解決0。readerのmkdir/chmod/chgrp/rename/delete0、outside body送出0。 | O-FS, O-HTTP, O-OS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧symlink拒否はopen前。open済capability後に名前を差替えるTOCTOUで別fileを読まない契約を独立判定。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-060`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-060-s01"></a>
#### IT-FILE-060-S01 / entry_swap_after_hold

種類：競合、反復：100、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "good": "201record正規ready/独立hash G",
  "evil": "同size別body/private canary E",
  "barrier": "正規entry O_PATH保持後/readchannel前"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：entry保持後name swap。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 正規保持FDを観測後、専有fixtureが元entry名を退避し同名にevilを置く。read解放後inode/hash/HTTPとnativeopen対象を採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-060-S01/fs.jsonl, IT-FILE-060-S01/http.jsonl, IT-FILE-060-S01/wire.jsonl, IT-FILE-060-S01/os.jsonl, IT-FILE-060-S01/log.jsonl | read channelは元保持inodeだけ。元path/同名evilへの再open/read0、E canaryがHTTP/DOM/logへ出現0。 |
| A02 | IT-FILE-060-S01/fs.jsonl, IT-FILE-060-S01/http.jsonl, IT-FILE-060-S01/wire.jsonl, IT-FILE-060-S01/os.jsonl, IT-FILE-060-S01/log.jsonl | 保持metadata検証が成立して継続した場合のbodyは元G、変化/所有検証不成立なら503/非配信。いずれもevilを正常データへ採用0。未知のentry削除/自動repair0、ownedFD1回close。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-060-s02"></a>
#### IT-FILE-060-S02 / child_name_swap

種類：競合、反復：100、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "barrier": "date/child handle取得後",
  "old_parent": "元親capability",
  "new_name": "evil symlink"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：held child parent name swap。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 親側nameを差替え、既保持childでのみ次entryを解決させる。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A03 | IT-FILE-060-S02/fs.jsonl, IT-FILE-060-S02/http.jsonl, IT-FILE-060-S02/os.jsonl, IT-FILE-060-S02/log.jsonl | 既保持childは自分のinode能力だけ使用、差替えた親name再解決0。readerのmkdir/chmod/chgrp/rename/delete0、outside body送出0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-061"></a>
## IT-FILE-061 native FS前提とreadonly mountの起動gate

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

root symlinkとは別のプラットフォーム前提。Java path fallback/権限緩和でreadyにする違反を判定。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-OPS |
| 確認契約 | native FS前提とreadonly mountの起動gate |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.3 API writerのdirectory capability（SSC-019） ／ ['SSC-019'] ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.4 起動時の診断専用probe（SSC-022） ／ ['SSC-022', 'SSC-162'] ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（2件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-061"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | readiness false/業務受付0、通常rename/Path.normalize/privateFD reflection/unchecked network FSへfallback0。root mkdir/chmod/権限緩和0。 | O-OS, O-FS, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 取得済resourceだけを正規終了、未取得FDをclose0。UNKNOWNならそのownerと証拠を保持し次start重複0。 | O-OS, O-FS, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | readiness false/業務受付0、通常rename/Path.normalize/privateFD reflection/unchecked network FSへfallback0。root mkdir/chmod/権限緩和0。 | O-OS, O-FS, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 取得済resourceだけを正規終了、未取得FDをclose0。UNKNOWNならそのownerと証拠を保持し次start重複0。 | O-OS, O-FS, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A05 | readiness false/業務受付0、通常rename/Path.normalize/privateFD reflection/unchecked network FSへfallback0。root mkdir/chmod/権限緩和0。 | O-OS, O-FS, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A06 | 取得済resourceだけを正規終了、未取得FDをclose0。UNKNOWNならそのownerと証拠を保持し次start重複0。 | O-OS, O-FS, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A07 | readiness false/業務受付0、通常rename/Path.normalize/privateFD reflection/unchecked network FSへfallback0。root mkdir/chmod/権限緩和0。 | O-OS, O-FS, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A08 | 取得済resourceだけを正規終了、未取得FDをclose0。UNKNOWNならそのownerと証拠を保持し次start重複0。 | O-OS, O-FS, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A09 | readiness false/業務受付0、通常rename/Path.normalize/privateFD reflection/unchecked network FSへfallback0。root mkdir/chmod/権限緩和0。 | O-OS, O-FS, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A10 | 取得済resourceだけを正規終了、未取得FDをclose0。UNKNOWNならそのownerと証拠を保持し次start重複0。 | O-OS, O-FS, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, DEP-OPS-HOLD を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

root symlinkとは別のプラットフォーム前提。Java path fallback/権限緩和でreadyにする違反を判定。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-061`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-061-s01"></a>
#### IT-FILE-061-S01 / native_access_unavailable

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entry": "専有API/Web ordinary startup",
  "environment_fault": "native_access_unavailable",
  "root": "正規所有/非重複"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 指定前提だけを隔離環境で不成立にしstartup/probe/readiness/producer開始を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-061-S01/os.jsonl, IT-FILE-061-S01/fs.jsonl, IT-FILE-061-S01/mq.jsonl, IT-FILE-061-S01/log.jsonl | readiness false/業務受付0、通常rename/Path.normalize/privateFD reflection/unchecked network FSへfallback0。root mkdir/chmod/権限緩和0。 |
| A02 | IT-FILE-061-S01/os.jsonl, IT-FILE-061-S01/fs.jsonl, IT-FILE-061-S01/mq.jsonl, IT-FILE-061-S01/log.jsonl | 取得済resourceだけを正規終了、未取得FDをclose0。UNKNOWNならそのownerと証拠を保持し次start重複0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-061-s02"></a>
#### IT-FILE-061-S02 / procfs_unavailable

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entry": "専有API/Web ordinary startup",
  "environment_fault": "procfs_unavailable",
  "root": "正規所有/非重複"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 指定前提だけを隔離環境で不成立にしstartup/probe/readiness/producer開始を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A03 | IT-FILE-061-S02/os.jsonl, IT-FILE-061-S02/fs.jsonl, IT-FILE-061-S02/mq.jsonl, IT-FILE-061-S02/log.jsonl | readiness false/業務受付0、通常rename/Path.normalize/privateFD reflection/unchecked network FSへfallback0。root mkdir/chmod/権限緩和0。 |
| A04 | IT-FILE-061-S02/os.jsonl, IT-FILE-061-S02/fs.jsonl, IT-FILE-061-S02/mq.jsonl, IT-FILE-061-S02/log.jsonl | 取得済resourceだけを正規終了、未取得FDをclose0。UNKNOWNならそのownerと証拠を保持し次start重複0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-061-s03"></a>
#### IT-FILE-061-S03 / SDS_unsupported

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entry": "専有API/Web ordinary startup",
  "environment_fault": "SDS_unsupported",
  "root": "正規所有/非重複"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 指定前提だけを隔離環境で不成立にしstartup/probe/readiness/producer開始を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A05 | IT-FILE-061-S03/os.jsonl, IT-FILE-061-S03/fs.jsonl, IT-FILE-061-S03/mq.jsonl, IT-FILE-061-S03/log.jsonl | readiness false/業務受付0、通常rename/Path.normalize/privateFD reflection/unchecked network FSへfallback0。root mkdir/chmod/権限緩和0。 |
| A06 | IT-FILE-061-S03/os.jsonl, IT-FILE-061-S03/fs.jsonl, IT-FILE-061-S03/mq.jsonl, IT-FILE-061-S03/log.jsonl | 取得済resourceだけを正規終了、未取得FDをclose0。UNKNOWNならそのownerと証拠を保持し次start重複0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-061-s04"></a>
#### IT-FILE-061-S04 / Transfer_mount_ST_RDONLY

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entry": "専有API/Web ordinary startup",
  "environment_fault": "Transfer_mount_ST_RDONLY",
  "root": "正規所有/非重複"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 指定前提だけを隔離環境で不成立にしstartup/probe/readiness/producer開始を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A07 | IT-FILE-061-S04/os.jsonl, IT-FILE-061-S04/fs.jsonl, IT-FILE-061-S04/mq.jsonl, IT-FILE-061-S04/log.jsonl | readiness false/業務受付0、通常rename/Path.normalize/privateFD reflection/unchecked network FSへfallback0。root mkdir/chmod/権限緩和0。 |
| A08 | IT-FILE-061-S04/os.jsonl, IT-FILE-061-S04/fs.jsonl, IT-FILE-061-S04/mq.jsonl, IT-FILE-061-S04/log.jsonl | 取得済resourceだけを正規終了、未取得FDをclose0。UNKNOWNならそのownerと証拠を保持し次start重複0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-061-s05"></a>
#### IT-FILE-061-S05 / RENAME_NOREPLACE_unsupported

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "entry": "専有API/Web ordinary startup",
  "environment_fault": "RENAME_NOREPLACE_unsupported",
  "root": "正規所有/非重複"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 指定前提だけを隔離環境で不成立にしstartup/probe/readiness/producer開始を観測。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A09 | IT-FILE-061-S05/os.jsonl, IT-FILE-061-S05/fs.jsonl, IT-FILE-061-S05/mq.jsonl, IT-FILE-061-S05/log.jsonl | readiness false/業務受付0、通常rename/Path.normalize/privateFD reflection/unchecked network FSへfallback0。root mkdir/chmod/権限緩和0。 |
| A10 | IT-FILE-061-S05/os.jsonl, IT-FILE-061-S05/fs.jsonl, IT-FILE-061-S05/mq.jsonl, IT-FILE-061-S05/log.jsonl | 取得済resourceだけを正規終了、未取得FDをclose0。UNKNOWNならそのownerと証拠を保持し次start重複0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-062"></a>
## IT-FILE-062 UUID collisionの非上書きと有限生成

仕様：**PENDING_DECISION** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

旧write/forceケースのcollisionを独立化。CREATE_NEW part競合とpublish ready競合で保全対象が異なる。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | UUID collisionの非上書きと有限生成 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 5. Large-result生成algorithm ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 5. Large-result生成algorithm ／ ['SSC-019'] ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（2件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-062"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 既存partはtruncate/上書き/削除0。新UUIDのCREATE_NEWでだけ書く、正規ready1、元P0hash不変。 | O-FS, O-DB, O-WIRE, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A02 | NOREPLACE COLLISION、R0/P1双方bytes保全、通常rename/置換fallback0。成功descriptor0、無断collision先削除0。 | O-FS, O-HTTP, O-DB, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 無限UUID再生成/既存file消去0。上限到達は一時異常/成功descriptor0。総3又は4attemptの解釈だけISS-UUID-RETRY判断待ち、試験側で選ばない。 | O-FS, O-DB, O-WIRE, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：ISS-UUID-RETRY。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

旧write/forceケースのcollisionを独立化。CREATE_NEW part競合とpublish ready競合で保全対象が異なる。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-062`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-062-s01"></a>
#### IT-FILE-062-S01 / part_exists

種類：境界、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "UUID_sequence": "U0 existing.part→U1 fresh",
  "old_part_hash": "P0",
  "records": 201
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 専有UUID供給を2候補に固定し既存partと衝突させた後生成。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-062-S01/fs.jsonl, IT-FILE-062-S01/db.jsonl, IT-FILE-062-S01/wire.jsonl, IT-FILE-062-S01/log.jsonl | 既存partはtruncate/上書き/削除0。新UUIDのCREATE_NEWでだけ書く、正規ready1、元P0hash不変。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-062-s02"></a>
#### IT-FILE-062-S02 / ready_exists

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "UUID": "U0",
  "old_ready_hash": "R0",
  "new_part_hash": "P1!=R0"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 新part生成後、同U0 ready存在でnativepublishを試みる。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-062-S02/fs.jsonl, IT-FILE-062-S02/http.jsonl, IT-FILE-062-S02/db.jsonl, IT-FILE-062-S02/log.jsonl | NOREPLACE COLLISION、R0/P1双方bytes保全、通常rename/置換fallback0。成功descriptor0、無断collision先削除0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-062-s03"></a>
#### IT-FILE-062-S03 / all_collide

種類：境界、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "UUID_sequence": "全候補existing.part",
  "parenthetical_limit": "初回+再試行3の記述",
  "ambiguous_text": "最大3回新UUIDとの総attempt解釈"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 初回から衝突が続く有限供給を用い発行回数/失敗/元fileを採取。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A03 | IT-FILE-062-S03/fs.jsonl, IT-FILE-062-S03/db.jsonl, IT-FILE-062-S03/wire.jsonl, IT-FILE-062-S03/log.jsonl | 無限UUID再生成/既存file消去0。上限到達は一時異常/成功descriptor0。総3又は4attemptの解釈だけISS-UUID-RETRY判断待ち、試験側で選ばない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-063"></a>
## IT-FILE-063 Media7拡張子/MIMEとdisposition・毎GET認証

仕様：**PENDING_DECISION** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

既存IFの代表Mediaだけでは7組合せ/attachment HTTP変換と未定義署名追加の誤りを検出できない。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | Media7拡張子/MIMEとdisposition・毎GET認証 |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 8. Media認可・descriptor ／ ['SSC-004'] ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 8. Media認可・descriptor ／ ['SSC-030'] ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 8. Media認可・descriptor ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（3件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-063"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | inline MIME=audio/ogg、attachment対応時descriptorは同MIME/HTTPだけapplication/octet-stream。VideoAは許可しない。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 相対storage pathは物理解決専用、Browser/HTML/header/logへ漏洩0。各GETでfresh API認証/manifest確認、session cacheだけで配信0。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A03 | inline MIME=video/mp4、attachment対応時descriptorは同MIME/HTTPだけapplication/octet-stream。VideoAは許可しない。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 相対storage pathは物理解決専用、Browser/HTML/header/logへ漏洩0。各GETでfresh API認証/manifest確認、session cacheだけで配信0。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A05 | inline MIME=audio/mp4、attachment対応時descriptorは同MIME/HTTPだけapplication/octet-stream。VideoAは許可しない。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A06 | 相対storage pathは物理解決専用、Browser/HTML/header/logへ漏洩0。各GETでfresh API認証/manifest確認、session cacheだけで配信0。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A07 | inline MIME=audio/mpeg、attachment対応時descriptorは同MIME/HTTPだけapplication/octet-stream。VideoAは許可しない。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A08 | 相対storage pathは物理解決専用、Browser/HTML/header/logへ漏洩0。各GETでfresh API認証/manifest確認、session cacheだけで配信0。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A09 | inline MIME=audio/ogg、attachment対応時descriptorは同MIME/HTTPだけapplication/octet-stream。VideoAは許可しない。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A10 | 相対storage pathは物理解決専用、Browser/HTML/header/logへ漏洩0。各GETでfresh API認証/manifest確認、session cacheだけで配信0。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A11 | inline MIME=audio/wav、attachment対応時descriptorは同MIME/HTTPだけapplication/octet-stream。VideoAは許可しない。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A12 | 相対storage pathは物理解決専用、Browser/HTML/header/logへ漏洩0。各GETでfresh API認証/manifest確認、session cacheだけで配信0。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A13 | inline MIME=audio/flac、attachment対応時descriptorは同MIME/HTTPだけapplication/octet-stream。VideoAは許可しない。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A14 | 相対storage pathは物理解決専用、Browser/HTML/header/logへ漏洩0。各GETでfresh API認証/manifest確認、session cacheだけで配信0。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A15 | allowlist完全一致不成立でstream0/本文0。大文字/別名を推測受理0、署名field/HMACkeyをWebへ新配布して整合させる0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A16 | commoncodecとMediaResponseDecoderの終端分類はISS-FILE-ERROR-PATHへ、非配信/非更新と秘密非露出は独立確定。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A17 | allowlist完全一致不成立でstream0/本文0。大文字/別名を推測受理0、署名field/HMACkeyをWebへ新配布して整合させる0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A18 | commoncodecとMediaResponseDecoderの終端分類はISS-FILE-ERROR-PATHへ、非配信/非更新と秘密非露出は独立確定。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A19 | allowlist完全一致不成立でstream0/本文0。大文字/別名を推測受理0、署名field/HMACkeyをWebへ新配布して整合させる0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A20 | commoncodecとMediaResponseDecoderの終端分類はISS-FILE-ERROR-PATHへ、非配信/非更新と秘密非露出は独立確定。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A21 | allowlist完全一致不成立でstream0/本文0。大文字/別名を推測受理0、署名field/HMACkeyをWebへ新配布して整合させる0。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A22 | commoncodecとMediaResponseDecoderの終端分類はISS-FILE-ERROR-PATHへ、非配信/非更新と秘密非露出は独立確定。 | O-HTTP, O-WIRE, O-DB, O-FS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A23 | HTTP200/全長/application/octet-stream、descriptor側は元allowlist MIME。Rangeを与えても206応答0件、本文は独立全file hashと一致。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A24 | filenameは安全fallback+RFC5987、物理path/secret露出0。各GETのfresh API認証とmanifest確認、session権限cache代用0。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A25 | HTTP200/全長/application/octet-stream、descriptor側は元allowlist MIME。Rangeを与えても206応答0件、本文は独立全file hashと一致。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A26 | filenameは安全fallback+RFC5987、物理path/secret露出0。各GETのfresh API認証とmanifest確認、session権限cache代用0。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A27 | HTTP200/全長/application/octet-stream、descriptor側は元allowlist MIME。Rangeを与えても206応答0件、本文は独立全file hashと一致。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A28 | filenameは安全fallback+RFC5987、物理path/secret露出0。各GETのfresh API認証とmanifest確認、session権限cache代用0。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A29 | HTTP200/全長/application/octet-stream、descriptor側は元allowlist MIME。Rangeを与えても206応答0件、本文は独立全file hashと一致。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A30 | filenameは安全fallback+RFC5987、物理path/secret露出0。各GETのfresh API認証とmanifest確認、session権限cache代用0。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A31 | HTTP200/全長/application/octet-stream、descriptor側は元allowlist MIME。Rangeを与えても206応答0件、本文は独立全file hashと一致。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A32 | filenameは安全fallback+RFC5987、物理path/secret露出0。各GETのfresh API認証とmanifest確認、session権限cache代用0。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A33 | HTTP200/全長/application/octet-stream、descriptor側は元allowlist MIME。Rangeを与えても206応答0件、本文は独立全file hashと一致。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |
| A34 | filenameは安全fallback+RFC5987、物理path/secret露出0。各GETのfresh API認証とmanifest確認、session権限cache代用0。 | O-HTTP, O-WIRE, O-FS, O-DB。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：ISS-FILE-ERROR-PATH。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

既存IFの代表Mediaだけでは7組合せ/attachment HTTP変換と未定義署名追加の誤りを検出できない。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-063`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-063-s01"></a>
#### IT-FILE-063-S01 / Audio.ogg

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "type": "Audio",
  "storage_ext": ".ogg",
  "descriptor_MIME": "audio/ogg",
  "modes": "I",
  "size": 1048593,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 正規DBmetadata/manifest/実fileを整合させ、inline実descriptor→WebGETを一回要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-063-S01/http.jsonl, IT-FILE-063-S01/wire.jsonl, IT-FILE-063-S01/fs.jsonl, IT-FILE-063-S01/db.jsonl | inline MIME=audio/ogg、attachment対応時descriptorは同MIME/HTTPだけapplication/octet-stream。VideoAは許可しない。 |
| A02 | IT-FILE-063-S01/http.jsonl, IT-FILE-063-S01/wire.jsonl, IT-FILE-063-S01/fs.jsonl, IT-FILE-063-S01/db.jsonl | 相対storage pathは物理解決専用、Browser/HTML/header/logへ漏洩0。各GETでfresh API認証/manifest確認、session cacheだけで配信0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s02"></a>
#### IT-FILE-063-S02 / Video.mp4

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "type": "Video",
  "storage_ext": ".mp4",
  "descriptor_MIME": "video/mp4",
  "modes": "I",
  "size": 1048593,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. DBmetadata/manifest/実fileを整合させ、正規descriptor→実WebGET。I/A両対応は各HTTPをmode parameter subrowとして別証跡に記録。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A03 | IT-FILE-063-S02/http.jsonl, IT-FILE-063-S02/wire.jsonl, IT-FILE-063-S02/fs.jsonl, IT-FILE-063-S02/db.jsonl | inline MIME=video/mp4、attachment対応時descriptorは同MIME/HTTPだけapplication/octet-stream。VideoAは許可しない。 |
| A04 | IT-FILE-063-S02/http.jsonl, IT-FILE-063-S02/wire.jsonl, IT-FILE-063-S02/fs.jsonl, IT-FILE-063-S02/db.jsonl | 相対storage pathは物理解決専用、Browser/HTML/header/logへ漏洩0。各GETでfresh API認証/manifest確認、session cacheだけで配信0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s03"></a>
#### IT-FILE-063-S03 / Music.m4a

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "type": "Music",
  "storage_ext": ".m4a",
  "descriptor_MIME": "audio/mp4",
  "modes": "I",
  "size": 1048593,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 正規DBmetadata/manifest/実fileを整合させ、inline実descriptor→WebGETを一回要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A05 | IT-FILE-063-S03/http.jsonl, IT-FILE-063-S03/wire.jsonl, IT-FILE-063-S03/fs.jsonl, IT-FILE-063-S03/db.jsonl | inline MIME=audio/mp4、attachment対応時descriptorは同MIME/HTTPだけapplication/octet-stream。VideoAは許可しない。 |
| A06 | IT-FILE-063-S03/http.jsonl, IT-FILE-063-S03/wire.jsonl, IT-FILE-063-S03/fs.jsonl, IT-FILE-063-S03/db.jsonl | 相対storage pathは物理解決専用、Browser/HTML/header/logへ漏洩0。各GETでfresh API認証/manifest確認、session cacheだけで配信0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s04"></a>
#### IT-FILE-063-S04 / Music.mp3

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "type": "Music",
  "storage_ext": ".mp3",
  "descriptor_MIME": "audio/mpeg",
  "modes": "I",
  "size": 1048593,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 正規DBmetadata/manifest/実fileを整合させ、inline実descriptor→WebGETを一回要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A07 | IT-FILE-063-S04/http.jsonl, IT-FILE-063-S04/wire.jsonl, IT-FILE-063-S04/fs.jsonl, IT-FILE-063-S04/db.jsonl | inline MIME=audio/mpeg、attachment対応時descriptorは同MIME/HTTPだけapplication/octet-stream。VideoAは許可しない。 |
| A08 | IT-FILE-063-S04/http.jsonl, IT-FILE-063-S04/wire.jsonl, IT-FILE-063-S04/fs.jsonl, IT-FILE-063-S04/db.jsonl | 相対storage pathは物理解決専用、Browser/HTML/header/logへ漏洩0。各GETでfresh API認証/manifest確認、session cacheだけで配信0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s05"></a>
#### IT-FILE-063-S05 / Music.ogg

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "type": "Music",
  "storage_ext": ".ogg",
  "descriptor_MIME": "audio/ogg",
  "modes": "I",
  "size": 1048593,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 正規DBmetadata/manifest/実fileを整合させ、inline実descriptor→WebGETを一回要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A09 | IT-FILE-063-S05/http.jsonl, IT-FILE-063-S05/wire.jsonl, IT-FILE-063-S05/fs.jsonl, IT-FILE-063-S05/db.jsonl | inline MIME=audio/ogg、attachment対応時descriptorは同MIME/HTTPだけapplication/octet-stream。VideoAは許可しない。 |
| A10 | IT-FILE-063-S05/http.jsonl, IT-FILE-063-S05/wire.jsonl, IT-FILE-063-S05/fs.jsonl, IT-FILE-063-S05/db.jsonl | 相対storage pathは物理解決専用、Browser/HTML/header/logへ漏洩0。各GETでfresh API認証/manifest確認、session cacheだけで配信0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s06"></a>
#### IT-FILE-063-S06 / Music.wav

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "type": "Music",
  "storage_ext": ".wav",
  "descriptor_MIME": "audio/wav",
  "modes": "I",
  "size": 1048593,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 正規DBmetadata/manifest/実fileを整合させ、inline実descriptor→WebGETを一回要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A11 | IT-FILE-063-S06/http.jsonl, IT-FILE-063-S06/wire.jsonl, IT-FILE-063-S06/fs.jsonl, IT-FILE-063-S06/db.jsonl | inline MIME=audio/wav、attachment対応時descriptorは同MIME/HTTPだけapplication/octet-stream。VideoAは許可しない。 |
| A12 | IT-FILE-063-S06/http.jsonl, IT-FILE-063-S06/wire.jsonl, IT-FILE-063-S06/fs.jsonl, IT-FILE-063-S06/db.jsonl | 相対storage pathは物理解決専用、Browser/HTML/header/logへ漏洩0。各GETでfresh API認証/manifest確認、session cacheだけで配信0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s07"></a>
#### IT-FILE-063-S07 / Music.flac

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "type": "Music",
  "storage_ext": ".flac",
  "descriptor_MIME": "audio/flac",
  "modes": "I",
  "size": 1048593,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 正規DBmetadata/manifest/実fileを整合させ、inline実descriptor→WebGETを一回要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A13 | IT-FILE-063-S07/http.jsonl, IT-FILE-063-S07/wire.jsonl, IT-FILE-063-S07/fs.jsonl, IT-FILE-063-S07/db.jsonl | inline MIME=audio/flac、attachment対応時descriptorは同MIME/HTTPだけapplication/octet-stream。VideoAは許可しない。 |
| A14 | IT-FILE-063-S07/http.jsonl, IT-FILE-063-S07/wire.jsonl, IT-FILE-063-S07/fs.jsonl, IT-FILE-063-S07/db.jsonl | 相対storage pathは物理解決専用、Browser/HTML/header/logへ漏洩0。各GETでfresh API認証/manifest確認、session cacheだけで配信0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s08"></a>
#### IT-FILE-063-S08 / deny_8

種類：異常、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "baseline": "正規Media101",
  "mutation": "Music .mp3 with audio/mp4"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 指定組合せだけ不適合なdescriptor/metadataを実API又は隔離replydriverへ渡す。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A15 | IT-FILE-063-S08/http.jsonl, IT-FILE-063-S08/wire.jsonl, IT-FILE-063-S08/db.jsonl, IT-FILE-063-S08/fs.jsonl, IT-FILE-063-S08/log.jsonl | allowlist完全一致不成立でstream0/本文0。大文字/別名を推測受理0、署名field/HMACkeyをWebへ新配布して整合させる0。 |
| A16 | IT-FILE-063-S08/http.jsonl, IT-FILE-063-S08/wire.jsonl, IT-FILE-063-S08/db.jsonl, IT-FILE-063-S08/fs.jsonl, IT-FILE-063-S08/log.jsonl | commoncodecとMediaResponseDecoderの終端分類はISS-FILE-ERROR-PATHへ、非配信/非更新と秘密非露出は独立確定。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s09"></a>
#### IT-FILE-063-S09 / deny_9

種類：異常、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "baseline": "正規Media101",
  "mutation": "Audio .OGG uppercase alias"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 指定組合せだけ不適合なdescriptor/metadataを実API又は隔離replydriverへ渡す。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A17 | IT-FILE-063-S09/http.jsonl, IT-FILE-063-S09/wire.jsonl, IT-FILE-063-S09/db.jsonl, IT-FILE-063-S09/fs.jsonl, IT-FILE-063-S09/log.jsonl | allowlist完全一致不成立でstream0/本文0。大文字/別名を推測受理0、署名field/HMACkeyをWebへ新配布して整合させる0。 |
| A18 | IT-FILE-063-S09/http.jsonl, IT-FILE-063-S09/wire.jsonl, IT-FILE-063-S09/db.jsonl, IT-FILE-063-S09/fs.jsonl, IT-FILE-063-S09/log.jsonl | commoncodecとMediaResponseDecoderの終端分類はISS-FILE-ERROR-PATHへ、非配信/非更新と秘密非露出は独立確定。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s10"></a>
#### IT-FILE-063-S10 / deny_10

種類：異常、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "baseline": "正規Media101",
  "mutation": "Video disposition=A"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 指定組合せだけ不適合なdescriptor/metadataを実API又は隔離replydriverへ渡す。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A19 | IT-FILE-063-S10/http.jsonl, IT-FILE-063-S10/wire.jsonl, IT-FILE-063-S10/db.jsonl, IT-FILE-063-S10/fs.jsonl, IT-FILE-063-S10/log.jsonl | allowlist完全一致不成立でstream0/本文0。大文字/別名を推測受理0、署名field/HMACkeyをWebへ新配布して整合させる0。 |
| A20 | IT-FILE-063-S10/http.jsonl, IT-FILE-063-S10/wire.jsonl, IT-FILE-063-S10/db.jsonl, IT-FILE-063-S10/fs.jsonl, IT-FILE-063-S10/log.jsonl | commoncodecとMediaResponseDecoderの終端分類はISS-FILE-ERROR-PATHへ、非配信/非更新と秘密非露出は独立確定。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s11"></a>
#### IT-FILE-063-S11 / deny_11

種類：異常、反復：1、状態：PENDING_DECISION/NOT_EXECUTED。

```json
{
  "baseline": "正規Media101",
  "mutation": "unknown MIME application/x-test"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 指定組合せだけ不適合なdescriptor/metadataを実API又は隔離replydriverへ渡す。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A21 | IT-FILE-063-S11/http.jsonl, IT-FILE-063-S11/wire.jsonl, IT-FILE-063-S11/db.jsonl, IT-FILE-063-S11/fs.jsonl, IT-FILE-063-S11/log.jsonl | allowlist完全一致不成立でstream0/本文0。大文字/別名を推測受理0、署名field/HMACkeyをWebへ新配布して整合させる0。 |
| A22 | IT-FILE-063-S11/http.jsonl, IT-FILE-063-S11/wire.jsonl, IT-FILE-063-S11/db.jsonl, IT-FILE-063-S11/fs.jsonl, IT-FILE-063-S11/log.jsonl | commoncodecとMediaResponseDecoderの終端分類はISS-FILE-ERROR-PATHへ、非配信/非更新と秘密非露出は独立確定。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s12"></a>
#### IT-FILE-063-S12 / Audio.ogg_attachment

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "type": "Audio",
  "storage_ext": ".ogg",
  "descriptor_MIME": "audio/ogg",
  "modes": "A",
  "size": 1048593,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同じ正規metadataのattachment実descriptor→Webdownloadを一回要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A23 | IT-FILE-063-S12/http.jsonl, IT-FILE-063-S12/wire.jsonl, IT-FILE-063-S12/fs.jsonl, IT-FILE-063-S12/db.jsonl | HTTP200/全長/application/octet-stream、descriptor側は元allowlist MIME。Rangeを与えても206応答0件、本文は独立全file hashと一致。 |
| A24 | IT-FILE-063-S12/http.jsonl, IT-FILE-063-S12/wire.jsonl, IT-FILE-063-S12/fs.jsonl, IT-FILE-063-S12/db.jsonl | filenameは安全fallback+RFC5987、物理path/secret露出0。各GETのfresh API認証とmanifest確認、session権限cache代用0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s13"></a>
#### IT-FILE-063-S13 / Music.m4a_attachment

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "type": "Music",
  "storage_ext": ".m4a",
  "descriptor_MIME": "audio/mp4",
  "modes": "A",
  "size": 1048593,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同じ正規metadataのattachment実descriptor→Webdownloadを一回要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A25 | IT-FILE-063-S13/http.jsonl, IT-FILE-063-S13/wire.jsonl, IT-FILE-063-S13/fs.jsonl, IT-FILE-063-S13/db.jsonl | HTTP200/全長/application/octet-stream、descriptor側は元allowlist MIME。Rangeを与えても206応答0件、本文は独立全file hashと一致。 |
| A26 | IT-FILE-063-S13/http.jsonl, IT-FILE-063-S13/wire.jsonl, IT-FILE-063-S13/fs.jsonl, IT-FILE-063-S13/db.jsonl | filenameは安全fallback+RFC5987、物理path/secret露出0。各GETのfresh API認証とmanifest確認、session権限cache代用0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s14"></a>
#### IT-FILE-063-S14 / Music.mp3_attachment

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "type": "Music",
  "storage_ext": ".mp3",
  "descriptor_MIME": "audio/mpeg",
  "modes": "A",
  "size": 1048593,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同じ正規metadataのattachment実descriptor→Webdownloadを一回要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A27 | IT-FILE-063-S14/http.jsonl, IT-FILE-063-S14/wire.jsonl, IT-FILE-063-S14/fs.jsonl, IT-FILE-063-S14/db.jsonl | HTTP200/全長/application/octet-stream、descriptor側は元allowlist MIME。Rangeを与えても206応答0件、本文は独立全file hashと一致。 |
| A28 | IT-FILE-063-S14/http.jsonl, IT-FILE-063-S14/wire.jsonl, IT-FILE-063-S14/fs.jsonl, IT-FILE-063-S14/db.jsonl | filenameは安全fallback+RFC5987、物理path/secret露出0。各GETのfresh API認証とmanifest確認、session権限cache代用0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s15"></a>
#### IT-FILE-063-S15 / Music.ogg_attachment

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "type": "Music",
  "storage_ext": ".ogg",
  "descriptor_MIME": "audio/ogg",
  "modes": "A",
  "size": 1048593,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同じ正規metadataのattachment実descriptor→Webdownloadを一回要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A29 | IT-FILE-063-S15/http.jsonl, IT-FILE-063-S15/wire.jsonl, IT-FILE-063-S15/fs.jsonl, IT-FILE-063-S15/db.jsonl | HTTP200/全長/application/octet-stream、descriptor側は元allowlist MIME。Rangeを与えても206応答0件、本文は独立全file hashと一致。 |
| A30 | IT-FILE-063-S15/http.jsonl, IT-FILE-063-S15/wire.jsonl, IT-FILE-063-S15/fs.jsonl, IT-FILE-063-S15/db.jsonl | filenameは安全fallback+RFC5987、物理path/secret露出0。各GETのfresh API認証とmanifest確認、session権限cache代用0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s16"></a>
#### IT-FILE-063-S16 / Music.wav_attachment

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "type": "Music",
  "storage_ext": ".wav",
  "descriptor_MIME": "audio/wav",
  "modes": "A",
  "size": 1048593,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同じ正規metadataのattachment実descriptor→Webdownloadを一回要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A31 | IT-FILE-063-S16/http.jsonl, IT-FILE-063-S16/wire.jsonl, IT-FILE-063-S16/fs.jsonl, IT-FILE-063-S16/db.jsonl | HTTP200/全長/application/octet-stream、descriptor側は元allowlist MIME。Rangeを与えても206応答0件、本文は独立全file hashと一致。 |
| A32 | IT-FILE-063-S16/http.jsonl, IT-FILE-063-S16/wire.jsonl, IT-FILE-063-S16/fs.jsonl, IT-FILE-063-S16/db.jsonl | filenameは安全fallback+RFC5987、物理path/secret露出0。各GETのfresh API認証とmanifest確認、session権限cache代用0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-063-s17"></a>
#### IT-FILE-063-S17 / Music.flac_attachment

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "type": "Music",
  "storage_ext": ".flac",
  "descriptor_MIME": "audio/flac",
  "modes": "A",
  "size": 1048593,
  "pattern": "byte[i]=i%251"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 同じ正規metadataのattachment実descriptor→Webdownloadを一回要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A33 | IT-FILE-063-S17/http.jsonl, IT-FILE-063-S17/wire.jsonl, IT-FILE-063-S17/fs.jsonl, IT-FILE-063-S17/db.jsonl | HTTP200/全長/application/octet-stream、descriptor側は元allowlist MIME。Rangeを与えても206応答0件、本文は独立全file hashと一致。 |
| A34 | IT-FILE-063-S17/http.jsonl, IT-FILE-063-S17/wire.jsonl, IT-FILE-063-S17/fs.jsonl, IT-FILE-063-S17/db.jsonl | filenameは安全fallback+RFC5987、物理path/secret露出0。各GETのfresh API認証とmanifest確認、session権限cache代用0。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。


<a id="it-file-064"></a>
## IT-FILE-064 Web実UID/mountの書込拒否と属性deny

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

path文字列拒否/ハッシュ不一致とは異なるOS資格・属性責務。実library存在だけでwrite権限付与していないことを確認。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-OPS |
| 確認契約 | Web実UID/mountの書込拒否と属性deny |
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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 追加v3の具体仕様・HTTPname/source・独立field/config/schema oracle・再現/校正は515を優先。全T-v3はUNIMPLEMENTED、実在commandとして呼び出さない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.2 OS・TOCTOU対策 ／ 固定承認本文 ／ commit `7147c428bb9d`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.2 OS・TOCTOU対策 ／ 固定承認本文 ／ commit `7147c428bb9d`

意味監査：CONTRACT_REVIEWED。条件ID：JSONの `ss_condition_ids`（2件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "scenario_table": "data/scenarios.json",
  "contract_id": "ITC-FILE-064"
}
```

**操作順序・入口**

個別SCのstepsを順番に実行。途中再送・再開は同SC内で指定したIDだけを用いる。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 全4write操作拒否/更新0。readonly rootをbind-RWやchmod/chgrpで緩和0、Caddy DocumentRoot公開0。正規readは許可し、拒否全件だけで合格にしない。 | O-OS, O-FS, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 属性不成立はreadchannel前拒否、本文配信0。root/属性自動修復0、未知を通常file/size0へ補完0、元fileと他namespace保全。 | O-OS, O-FS, O-HTTP, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 属性不成立はreadchannel前拒否/本文0。自動chmod/chgrp/修復0、未知属性を既知成功へ補完0、元file/他namespace保全。 | O-OS, O-FS, O-HTTP, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 属性不成立はreadchannel前拒否/本文0。自動chmod/chgrp/修復0、未知属性を既知成功へ補完0、元file/他namespace保全。 | O-OS, O-FS, O-HTTP, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 属性不成立はreadchannel前拒否/本文0。自動chmod/chgrp/修復0、未知属性を既知成功へ補完0、元file/他namespace保全。 | O-OS, O-FS, O-HTTP, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A06 | 属性不成立はreadchannel前拒否/本文0。自動chmod/chgrp/修復0、未知属性を既知成功へ補完0、元file/他namespace保全。 | O-OS, O-FS, O-HTTP, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, DEP-OPS-HOLD を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

### 契約再監査と具体実行単位

path文字列拒否/ハッシュ不一致とは異なるOS資格・属性責務。実library存在だけでwrite権限付与していないことを確認。

既存代表caseではこの確定点・非更新条件の観測がなく合否を独立判定できない。失敗後に許される再処理が異なるため独立契約とする。同一契約内の値/状態差はSC行へ統合。

契約：`ITC-FILE-064`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。

<a id="it-file-064-s01"></a>
#### IT-FILE-064-S01 / Web_RO

種類：正常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "principal": "実Web Unit UID/GID/NSS/caps/mount",
  "targets": "専有Asset/Transferの正規existingfile",
  "operations": [
    "open WRITE",
    "create",
    "rename",
    "unlink"
  ]
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. 実Webと同一Unit hardening/UID/mount資格の承認済collectorで所有対象だけwrite試行、前後inode/hash/direntryを比較。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A01 | IT-FILE-064-S01/os.jsonl, IT-FILE-064-S01/fs.jsonl, IT-FILE-064-S01/log.jsonl | 全4write操作拒否/更新0。readonly rootをbind-RWやchmod/chgrpで緩和0、Caddy DocumentRoot公開0。正規readは許可し、拒否全件だけで合格にしない。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-064-s02"></a>
#### IT-FILE-064-S02 / wrong_attrs

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "file": "API認証/metadataは正規",
  "variants": "owner違いだけ"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. startup後に保持candidateのownerだけ不適合へ変え、通常Web readを一回要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A02 | IT-FILE-064-S02/os.jsonl, IT-FILE-064-S02/fs.jsonl, IT-FILE-064-S02/http.jsonl, IT-FILE-064-S02/log.jsonl | 属性不成立はreadchannel前拒否、本文配信0。root/属性自動修復0、未知を通常file/size0へ補完0、元fileと他namespace保全。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-064-s03"></a>
#### IT-FILE-064-S03 / attrs_GID違い

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "file": "正規candidate",
  "mutation": "GID違い"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. startup後に指定1属性だけ変え通常Webreadを要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A03 | IT-FILE-064-S03/os.jsonl, IT-FILE-064-S03/fs.jsonl, IT-FILE-064-S03/http.jsonl, IT-FILE-064-S03/log.jsonl | 属性不成立はreadchannel前拒否/本文0。自動chmod/chgrp/修復0、未知属性を既知成功へ補完0、元file/他namespace保全。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-064-s04"></a>
#### IT-FILE-064-S04 / attrs_mode0644

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "file": "正規candidate",
  "mutation": "mode0644"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. startup後に指定1属性だけ変え通常Webreadを要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A04 | IT-FILE-064-S04/os.jsonl, IT-FILE-064-S04/fs.jsonl, IT-FILE-064-S04/http.jsonl, IT-FILE-064-S04/log.jsonl | 属性不成立はreadchannel前拒否/本文0。自動chmod/chgrp/修復0、未知属性を既知成功へ補完0、元file/他namespace保全。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-064-s05"></a>
#### IT-FILE-064-S05 / attrs_nlink2

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "file": "正規candidate",
  "mutation": "nlink2"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. startup後に指定1属性だけ変え通常Webreadを要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A05 | IT-FILE-064-S05/os.jsonl, IT-FILE-064-S05/fs.jsonl, IT-FILE-064-S05/http.jsonl, IT-FILE-064-S05/log.jsonl | 属性不成立はreadchannel前拒否/本文0。自動chmod/chgrp/修復0、未知属性を既知成功へ補完0、元file/他namespace保全。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。

<a id="it-file-064-s06"></a>
#### IT-FILE-064-S06 / attrs_attribute未知

種類：異常、反復：1、状態：CONFIRMED/NOT_EXECUTED。

```json
{
  "file": "正規candidate",
  "mutation": "attribute未知"
}
```

実入口：実HTTP/Browser→既存IF。worker/保守は最終artifactの既存Unit/dispatcher入口（v2工具結線待ち）。故障/競合：なし。待機：同期HTTPは2秒、worker/Outboxは状態イベントを最大120秒待つ。watchdogはSLAの延長ではない。。

1. 予約manifestのsource/env/case/SC/active-job一致とHOLD解除証拠を確認。異なるjob/途中証跡があれば停止。
2. 独立cloneへinitial_stateを設定しbefore DB/queue/inode/pool/Unitと時刻を採取。
3. collectorと一回barrierをarmしack受領。
4. startup後に指定1属性だけ変え通常Webreadを要求。
5. 指定terminalイベント後に別接続・独立readerでafterとraw応答を採取。全assertionを評価。
6. failure/UNKNOWNを先に保全、注入を解除し所有範囲だけ復旧。cleanup readback成功後に予約を解除。

| Assertion | 個別証跡path（attempt root相対） | 判定predicate |
|---|---|---|
| A06 | IT-FILE-064-S06/os.jsonl, IT-FILE-064-S06/fs.jsonl, IT-FILE-064-S06/http.jsonl, IT-FILE-064-S06/log.jsonl | 属性不成立はreadchannel前拒否/本文0。自動chmod/chgrp/修復0、未知属性を既知成功へ補完0、元file/他namespace保全。 |

再開：同source/env/SC/fixture/job/receiptまで一致して再付着。不明な送信/commit後は独立照合してから続行。二度目のstart/送信禁止。 必須工具：UNIMPLEMENTED、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。
