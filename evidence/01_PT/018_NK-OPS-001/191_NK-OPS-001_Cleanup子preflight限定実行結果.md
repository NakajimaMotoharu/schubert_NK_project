# 191 NK-OPS-001 Cleanup子preflight限定実行結果

2026-09-28 JST、PG333/SSC-104、branch `dev-foundation`、source `cc07715fc3617d873396bad479313a1386ff7e37`。RD OPS-009/BAK-001、UI251、SS341/343。PT-OPS-CPR001～004の5 method。Linux host/JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0。PostgreSQL fixtureは本選択順序試験では使用しない（PG332の別証跡参照）。

| 入力・独立期待値 | 実際・判定 |
|---|---|
| 固定公開request/activation/manifestと手書き順序 `gate→request→original→database→request→original→gate` | CPR001/004 PASS、再送でも同順序・DB観測1回、DELETE 0。選択Storage8＋Bootstrap8＋Batch5＝21PT F/E/S0、3module SpotBugs0 |
| 後段request/原本交換、別run/cutoff manifest、7段階IO故障、時計cutoff前、4割込、null | 交換・既知故障・時計/割込は固定非成功で後続呼出0。nullは契約違反として正常化なし |
| 変更`CleanupPreflight`の4指標 | line35/35・branch12/12・method6/6・class1/1、missed0、除外0。Batch JaCoCoはno-clean累積のため正式全体coverageに不使用 |

証跡: `evidence/provisional/PG333-selected/manifest.json` SHA256 `cfdcde023cace199673063b50592519bbb5f2fe78b9708e0804a90c1543438e3`。日時・command・exit・input/expected/actual・coverage・source2/log2 SHAはmanifest参照。Sanitized選択JUnit3＋static3＋Batch coverage1＝7file、source2、Git外原始log2の計11hash不一致0。JUnit properties/output/failure/skipped除去、保存証跡の秘密pattern scan0。

これはpackage限定port上の順序/失敗閉鎖試験。native root context/private credential/実DB sessionと結線した実Cleanup Unit、親M/A、DELETE/transfer/Artemis、Production全体coverage100%は未実行・未認定。全6最新回帰はPG332 `92ba3e1cf`の2,310PTであり、PG333の新sourceを含まない。正式認定source/run `858713c0bf310ae8bf62078b0a1cedbce4e968db`/`PT-WEB-20260925-24`、1964PT/53scope、中心48.3%据置。
