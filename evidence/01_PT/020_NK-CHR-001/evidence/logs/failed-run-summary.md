# BUG-001 修正中run要約

## 1. 位置づけ

`pgpt-gate-20260901-01`～`04`は、BUG-001/YKT-001の不足観点を追加しながらfixtureとharnessをTDDで確立した修正中runであり、合格件数へ算入しない。部分artifactを正規Current evidenceと誤認しないようRepository外の作業領域へ移動し、削除せず保持した。

- 保持先: `/home/mini/codex/project1/work/characterization-failed-runs/20260901/`
- 正規成功run: `pgpt-gate-20260901-05`、`pgpt-gate-20260901-06`
- 秘密情報: Credential、password、raw token/session/cookie、private keyを含まないことをpath-only scanで確認

## 2. 修正中run

| Run | 初回結果 | 部分file数 | directory aggregate SHA-256 | 主な解消内容 |
|---|---:|---:|---|---|
| `pgpt-gate-20260901-01` | 3 failure / 2 error | 25 | `c69187dc647e01d5f9a4d24fca1f29d1cd5588056aeda6b287deec4980c9046b` | 新規fixture、DB停止復旧、Range、fallback、複数voice観点のharness不足を再現 |
| `pgpt-gate-20260901-02` | 1 failure / 1 error | 27 | `e366f4f15fa1a33ddf4b6bf90957ee6d8e3c8c3e8a60eacd5348f6b854907dd8` | fixture初期化・cleanupと期待値を独立oracleへ調整 |
| `pgpt-gate-20260901-03` | 1 failure / 1 error | 27 | `e366f4f15fa1a33ddf4b6bf90957ee6d8e3c8c3e8a60eacd5348f6b854907dd8` | controlled PostgreSQL停止・再開順序を修正 |
| `pgpt-gate-20260901-04` | 1 failure / 1 error | 27 | `e366f4f15fa1a33ddf4b6bf90957ee6d8e3c8c3e8a60eacd5348f6b854907dd8` | 最終fixture後条件とsupplemental assertionを修正 |

Aggregate SHA-256は各directory内のPOSIX相対pathをC locale昇順にし、`<file SHA-256><two spaces><relative path>\n`列全体をSHA-256化した値である。修正後はrun 05/06が各Current適用23/23 PASS、CHR-N01 metadata PASS、28 fileのrepeat差分0となった。
