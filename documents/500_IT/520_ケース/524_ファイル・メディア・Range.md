# ファイル・メディア・Range 結合テストケース

編集正本は [cases.json](../data/cases.json)。この巻は自動生成。全件NOT_EXECUTED。

全ケースは [512](../510_方針・準備/512_結合構成・環境・データ.md) の経路・環境・fixture・観測・C-ISOLATE と [541](../540_実行・管理/541_Codex実行・判定・証跡・再開.md) を参照する。共通CP-BASEの入力以外の初期状態・証跡・中断・後片付けは cases.json.profiles に一元化し、個別追加条件と併せて必須とする。

他巻：[インターフェース](521_インターフェース.md) / [トランザクション・データ](522_トランザクション・データ.md) / [認証・権限・セキュリティ](523_認証・権限・セキュリティ.md) / [ファイル・メディア・Range](524_ファイル・メディア・Range.md) / [運用・復旧・監視](525_運用・復旧・監視.md) / [MQ・非同期・容量](526_MQ・非同期・容量.md) / [性能・資源・Logout混在](527_性能・資源・Logout混在.md)

<a id="it-file-001"></a>
## IT-FILE-001 Scenario展開record境界 0

仕様：**PENDING_DECISION** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

Scenario展開record境界 0によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Scenario展開record境界 0 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [312_処理sequence・method・例外・transaction設計.md](<../../300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md>) §5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) §4.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §5/6/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（93件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "expanded_records": 0,
  "record_pattern": "entryは1開始、音声なしAudioSeq0、各本文IT本文<番号>、非表示paddingはUI234の固定表",
  "boundary_basis": "entry数でなくaudio展開後件数"
}
```

**操作順序・入口**

fixture件数を独立countしSF1のGET→wire/ready/DOMを一連で検証。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | SCNRSP01 mode I、inline件数0、wire byte数1984。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 200以下はtransfer公開0、201以上は1readyだけ、全工程のFD/lock解放、日中成功/失敗によるready削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, ISS-EMPTY を全解除。判断待ち：ISS-EMPTY。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-002"></a>
## IT-FILE-002 Scenario展開record境界 1

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

Scenario展開record境界 1によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Scenario展開record境界 1 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [312_処理sequence・method・例外・transaction設計.md](<../../300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md>) §5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) §4.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §5/6/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（93件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "expanded_records": 1,
  "record_pattern": "entryは1開始、音声なしAudioSeq0、各本文IT本文<番号>、非表示paddingはUI234の固定表",
  "boundary_basis": "entry数でなくaudio展開後件数"
}
```

**操作順序・入口**

fixture件数を独立countしSF1のGET→wire/ready/DOMを一連で検証。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | SCNRSP01 mode I、inline件数1、wire byte数6784。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 200以下はtransfer公開0、201以上は1readyだけ、全工程のFD/lock解放、日中成功/失敗によるready削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-003"></a>
## IT-FILE-003 Scenario展開record境界 200

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

Scenario展開record境界 200によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Scenario展開record境界 200 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [312_処理sequence・method・例外・transaction設計.md](<../../300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md>) §5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) §4.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §5/6/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（93件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "expanded_records": 200,
  "record_pattern": "entryは1開始、音声なしAudioSeq0、各本文IT本文<番号>、非表示paddingはUI234の固定表",
  "boundary_basis": "entry数でなくaudio展開後件数"
}
```

**操作順序・入口**

fixture件数を独立countしSF1のGET→wire/ready/DOMを一連で検証。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | SCNRSP01 mode I、inline件数200、wire byte数961984。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 200以下はtransfer公開0、201以上は1readyだけ、全工程のFD/lock解放、日中成功/失敗によるready削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-004"></a>
## IT-FILE-004 Scenario展開record境界 201

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

Scenario展開record境界 201によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Scenario展開record境界 201 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [312_処理sequence・method・例外・transaction設計.md](<../../300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md>) §5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) §4.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §5/6/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（93件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "expanded_records": 201,
  "record_pattern": "entryは1開始、音声なしAudioSeq0、各本文IT本文<番号>、非表示paddingはUI234の固定表",
  "boundary_basis": "entry数でなくaudio展開後件数"
}
```

**操作順序・入口**

