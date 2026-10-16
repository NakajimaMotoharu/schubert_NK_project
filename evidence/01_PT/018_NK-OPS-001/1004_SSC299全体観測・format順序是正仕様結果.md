# SSC299全体観測・format順序是正仕様結果

Program NK-OPS-001、SS343/354/355、411、BUG1381/YKT1147。Production825e463334c43a5bc96f50db964df22e11758d1b。旧964e native/正式1964PT・53scopeは新sourceへ合算しない。

## 元job（再発行禁止）

PG4694-six-v1 / 元exec11464 / aru controller1704555・ticks18336989。開始2026-10-16T20:38:27.171189Z、archive SHA74d97051d37b3f18dc7eb7278104a4d5548a62212bb09778ba1f318812226256、payload SHA525ff8a0a169c19754f9bd78a98efc5d1cb9a89d991362d8c254b9e5ea50ac94。元begin/source/全argv/ticksを05:49/05:52JSTに読取照合しRUNNING・manifest未作成、API試験進行。期待3739PT/549suite/1646Mainは完走前の実合格数ではない。元artifactはPG379/pg4694-ssc299-six-v1、aru runs/PG4694-six-v1に保全。

BUG1381はreactor各moduleのformat→PTが、規約の全六format完走→いずれかのPTという順序を満たさない点。PTの失敗や実format不一致とは別である。元command/実結果を事後に先行済みへ書き換えず、正式受入へ繰り上げない。順序だけを理由とする全3739の再発行は行わず、元jobの終了値と全XMLを回収し、必要gateの適用を別評価する。

## 独立工具試験

環境Linux/Python3.14.4、branch dev-foundation、対象保存commitは本書・工具を含むGit履歴。commandは`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pyflakes3.4.0/runtime> python3 -B -m unittest whole_format_preflight_test pg4696_ssc299_whole_qualification_test pg4700_ssc299_static_test -v`。期待値は固定module/goal列、元手書き18case、literal byte/SHA/明示XML反例から算出し、Productionを期待値生成に使わない。

| Test ID | 入力・独立期待値 | 結果 |
|---|---|---|
| PT-OPS-FORMAT-ORDER | 実全体factoryのAST。全六format-only呼出しが唯一のPT processより前、二重instrument拒否 | 2工具試験内で合格 |
| PT-OPS-FORMAT-FAIL | exit1/bool、不変sourceの変異、foreign module。PTへ戻らず拒否、発行commandはformat-only一回。正常0/不変だけ通過 | 同上、合格 |
| PT-OPS-WHOLE-XML | 18case・6変更/2追加/1638不変の固定期待、failed/skipped/flaky/rerun/hash/未知class反例 | 既3工具試験合格 |
| PT-OPS-STATIC-ABI | 新全六Jarだけ4694へ束縛、第三者Jar不変、欠落六集合拒否。実emitted全global/static0、固定規則・F03未受入保持 | 2工具試験合格 |

7工具試験・F/E/S0（5と2の二commandで実行済み、後に同commandまとめ確認）。新Main/業務試験数やcoverageへ加算0。future `whole_format_preflight.compose`は停止中の元payloadへ適用せず、次に正当なfresh全体を要する際の工具へ接続する。実先行gateの適合証拠はまだないためBUG1381/YKT1147は未完。PG4700診断は元4694/4696資格後だけ発行し、未分類PMD・F03を0扱いしない。
