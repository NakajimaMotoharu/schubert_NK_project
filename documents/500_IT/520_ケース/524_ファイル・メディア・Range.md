# ファイル・メディア・Range 結合テストケース

編集正本は [cases.json](../data/cases.json)。この巻は自動生成。全件NOT_EXECUTED。SUPERSEDEDは旧ID履歴。PENDING_REAUDITは具体シナリオ再監査待ちで、仕様確定・実行可能へ算入しない。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, ISS-EMPTY, PREP-SEMANTIC を全解除。判断待ち：ISS-EMPTY。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-002"></a>
## IT-FILE-002 Scenario展開record境界 1

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-003"></a>
## IT-FILE-003 Scenario展開record境界 200

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-004"></a>
## IT-FILE-004 Scenario展開record境界 201

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-005"></a>
## IT-FILE-005 Scenario展開record境界 10000

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-006"></a>
## IT-FILE-006 Scenario展開record境界 10001

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-010"></a>
## IT-FILE-010 Large-result公開の故障 FP-FILE-WRITE

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-011"></a>
## IT-FILE-011 Large-result公開の故障 FP-FILE-FORCE

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-012"></a>
## IT-FILE-012 Large-result公開の故障 FP-FILE-PUBLISH-AFTER

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-020"></a>
## IT-FILE-020 descriptor/物理結合拒否 size+1

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-021"></a>
## IT-FILE-021 descriptor/物理結合拒否 hash1桁変更

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-022"></a>
## IT-FILE-022 descriptor/物理結合拒否 path ../outside.ready

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-023"></a>
## IT-FILE-023 descriptor/物理結合拒否 UUID/path不一致

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-024"></a>
## IT-FILE-024 descriptor/物理結合拒否 recordLength4799

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-025"></a>
## IT-FILE-025 descriptor/物理結合拒否 count10001

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-026"></a>
## IT-FILE-026 descriptor/物理結合拒否 root symlink

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-027"></a>
## IT-FILE-027 descriptor/物理結合拒否 date symlink

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-028"></a>
## IT-FILE-028 descriptor/物理結合拒否 entry symlink

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-029"></a>
## IT-FILE-029 descriptor/物理結合拒否 hardlink nlink2

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-030"></a>
## IT-FILE-030 descriptor/物理結合拒否 読取中内容改変

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-031"></a>
## IT-FILE-031 descriptor/物理結合拒否 record順逆転

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-file-040"></a>
## IT-FILE-040 SCN保存結果・欠落再生成・最終失効

仕様：**PENDING_REAUDIT** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, PREP-SEMANTIC を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 3. Class・method責務 ／ 固定承認本文 ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 10. Range解析・応答 > 10.2 範囲計算 ／ 固定承認本文 ／ commit `8b91944df582`

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

意味監査：LEGACY_PARTIAL。条件ID：JSONの `ss_condition_ids`（0件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

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

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, ISS-DATA, ISS-STREAM, PREP-SEMANTIC を全解除。判断待ち：ISS-DATA, ISS-STREAM。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 > 6.1 APIの再送file確認と再生成（SSC-027） ／ ['SSC-027'] ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 > 6.1 APIの再送file確認と再生成（SSC-027） ／ ['SSC-027'] ／ commit `8b91944df582`
- [332_SQL・transaction・lock・削除設計.md](<../../300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md>) SQL・transaction・lock・削除設計 > 4. Scenario・Speaker・Media query > 4.2 Scenario file/detail（IF-003/004） ／ ['PT-IDEM-SR01', 'SSC-027'] ／ commit `8b91944df582`

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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 > 6.1 APIの再送file確認と再生成（SSC-027） ／ ['SSC-027'] ／ commit `8b91944df582`

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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 6. Descriptor検証・取得 > 6.1 APIの再送file確認と再生成（SSC-027） ／ ['SSC-027'] ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.3 API writerのdirectory capability（SSC-019） ／ ['SSC-019', 'SSC-049'] ／ commit `8b91944df582`

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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.4 起動時の診断専用probe（SSC-022） ／ ['SSC-022'] ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.4 起動時の診断専用probe（SSC-022） ／ ['SSC-022'] ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.4 起動時の診断専用probe（SSC-022） ／ ['SSC-022'] ／ commit `8b91944df582`

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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 7. Path検証の実装規約 > 7.2 OS・TOCTOU対策 ／ 固定承認本文 ／ commit `8b91944df582`

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
| 自動化・未作成工具 | T-DRIVER/FIXTURE/FAULT/DB/WIRE/COLLECT/LOAD/RESUME-v2はUNIMPLEMENTED。公開実入口は既存IF/Unitを最終artifactで再確認し工具実装・レビュー後に限り使用。新規commandの存在を主張しない。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) 大容量結果file・media・Range配信設計 > 9. Endpoint・HTTP header ／ 固定承認本文 ／ commit `8b91944df582`

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