fixture件数を独立countしSF1のGET→wire/ready/DOMを一連で検証。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | SCNRSP01 mode F、inline件数0、wire byte数1984。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | readyはheader/BOM/改行なし4800byte×201=964800byte、descriptor size/count/hash完全一致、全record順(EntrySeq,AudioSeq)独立表一致。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | DB snapshot TXはfile書込み前に終了、最終短write TXで最新認証/owner/Inboxを再検証してから応答。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 200以下はtransfer公開0、201以上は1readyだけ、全工程のFD/lock解放、日中成功/失敗によるready削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-005"></a>
## IT-FILE-005 Scenario展開record境界 10000

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

Scenario展開record境界 10000によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Scenario展開record境界 10000 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [312_処理sequence・method・例外・transaction設計.md](<../../300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md>) §5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) §4.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §5/6/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（93件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "expanded_records": 10000,
  "record_pattern": "entryは1開始、音声なしAudioSeq0、各本文IT本文<番号>、非表示paddingはUI234の固定表",
  "boundary_basis": "entry数でなくaudio展開後件数"
}
```

**操作順序・入口**

fixture件数を独立countしSF1のGET→wire/ready/DOMを一連で検証。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | SCNRSP01 mode F、inline件数0、wire byte数1984。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | readyはheader/BOM/改行なし4800byte×10000=48000000byte、descriptor size/count/hash完全一致、全record順(EntrySeq,AudioSeq)独立表一致。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | DB snapshot TXはfile書込み前に終了、最終短write TXで最新認証/owner/Inboxを再検証してから応答。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 200以下はtransfer公開0、201以上は1readyだけ、全工程のFD/lock解放、日中成功/失敗によるready削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-006"></a>
## IT-FILE-006 Scenario展開record境界 10001

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

Scenario展開record境界 10001によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Scenario展開record境界 10001 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [312_処理sequence・method・例外・transaction設計.md](<../../300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md>) §5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) §4.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §5/6/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（93件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "expanded_records": 10001,
  "record_pattern": "entryは1開始、音声なしAudioSeq0、各本文IT本文<番号>、非表示paddingはUI234の固定表",
  "boundary_basis": "entry数でなくaudio展開後件数"
}
```

**操作順序・入口**

fixture件数を独立countしSF1のGET→wire/ready/DOMを一連で検証。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 9001/HTTP503、部分成功のrecord/descriptor0、業務受付/ready公開0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-010"></a>
## IT-FILE-010 Large-result公開の故障 FP-FILE-WRITE

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

Large-result公開の故障 FP-FILE-WRITEによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Large-result公開の故障 FP-FILE-WRITE |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | FP-FILE-WRITE、別variantは既存targetを別内容で準備。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §5/7.3/7.4 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（82件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "records": 201,
  "bytes": 964800,
  "fault": "FP-FILE-WRITE"
}
```

**操作順序・入口**

201record SCNをbarrierで失敗→Web応答とpart/ready/Inboxを採取→同Message再操作。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 公開前失敗は503/一時異常、partは所有済のみbest-effort削除、削除失敗を原障害で隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 公開後response失敗のreadyは保全、再送で同snapshot/refを検証し二重業務更新0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 既存同UUID先はNOREPLACE collision、元ready/partのbyteを保持、通常rename/上書きfallback0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-011"></a>
## IT-FILE-011 Large-result公開の故障 FP-FILE-FORCE

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

Large-result公開の故障 FP-FILE-FORCEによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Large-result公開の故障 FP-FILE-FORCE |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | FP-FILE-FORCE、別variantは既存targetを別内容で準備。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §5/7.3/7.4 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（82件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "records": 201,
  "bytes": 964800,
  "fault": "FP-FILE-FORCE"
}
```

**操作順序・入口**

201record SCNをbarrierで失敗→Web応答とpart/ready/Inboxを採取→同Message再操作。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 公開前失敗は503/一時異常、partは所有済のみbest-effort削除、削除失敗を原障害で隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 公開後response失敗のreadyは保全、再送で同snapshot/refを検証し二重業務更新0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 既存同UUID先はNOREPLACE collision、元ready/partのbyteを保持、通常rename/上書きfallback0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-012"></a>
## IT-FILE-012 Large-result公開の故障 FP-FILE-PUBLISH-AFTER

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

