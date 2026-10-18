# Browser clock-domain／失敗履歴連結（BUG1454/YKT1218）

Program=NativeNkBrowserBusinessCohort.clockInstant/guestClock/run、PG5520/5522/5524/5526/5528。関連UI224/226、SS314/323/331/351/343、1129。Main/Test296/PG5430/BOM85fbは固定、上位仕様・Current baselineを変更しない。

## 独立期待値・前提

同boot79a3/同Root57ceefbe・同四普通ownerをguardで前後確認する。元Root5478真正WARNING10/1538.996795秒、5480全24/5482seal0を再利用し、Root/全回帰/署名を再発行しない。旧5488 actual1/[0,1]、UI12のみ出力、host時刻窓失敗を保持し全体合格へ加算しない。

SQL `clock_timestamp()` はDB後条件と同じguest時計であり、rowの最小/最大値や現在offsetから窓を作らない。新Browserはsource HTTP probeより前にlower clock、終了drain/after24捕捉後にupper clockを取得する。各SQL取得はhost単調時計で0～30秒、同process全体は0～600秒、timezone付き・順序・型・domain・exact値を独立Pythonで確認後、元pg3136全24 oracleを変更せず適用する。ゲスト時計を操作せず、wall逆行/欠測を不合格にする。

## Test ID／期待値

- OPS-GCLK-001: Java clockInstantの独立timezone/型/null/不正日付fixture。UTC正規化と拒否を確認、expectedをproduction methodで作らない。
- OPS-GCLK-002: 独立host+5秒/guest窓fixture、正常全24と境界外一件。正常だけpass、窓拡張なしで後者を拒否。
- OPS-GCLK-003: missing/host-only/row-derived clock、不一致、bool、timezone欠落、逆行、過大取得/全体時間を拒否。
- OPS-GCLK-004: 新driverはguest clock post、新only ready/output、12 UI期待値は従来独立oracleそのまま。源Main/Test変更0。
- OPS-GCLK-005: 元失敗のDB効果を保全用prefixとしてのみ検証。Rootsealの独立guest観測時刻～新lower clockを保全envelopeとするが、**旧有限時刻窓を回復・合格化しない**。元contextを独立fieldへそのまま保持し、oldActualExit1/oldFiniteTimeWindowQualified=false/failedCaseNormalized=falseを必須とする。
- OPS-GCLK-006: Root固定rows==旧before、旧after==新before、新after==現在24を厳密一致。欠落/異owner/独立anchor逆行を拒否。旧効果の保全照合と新一往復の厳密時刻条件を区別、粗いenvelopeに新試験合格の代用をさせない。
- OPS-GCLK-007: composed GUARD/ROOT_ORACLE/保存snapshot/新CHAINはexact byte/literal保持。新typed18は当composite成立後のみ。owned5496生成dir未作成を確認済みで、初回生成先を新5524/5526/5528へ明示結合し旧失敗receiptを使わない。

## 実行・証跡

`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B -m unittest pg5520_guest_clock_contract_test pg5529_guest_clock_chain_test pg5504_current_owned_test`

純粋fixtureはVM操作権限ではない。clean operator sourceを固定後、新5522 compile/独立Java oracle/独立Python/credential RO資格→5524同owner Browser一往復→5526読取composite→5528typed18→owned graphの順。元5486/5488を上書きせず新private directoryへ日時/source/operator/終了/入力hashを保存。private DB/cookie/token/passwordをGitへ保存しない。

実行結果/commit/hash/clock時刻とcounterは1136へ追補。Java/toolsの限定検証であり、Production coverage100/native/451/正式1964PT53scope/QA051finalを更新しない。未実行・skipped・元失敗を成功へ算入しない。旧source native88は保全のみ。
