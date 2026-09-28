# 179 NK-OPS-001 Cleanup子release限定実行結果

2026-09-28 JST、PG327/SSC-104、branch `dev-foundation`、対象source `ac709cda50478f877d254f85ade45fe3410f3298`。RD OPS-009/BAK-001、UI251、SS343 §6/341 §3。PT-OPS-ROOTBOM009（既存 ROOTBOM001～008/ROOTCTX001～009回帰）。Linux/JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0。

実行command: `./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl :schubert-nk-protocol,:schubert-nk-storage,:schubert-nk-bootstrap,:schubert-nk-api,:schubert-nk-web,:schubert-nk-batch -am clean test com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`、続けて同reactorで `org.jacoco:jacoco-maven-plugin:0.8.15:report`。両exit0。

| 入力・独立期待 | 実際・判定 |
|---|---|
| literal子Unit/自己PID・固定platform/build、異actor/変造/null。正しい子だけfresh release読取1増＋六列schema照会1、異actorはDB照会0 | ROOTBOM009 PASS。既存MORNING入口の専用契約も維持。選択Batch39件＋依存16件 F/E/S0、静的0。合成actorは実systemd証明でない |
| 変更method `verifyCleanup`、共用 `verifyFor` を全条件/拒否で網羅 | `verifyCleanup` line2/2・method1/1、`verifyFor` line9/9・branch4/4・method1/1。全`RootReleaseAdmission` classには旧native factory等のline/method欠けが残るためclass全体100%とはしない |
| security横断6module | clean全2,284PT/337suite、F/E/S0、6module SpotBugs0。PG328の同一source/runと共有、正式451 runではない |

証跡: `evidence/provisional/PG328-six-security/manifest.json` SHA256 `51aab47dff5ffaa9c38181de4e2996842aa0c7fc0b4b8bf18504367e80a2477c`、同dirのBatch JUnit/JaCoCo・全349file hash。JUnitのproperties/outputを除いた再構成XML、秘密pattern scan0、349file/source5 hash不整合0。関連BUG-310/311、YKT-243/244は181/台帳参照。実Root Cleanup Unit・署名原本/両backup/DELETE/Artemisは未受入、formal `858713c0bf310ae8bf62078b0a1cedbce4e968db`/`PT-WEB-20260925-24`は据置。