Large-result公開の故障 FP-FILE-PUBLISH-AFTERによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | Large-result公開の故障 FP-FILE-PUBLISH-AFTER |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | FP-FILE-PUBLISH-AFTER、別variantは既存targetを別内容で準備。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §5/7.3/7.4 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（82件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "records": 201,
  "bytes": 964800,
  "fault": "FP-FILE-PUBLISH-AFTER"
}
```

**操作順序・入口**

201record SCNをbarrierで失敗→Web応答とpart/ready/Inboxを採取→同Message再操作。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 公開前失敗は503/一時異常、partは所有済のみbest-effort削除、削除失敗を原障害で隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 公開後response失敗のreadyは保全、再送で同snapshot/refを検証し二重業務更新0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 既存同UUID先はNOREPLACE collision、元ready/partのbyteを保持、通常rename/上書きfallback0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-020"></a>
## IT-FILE-020 descriptor/物理結合拒否 size+1

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

descriptor/物理結合拒否 size+1によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor/物理結合拒否 size+1 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 一項目変造。途中改変はreaderのhash→decode barrier、partial-value返却0。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §6/7/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（83件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "base": "201record/964800byte/正常descriptor",
  "one_mutation": "size+1"
}
```

**操作順序・入口**

正常実API descriptor/実fileの一項目だけ変え、Webの実readerからGETする。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 503、file不正部分のDOM表示0、FILE_DESCRIPTOR_INVALID又はFILE_INTEGRITY_MISMATCHを該当段で記録。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 不正な相手inodeをread/write/deleteしない、既存file/ready/Inbox保存結果の書換え0、FD全解放。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 正常controlは同入力の改変なしで201record完全表示、試験期待がreject全件に偏らない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-021"></a>
## IT-FILE-021 descriptor/物理結合拒否 hash1桁変更

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

descriptor/物理結合拒否 hash1桁変更によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor/物理結合拒否 hash1桁変更 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 一項目変造。途中改変はreaderのhash→decode barrier、partial-value返却0。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §6/7/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（83件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "base": "201record/964800byte/正常descriptor",
  "one_mutation": "hash1桁変更"
}
```

**操作順序・入口**

正常実API descriptor/実fileの一項目だけ変え、Webの実readerからGETする。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 503、file不正部分のDOM表示0、FILE_DESCRIPTOR_INVALID又はFILE_INTEGRITY_MISMATCHを該当段で記録。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 不正な相手inodeをread/write/deleteしない、既存file/ready/Inbox保存結果の書換え0、FD全解放。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 正常controlは同入力の改変なしで201record完全表示、試験期待がreject全件に偏らない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-022"></a>
## IT-FILE-022 descriptor/物理結合拒否 path ../outside.ready

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

descriptor/物理結合拒否 path ../outside.readyによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor/物理結合拒否 path ../outside.ready |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 一項目変造。途中改変はreaderのhash→decode barrier、partial-value返却0。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §6/7/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（83件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "base": "201record/964800byte/正常descriptor",
  "one_mutation": "path ../outside.ready"
}
```

**操作順序・入口**

正常実API descriptor/実fileの一項目だけ変え、Webの実readerからGETする。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 503、file不正部分のDOM表示0、FILE_DESCRIPTOR_INVALID又はFILE_INTEGRITY_MISMATCHを該当段で記録。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 不正な相手inodeをread/write/deleteしない、既存file/ready/Inbox保存結果の書換え0、FD全解放。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 正常controlは同入力の改変なしで201record完全表示、試験期待がreject全件に偏らない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-023"></a>
## IT-FILE-023 descriptor/物理結合拒否 UUID/path不一致

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

descriptor/物理結合拒否 UUID/path不一致によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor/物理結合拒否 UUID/path不一致 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 一項目変造。途中改変はreaderのhash→decode barrier、partial-value返却0。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §6/7/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（83件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "base": "201record/964800byte/正常descriptor",
  "one_mutation": "UUID/path不一致"
}
```

**操作順序・入口**

正常実API descriptor/実fileの一項目だけ変え、Webの実readerからGETする。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 503、file不正部分のDOM表示0、FILE_DESCRIPTOR_INVALID又はFILE_INTEGRITY_MISMATCHを該当段で記録。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 不正な相手inodeをread/write/deleteしない、既存file/ready/Inbox保存結果の書換え0、FD全解放。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 正常controlは同入力の改変なしで201record完全表示、試験期待がreject全件に偏らない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-024"></a>
## IT-FILE-024 descriptor/物理結合拒否 recordLength4799

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

descriptor/物理結合拒否 recordLength4799によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor/物理結合拒否 recordLength4799 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 一項目変造。途中改変はreaderのhash→decode barrier、partial-value返却0。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §6/7/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（83件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "base": "201record/964800byte/正常descriptor",
  "one_mutation": "recordLength4799"
}
```

