# 969 NK-OPS-001 failed Root読取診断仕様・結果

2026-10-16。対象Production 7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e / PG3976 / BOM0a409301、SS343/353 SSC286、RD OPS009/FIL006/SYS004、UI251、451/487、BUG1332～1335/YKT1098～1101。診断工具はProduction PTへ加点しない。正式1964PT/53scope、旧個別17/190、工数完成率null、QA051 final保留を維持する。

## 独立期待値・実行範囲

- PT-OPS-PROFILE4050: 実LinuxSystemdQueryの固定API七項目を5回読取、出力は固定phase/count/nanosだけ。署名/source/boot/同API世代の前後一致。実0、合計240641172ns。Root/許可の仮構成0、HTTP/DB/signal0。
- PT-OPS-PRESERVE4052: 実署名187/固定ten Unit・元Root timeout143/同普通四actorを再認証。全24の独立RO snapshotを二回比較、原本/Backup/鍵/旧proof/nativeを私有保全。実0、全24同値・四actor同世代・DB普通3/管理advisory0/flock0・native50 exec。親.done10は正常親証拠にしない。私有sha732bec2c19cadc926ca64efdeffa08aa9b167359c36131b889e3656c473c6da6。
- PT-OPS-PROFILE4054/4056: 全100回の属性/ACL/FS/readonly・factory/固定proc FS読取。旧4054 compile1（BUG1333）、抑制せず固定SpotBugs annotation4.10.4/SHA28fa4bef…へ是正。欠落/bit改変拒否の純2、new-only4056 lintWerror0/profile0。各100回合計6.5～38.8ms、観測値であって期限保証ではない。
- PT-OPS-PROFILE4058/4060: 4058 compile0、IPv4片family baselineでrun1（Java前、BUG1334）。既pg3509の実両family正規化/両端一意性をそのまま再利用。4060 compile0・全4class hash固定、旧class/Javaの改変無し。4060 run1はOID JSON型誤認（BUG1335）によりREADY後・graph前で拒否。診断stdin ABORTだけで返却し、freshで旧Java消滅・普通DB3/advisory0を確認。旧失敗・予約は不変。
- PT-OPS-PROFILE4064: OIDの独立SQL vector（oid=JSON string、bigint=JSON number）に基づき観測SQLを明示bigint cast。既4060のJava/annotation/全classを完全hash照合して利用し、再compileしない。別new-only管理scopeのM→A/実batch RO/本人backend・71419602/両端socket・heartbeat・十Ref・32設定/全24/原本等を独立observerで前後照合。実0。first graph310791246ns、second146414609ns、retained二回4848447ns、属性/ACL/FS/readonly各5012回、実file open476回。前後私有snapshot同sha c1983a08d612b4e710000912bc3e1636776105607900af00248187571196e1d9。全四actor/Unit/config/24表/原本Backup/native不変、本人DB/advisory/M-A消失・十Ref正常返却。Root timeout143を正常化しない。

fixtureは固定独立kernel TCP vector・異role/余剰/欠落/両端inode/IPv4-mapped/重複/foreign advisory/flock、全保全分類・DB row改変を使用する。Production自身からexpectedを生成しない。4058純4、4060純6（既4を含む）、4064純6（同じ既4を含む）は工具検査であり16件の新Production PTではない。

## 再現command・環境・証跡

`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/<各pg番号の工具>.py`。原slotはnew-only・再実行禁止。各元manifestのaction/実command/exit/source/hashを参照し、再現が必要な場合は同一成功操作の再演ではなく新しい明示診断scopeを定義する。Java25.0.4、guest Linux boot79a3260a、compile -Xlint:all -Werror/sourcepath空、暗黙JAVA_OPTIONSを除去。Java sourceSHA d863da5b…、4060 compileSHA15e9876c…、annotationSHA28fa4bef…、全class hashを公開manifestへ保持する。

公開 `evidence/provisional/PG4066-failed-root-readonly-diagnostics-v1/manifest.json` SHA3c16d60c6b49681bf8932b1e966eaebbdca4c835d607462daf312d0af5795984、元PG379各new-only manifest/guest私有原値は非公開。DB row/credential/password/raw session/cookie/token/鍵/生FD dumpをGitへ輸出しない。ツールsource修正87619d365、修正前BUG起票f22ed594a/cdd6597d4/9f408be04、SSC登録4b734273c・設計7bd40d1a1/899091424・main PR131/merge0ea6563576bc0bd6406262662f8a809abc129414。PR添付はアプリ既存100件上限で失敗、既存添付を削除せずURLを保持する。

## 判定と残件

上記readonly診断scopeのみ成立。全fresh原本走査自体は32～40秒の完了proofの主因ではなく、他の同peer/DB/manager/TLS等の内訳は未確定。Root再start、normal acceptance4022/4042、stop/reload、全回帰/署名/配備の反復は0。BUG1332/YKT1098、真正親完了・適合する失敗回収・新source native/Browser/CHR/四100/F03/451は未完。診断のsource/runを正式受入へ合算しない。
