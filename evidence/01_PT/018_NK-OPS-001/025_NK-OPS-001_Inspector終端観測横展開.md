# NK-OPS-001 Inspector終端観測 横展開・検証記録

2026-09-13 正式認定: source af2526dda0e64ca3d0a427a66fd9335afff836ae / dev-foundation / PT-WEB-20260913-11、08:08:31～08:24:20 JST、exit0。全1375 PT成功、6 Java全4coverage100%、Production5静的解析未解決0、15collector/38scope・36負canary合格。新16 PTと5class/28method/165line/92branchは全missed0、Batch全体86class/440method/2661line/1411branch missed0。BUG187～190/YKT147～150を全関連case・compiler・静的解析・全回帰で再試験完了。SSC060はこのread-only部品範囲を完了し、起動配送/実終端quarantine/OS寿命/親/IT/STは未完了のまま維持する。独立input/outputとsource/tool/command/hashはevidence/manifest.json、018025を参照。以下は実装前・探索時点の履歴。

PT-OPS-UNIT-001～016は全PASS（skip/flaky/未実行を含まない）。独立373byte fixture SHA256=2170fc2e71a4ba50519bc2f123d0bf75fcc46adab033645b7b68b5c513c345f6。3actual traceはinputと独立literalへ照合済み。実環境/全実行command/target commit/coverage/static/関連BUG/SSC/各file hashは同Programのevidence/manifest.jsonへ一意に収集する。

## 対象と限界

PG-D-167、SSC060先行81e0e64b、SS/PT先行56ba7ae8。OPS009/UI251/SS311・341 §7.4・343。
InspectorUnitSnapshot、InspectorUnitProbeおよびNativeReader/SafeStream/QueryProcessの5 concrete class・28 method・165 line・92 branchを除外なしで対象にする。Reader/Startは実行文のないSPIでありcoverage除外設定なし。TWRのjavac生成suppressed経路はJaCoCo既定filterに数値を委ねずUNIT015の所有順・close回数・primary同一性・suppressed型/個数で実行確認する。

本部品はread-only観測。親のstart配送確定、同run環境とOS lockの連続寿命、全子の実終端、DB排他再取得、永続END、実backup生成、実配備Linux受入/IT/STは別gateで未完了。snapshot/probeを親全体の完了証明として使わない。

## 独立oracleと全観点

手書373byte ASCII fixtureのSHA256は2170fc2e71a4ba50519bc2f123d0bf75fcc46adab033645b7b68b5c513c345f6。実装前にPython hashlibで算出。実InvocationIDやprocess名は保存せず合成IDだけ。3actual traceは実返却値/実呼出数から生成し、022の独立literal/019の別記期待へ照合する。

- UNIT001～008: 全18property欠落/重複/未知、逆順同値、最終LF後非空19行目、373位置×NUL/CR/high-bit=1119負例、PID/job uint32・monotonic uint64 ±1/形式、code7×status256=1792、state6×substate6=36、freshID/時刻/0・10、NULL/byte所有/64並行。
- UNIT009～016: state→process→stateの3query、12可変field変化と6固定field違反、process厳密9byte以外拒否、各reader3位置IO/null/runtime/interrupt、2048/2049と9/10、5秒境界、実unprovisioned hostの拒否だけ。unit起動/停止なし。
- Native operation順の独立11件: start/get.stdout/get.stdin/get.stderr/stdin.close/stderr.close/wait/exit/stdout.read/stdout.close/alive。全位置Runtimeとinterrupt、getter null、wait InterruptedException、timeout TERM時割込、IO read/close、3cleanup×3primary複合を検証。SIGKILL/無期限waitは禁止fixtureで即失敗。
- NULLはconstructor/public boundaryの契約違反でありcatch-NPEによる正常化なし。未知Runtime/Errorのprimary identityを保持、既知IO/timeout/interruptは固定diagnosticかつraw cause/suppressedなし。取得済みresourceのみclose1回、取得前失敗は後続getterなし。source/opaque出力byteは成功返却時の所有移譲以外finally消去。
- command固定、envはPATH/LANG/LC_ALL/SYSTEMD_COLORS/TERMの5変数だけ。既存API/Web stop専用parser/queryは適用先が違い変更しない。