**操作順序・入口**

正常実API descriptor/実fileの一項目だけ変え、Webの実readerからGETする。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 503、file不正部分のDOM表示0、FILE_DESCRIPTOR_INVALID又はFILE_INTEGRITY_MISMATCHを該当段で記録。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 不正な相手inodeをread/write/deleteしない、既存file/ready/Inbox保存結果の書換え0、FD全解放。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 正常controlは同入力の改変なしで201record完全表示、試験期待がreject全件に偏らない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-025"></a>
## IT-FILE-025 descriptor/物理結合拒否 count10001

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

descriptor/物理結合拒否 count10001によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor/物理結合拒否 count10001 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 一項目変造。途中改変はreaderのhash→decode barrier、partial-value返却0。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §6/7/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（83件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "base": "201record/964800byte/正常descriptor",
  "one_mutation": "count10001"
}
```

**操作順序・入口**

正常実API descriptor/実fileの一項目だけ変え、Webの実readerからGETする。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 503、file不正部分のDOM表示0、FILE_DESCRIPTOR_INVALID又はFILE_INTEGRITY_MISMATCHを該当段で記録。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 不正な相手inodeをread/write/deleteしない、既存file/ready/Inbox保存結果の書換え0、FD全解放。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 正常controlは同入力の改変なしで201record完全表示、試験期待がreject全件に偏らない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-026"></a>
## IT-FILE-026 descriptor/物理結合拒否 root symlink

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

descriptor/物理結合拒否 root symlinkによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor/物理結合拒否 root symlink |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 一項目変造。途中改変はreaderのhash→decode barrier、partial-value返却0。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §6/7/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（83件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "base": "201record/964800byte/正常descriptor",
  "one_mutation": "root symlink"
}
```

**操作順序・入口**

正常実API descriptor/実fileの一項目だけ変え、Webの実readerからGETする。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 503、file不正部分のDOM表示0、FILE_DESCRIPTOR_INVALID又はFILE_INTEGRITY_MISMATCHを該当段で記録。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 不正な相手inodeをread/write/deleteしない、既存file/ready/Inbox保存結果の書換え0、FD全解放。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 正常controlは同入力の改変なしで201record完全表示、試験期待がreject全件に偏らない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-027"></a>
## IT-FILE-027 descriptor/物理結合拒否 date symlink

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

descriptor/物理結合拒否 date symlinkによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor/物理結合拒否 date symlink |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 一項目変造。途中改変はreaderのhash→decode barrier、partial-value返却0。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §6/7/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（83件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "base": "201record/964800byte/正常descriptor",
  "one_mutation": "date symlink"
}
```

**操作順序・入口**

正常実API descriptor/実fileの一項目だけ変え、Webの実readerからGETする。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 503、file不正部分のDOM表示0、FILE_DESCRIPTOR_INVALID又はFILE_INTEGRITY_MISMATCHを該当段で記録。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 不正な相手inodeをread/write/deleteしない、既存file/ready/Inbox保存結果の書換え0、FD全解放。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 正常controlは同入力の改変なしで201record完全表示、試験期待がreject全件に偏らない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-028"></a>
## IT-FILE-028 descriptor/物理結合拒否 entry symlink

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

descriptor/物理結合拒否 entry symlinkによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor/物理結合拒否 entry symlink |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 一項目変造。途中改変はreaderのhash→decode barrier、partial-value返却0。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §6/7/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（83件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "base": "201record/964800byte/正常descriptor",
  "one_mutation": "entry symlink"
}
```

**操作順序・入口**

正常実API descriptor/実fileの一項目だけ変え、Webの実readerからGETする。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 503、file不正部分のDOM表示0、FILE_DESCRIPTOR_INVALID又はFILE_INTEGRITY_MISMATCHを該当段で記録。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 不正な相手inodeをread/write/deleteしない、既存file/ready/Inbox保存結果の書換え0、FD全解放。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 正常controlは同入力の改変なしで201record完全表示、試験期待がreject全件に偏らない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-029"></a>
## IT-FILE-029 descriptor/物理結合拒否 hardlink nlink2

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

