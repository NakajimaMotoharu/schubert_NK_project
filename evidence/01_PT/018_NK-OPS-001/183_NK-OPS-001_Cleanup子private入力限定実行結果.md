# 183 NK-OPS-001 Cleanup子private入力限定実行結果

2026-09-28 JST、PG329/SSC-104、branch `dev-foundation`、source `6da91bf0affeb0481f10a40dffb4cbacf5ce5875`。RD OPS-009/BAK-001、UI251、SS341/343。PT-OPS-RBCR001～012。Linux host/JDK25.0.4/Maven3.9.12/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0。

| 入力・独立期待値 | 実際・判定 |
|---|---|
| SS343の固定private `cleanup-request` literal・root:root0500/0400・tmpfs/RO/ACL0・同device・1～256byte・close/inode安定。固定ASCII goldenをProduction encodeなしで算出 | RBCR001～012 全PASS。009～012は新たなcanonical/不正長・metadata/IO・再送の負境界。真正systemd Unit/private mountは本限定PTでは実測しない |
| 変更class全4指標 | `RootBatchCredentialReader` line53/53・branch56/56・method10/10・class1/1、`NativeIo` line4/4・method4/4・class1/1、定義branch0。missed0、除外0 |
| security共有変更のProduction回帰 | 6module clean 2,288PT/337suite、F/E/S0、SpotBugs全0、build exit0。内訳 Protocol80/Storage149/Bootstrap175/API742/Web555/Batch587。JaCoCo report exit0 |
| Production全体coverage100% | Protocol/Storage四指標missed0。Bootstrap branch37/line11/method4、API 1/19/3、Web 1/19/3、Batch branch0/line42/method19が未網羅。全module class missed0 |

証跡: `evidence/provisional/PG329-six-security/manifest.json` SHA256 `2ff0a01bcd9a8acb896d8bdc29c49e3fdaacc50271676d477115fc8b062b7c37`。実行日時・command・exit・入力・期待・実際・coverage・source/外部log SHAはmanifest参照。sanitized 337 JUnit XML＋coverage/static各6の349file、source2、外部log2のhashを全件照合し不一致0。JUnitのproperties/output/failure/skippedを除去し、保存証跡の秘密pattern scan0。raw logはGit外。

真正子Unit/固定`CREDENTIALS_DIRECTORY`、親連続M/A・同原本、両backup実artifact、実DELETE・Artemis依存・外部Web/API・CHRは未実施。正式source/run `858713c0bf310ae8bf62078b0a1cedbce4e968db`/`PT-WEB-20260925-24`、1964PT/53scope、暫定中心48.3%は据置。