## 障害と横展開

| BUG / YKT | 修正前根拠・原因 | 修正/確認対象と非該当根拠 | 再発防止 |
|---|---|---|---|
| BUG187/YKT147 | explore1 07:51:02 exit1、-Xlint:tryがTWR内explicit close2箇所を拒否。先行7ecefa16 | 新NativeReaderのstdin/stderrはEOF/discardをwait前に必要。SafeStream.finishで同once状態を共有。任意flush/availableや警告抑制なし。既存3query ownerは全reactor compilerが非該当確認 | UNIT009の11操作順、UNIT015の一回close、全testCompile/static |
| BUG188/YKT148 | explore3 07:57:27 exit1、再代入child capture2箇所。先行8aa8be28 | UNIT013/014をfinal別名束縛。全同class lambdaはloop内かeffective-final。Production/独立入力期待は変更なし | 全16 test compile・各timeout/interrupt非成功 |
| BUG189/YKT149 | SS3417.4/PT023のenv6転記誤記。実Mapと列挙は5。先行8aa8be28/SSC060 | 新2文書のみ修正。全SS/PGPT/OPSで環境6/固定6を検索、他の6root/64byteは件数対象が異なり非該当。Production allowlist不変更 | UNIT009/016と既存STOP015の固定Map独立assert |
| BUG190/YKT150 | explore4 PASSでもstderr未取得get.stderr primaryがcleanup注入を遮断、空suppressed loopは証明なし。先行c1203bf4 | UNIT015: stdout.closeはstdout.read、stdin.closeはget.stderr、stderr.closeは所有後stdin.closeでprimary。全3×3で注入回数1/suppressed1/各所有close1をassert | 全test getSuppressed検索。他のforeachはBackupArtifactVerifierTestのみで既にlength>=1、その場の所有後read/next/open faultとcloseDirectoryを確認。ArtemisReplyConsumerのstreamはanyMatchをassertTrueするため空集合は不合格。EnvironmentFiles/RunFiles他固定0/明示arrayは診断除去/固定期待で非該当。UNIT015を全reactor再試験 |

## 実行履歴

2026-09-13 Ubuntu26.04.1/Linux7.0.0-31/JDK25.0.4/Maven3.9.12/systemd259.5、dev-foundation。

- explore1: compile失敗2warning、PT未実行。explore2: snapshot8＋依存storage8成功。explore3: testCompile失敗2件、PT未実行。
- explore4: 新16＋依存storage8成功。ただしBUG190検出のためその条件の成功証明としない。
- explore5: 08:04:45 JST/9.172秒/exit0、新16＋依存storage8成功、全5class/28method/165line/92branch missed0。/tmp/pgpt-unit-explore5.log。探索は正式件数へ未加算。
- static1: 08:03:32 JST/14.603秒/exit0、Batch-am compile/SpotBugs0。/tmp/pgpt-unit-static1.log。
- 019証跡負canary35＋017の1=36成功。unit入力373全位置flip・3trace欠落/改竄/余分・全suite欠落/重複/未知/失敗/skipped/flakyを拒否。36件をJava PT数へ混ぜない。
- 正式全reactor PT-WEB-20260913-11は未実行。正式結果/commit/環境/command/全counter/hashは022/024およびevidence/manifest.jsonへ記録してから認定する。

実行commandは421と共通。探索はBatch-am -Dtest=InspectorUnitSnapshotTest,InspectorUnitProbeTest,LinuxFileLockTest test jacoco:report、正式はwork/pgpt_foundation_verify.shの全clean verify。探索logはGitへ生出力を入れず、正式sanitized結果・独立input/output・監査文書hashを022収集する。