descriptor/物理結合拒否 hardlink nlink2によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor/物理結合拒否 hardlink nlink2 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 一項目変造。途中改変はreaderのhash→decode barrier、partial-value返却0。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §6/7/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（83件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "base": "201record/964800byte/正常descriptor",
  "one_mutation": "hardlink nlink2"
}
```

**操作順序・入口**

正常実API descriptor/実fileの一項目だけ変え、Webの実readerからGETする。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 503、file不正部分のDOM表示0、FILE_DESCRIPTOR_INVALID又はFILE_INTEGRITY_MISMATCHを該当段で記録。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 不正な相手inodeをread/write/deleteしない、既存file/ready/Inbox保存結果の書換え0、FD全解放。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 正常controlは同入力の改変なしで201record完全表示、試験期待がreject全件に偏らない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-030"></a>
## IT-FILE-030 descriptor/物理結合拒否 読取中内容改変

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

descriptor/物理結合拒否 読取中内容改変によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor/物理結合拒否 読取中内容改変 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 一項目変造。途中改変はreaderのhash→decode barrier、partial-value返却0。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §6/7/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（83件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "base": "201record/964800byte/正常descriptor",
  "one_mutation": "読取中内容改変"
}
```

**操作順序・入口**

正常実API descriptor/実fileの一項目だけ変え、Webの実readerからGETする。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 503、file不正部分のDOM表示0、FILE_DESCRIPTOR_INVALID又はFILE_INTEGRITY_MISMATCHを該当段で記録。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 不正な相手inodeをread/write/deleteしない、既存file/ready/Inbox保存結果の書換え0、FD全解放。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 正常controlは同入力の改変なしで201record完全表示、試験期待がreject全件に偏らない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-031"></a>
## IT-FILE-031 descriptor/物理結合拒否 record順逆転

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

descriptor/物理結合拒否 record順逆転によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | descriptor/物理結合拒否 record順逆転 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 一項目変造。途中改変はreaderのhash→decode barrier、partial-value返却0。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §6/7/14.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [322_固定長電文codec実装設計.md](<../../300_SS/320_メッセージング/322_固定長電文codec実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（83件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "base": "201record/964800byte/正常descriptor",
  "one_mutation": "record順逆転"
}
```

**操作順序・入口**

正常実API descriptor/実fileの一項目だけ変え、Webの実readerからGETする。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 503、file不正部分のDOM表示0、FILE_DESCRIPTOR_INVALID又はFILE_INTEGRITY_MISMATCHを該当段で記録。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 不正な相手inodeをread/write/deleteしない、既存file/ready/Inbox保存結果の書換え0、FD全解放。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 正常controlは同入力の改変なしで201record完全表示、試験期待がreject全件に偏らない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-040"></a>
## IT-FILE-040 SCN保存結果・欠落再生成・最終失効

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

SCN保存結果・欠落再生成・最終失効によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | SCN保存結果・欠落再生成・最終失効 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | FP-FILE-PUBLISH-AFTER/最終write前の失効barrier、元snapshot全値を別observerで固定。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [324_Outbox・Inbox・冪等性・再送設計.md](<../../300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md>) §6.3/7.1 ／ SSC026/027 ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §6.1 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) §4.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（121件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "records": 201,
  "variants": [
    "ready存在",
    "date/ready ENOENT",
    "hash不正",
    "再生成途中にAPI失効",
    "snapshot metadata/hash不一致"
  ]
}
```

**操作順序・入口**

初回保存後、専用fixture上だけmissingを作る→同Message replay→file I/O中失効又はsnapshot不一致を別runで注入。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 存在正常はread-only検証だけ、ENOENT確定だけ再生成1回。同内容hash/count/metadata一致、descriptor変更はkey/date/UUIDだけ許可。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 更新はInboxのresponse_body_encrypted/response_key_version2列だけ、他17列・completed/expires保持。hash不正/close不明はMISSINGへ補完せず再生成0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | 最終認証失効は0102/新descriptor応答0、I/O中DB TX/rowlock0、既存成功をERRORへ上書き0、公開済ready削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-001"></a>
## IT-RANGE-001 none

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

noneによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | none |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": null,
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP200/Content-Length=2097169/Content-Range=なし、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;0:2097169&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-002"></a>
## IT-RANGE-002 one

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

oneによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | one |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": "bytes=0-0",
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP206/Content-Length=1/Content-Range=bytes 0-0/2097169、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;0:1&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-003"></a>
## IT-RANGE-003 1MiB

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

1MiBによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | 1MiB |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": "bytes=0-1048575",
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP206/Content-Length=1048576/Content-Range=bytes 0-1048575/2097169、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;0:1048576&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-004"></a>
## IT-RANGE-004 over1MiB

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

over1MiBによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | over1MiB |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": "bytes=0-1048576",
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP206/Content-Length=1048576/Content-Range=bytes 0-1048575/2097169、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;0:1048576&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-005"></a>
## IT-RANGE-005 open

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

openによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | open |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": "bytes=1048576-",
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP206/Content-Length=1048576/Content-Range=bytes 1048576-2097151/2097169、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;1048576:2097152&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-006"></a>
## IT-RANGE-006 suffix1

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

suffix1によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | suffix1 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": "bytes=-1",
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP206/Content-Length=1/Content-Range=bytes 2097168-2097168/2097169、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;2097168:2097169&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-007"></a>
## IT-RANGE-007 suffixbig

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

suffixbigによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | suffixbig |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": "bytes=-3000000",
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP206/Content-Length=1048576/Content-Range=bytes 0-1048575/2097169、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;0:1048576&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-008"></a>
## IT-RANGE-008 last

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

lastによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | last |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": "bytes=2097168-2097168",
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP206/Content-Length=1/Content-Range=bytes 2097168-2097168/2097169、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;2097168:2097169&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-009"></a>
## IT-RANGE-009 atTotal

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

atTotalによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | atTotal |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": "bytes=2097169-",
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP416/Content-Length=0/Content-Range=bytes */2097169、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;None:None&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-010"></a>
## IT-RANGE-010 reverse

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

reverseによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | reverse |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": "bytes=10-9",
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP416/Content-Length=0/Content-Range=bytes */2097169、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;None:None&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-011"></a>
## IT-RANGE-011 invalid

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

invalidによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | invalid |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": "bytes=a-b",
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP416/Content-Length=0/Content-Range=bytes */2097169、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;None:None&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-012"></a>
## IT-RANGE-012 overflow

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

overflowによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | overflow |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": "bytes=9223372036854775808-",
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP416/Content-Length=0/Content-Range=bytes */2097169、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;None:None&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-013"></a>
## IT-RANGE-013 multiValidFirst

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

multiValidFirstによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | multiValidFirst |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": "bytes=0-0,a-b",
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP206/Content-Length=1/Content-Range=bytes 0-0/2097169、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;0:1&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-014"></a>
## IT-RANGE-014 multiInvalidFirst

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

multiInvalidFirstによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | multiInvalidFirst |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": "bytes=a-b,0-0",
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP416/Content-Length=0/Content-Range=bytes */2097169、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;None:None&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-015"></a>
## IT-RANGE-015 unknownUnit

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

unknownUnitによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | unknownUnit |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 1同期操作はWeb待ち2秒。case watchdog120秒。2秒超を120秒以内成功で救済しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9/10/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.4/5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（36件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "url": "GET /animation/media/opening",
  "Range": "items=0-0",
  "total_bytes": 2097169,
  "pattern": "byte[i]=i mod251"
}
```

**操作順序・入口**

U1を正規Login→GET媒体を一回、同条件HEADも別独立requestで行う。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | HTTP416/Content-Length=0/Content-Range=bytes */2097169、206 body上限1048576byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | GET bodyは独立生成patternのslice&#91;None:None&#93;と全byte/hash一致（416はbody0）。HEADは同status/同Content-Length/同Rangeでbody0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | descriptor要求/現在API認証はGET/HEADそれぞれ実行、Path/秘密漏出0、stream permit/FD leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-range-020"></a>
## IT-RANGE-020 download・stream20/21・abort

仕様：**PENDING_DECISION** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

download・stream20/21・abortによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | download・stream20/21・abort |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 20個の自己所有client/barrier、21を一回投入、abort1件、残りの正常完走を確認。 |
| 反復 | 1 |
| timeout・中断 | stream watchdog180秒。製品に全媒体転送完了p95を追加しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §9〜11/14.2 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（49件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "download": "/music/download/<固定trackId> Range bytes=0-0",
  "streams": [
    20,
    21
  ],
  "Retry-After": "1"
}
```

**操作順序・入口**

20streamをbody途中barrierで保持→21番目開始→1件client abort→次request→全解放。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | downloadはRange無視200全長/attachment/application/octet-stream、安全UTF8filename、独立全file hash一致。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 20まで同時許可、21はwait0で即時拒否/Retry-After1、503/429の設計選択未確定はISS-STREAM。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | abortは追加response0/エラーalert対象外、headercommit後read失敗は接続close/sent origin bytesだけ記録、全permit/FD回収。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, ISS-DATA, ISS-STREAM を全解除。判断待ち：ISS-DATA, ISS-STREAM。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。
