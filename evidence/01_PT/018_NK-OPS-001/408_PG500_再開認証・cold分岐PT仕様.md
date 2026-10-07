# PG500 再開認証・cold-boot分岐の独立PT仕様

Program NK-OPS-001。WBS-G13.07初期join→WBS-N11→WBS-N14。
Production source a2e98ce9e96c42425921e3686e8ae7a94bff9e6c / PG495 /
schema028。工具/管理限定試験をProduction PT数・正式認定へ加算しない。
RD SYS-011/OPS-009～017、UI211/212/243/251～253、SS343 SSC165/174/198/202、
SS353 QA047復旧。RD要件の主担当は485を維持し、本接続の横断参照として扱う。

## 初期traceと予算

485は935物理artifact/281RDの担当割当であり、意味的充足は未認定。
今回の固有Test IDと独立oracleを以下で束縛する。G13.07全体/最終release差分は未完。
着手群の残枠は低1.72/標準5.50/高13.50pp（G13.07/N11/N14のみ、親子重複0）。
487のevents.jsonlへ実消費・期間・欠測・残予算を別保存する。

以下の表は着手前の入力/期待値と初期状態を保全する。現在の実行結果は末尾とmanifestを正とする。

| Test ID | 対象/入力・操作 | 独立期待値・根拠 | 状態/証跡 |
|---|---|---|---|
| PT-OPS-PG500-001 | 478 A/477/487・481/484～486・Git HEAD/dirty/stash・fresh枠・現在VM process確認 | 旧HEAD復元0、stash7保持、個別費null、旧482不変更。実枠>10%でのみ新規着手。指示値とapp実値を区別 | 開始2a6dfe017 clean/fetch差0/0、週次used1/残99、cursor初回末尾、WBS監査正常。VM process不在 |
| PT-OPS-PG500-002 | pg499_runtime_retirement_test.pyを現保存sourceで独立実行 | 407のliteral full18/全列/tree/config・正常/foreign/欠落/argv/例外、28検査。Production methodで期待値を生成しない | host28正常、native pin再試験は未実行 |
| PT-OPS-PG500-003 | VM不在/ディスク非使用を確認しoffline private copy→hash比較→root partition read-only調査 | 原qcow2 inode/size/mtime/ctime・全hash不変、copy hash一致。GPT固定root start2324480,size81561567/512byte。秘密原本はprivateのみ。業務start/DB変更0 | 実行中。元disk/古い保全物を上書きしない |
| PT-OPS-PG500-004 | 保存kernel/initrd・元boot-v2と同じ管理専用basic.target/wants・timer/path等maskでnew-only boot | QEMU/22222/diskの既使用時は起動前拒否。SSH/DB管理だけ、旧PID/bootを流用せず全10固定Unit/18property/kernel/Job/PIDを現bootで二読。旧/tmpfsを復元しない | 未実行。新console/PID/QMPだけ、旧ファイル不変更 |
| PT-OPS-PG500-005 | 現署名BOM/approval/current/source・全24table/442batch・原本Backup/Transfer/etc・PG498afterの再認証 | DBはPG498afterの独立SQL全列/全行literal原値と一致。永続treeは型/owner/mode/link/inode/mtime/ctime/hash一致、atimeは整合指標にしない。旧/run消失は別記し成功退役/正常closeとしない | 未実行、異常/不一致なら隔離を維持 |
| PT-OPS-PG500-006 | 旧pg492-once-resume runtimeの現物有無と現boot判定 | 同boot現物ならSS198の正規退役へ。別boot消失なら旧PG499 native未実証のままcold契約へ分岐、消失fileや旧epoch/permit/intentを復元しない。後続は新所有/署名/完全原本/全Unitとcold準備の実後条件が前提 | 未実行、OS停止はBUG808の再試験成功ではない |

## 例外・並行・保全

二重QEMU、使用中disk、22222占有、既存出力はnew-only guardで拒否する。
業務Unit生存、未知owner、全原値不一致、未認証署名、runtime混在・新boot不明では
後続start/配備/退役を発行しない。raw DB/session/token/credential/nativeをGitへ保存しない。
既存旧143/UNKNOWN/PG442中断・Current baseline・Scenario3・stash/Backupを保持する。

## 実行・終了・後続

管理検査: python3 -B tools/quality/wbs_progress_audit.py。
独立host検査: python3 -B tools/quality/vm/050_s1/pg499_runtime_retirement_test.py。
offline: bash tools/quality/vm/050_s1/pg500_offline_capture_v1.sh。
boot: bash tools/quality/vm/050_s1/pg500_boot_isolated_v1.sh（未発行、前提確認後一回）。
環境/日時/HEAD/command/exit/input/期待/実際・SHAは実結果manifestで採取する。
Coverageは管理工具のみ非適用。Production/native100%の受入はN15/G01に残す。
関連BUG808/YKT577・旧BUG544/YKT388は未解決。初回未実装試験は障害数へ加算しない。

## 現実行結果（2026-10-08）

002 host28/003 private disk原物不変更保全/004一回管理boot・全10cold/full18/kernel0は限定正常。
005 v1 actual1 BUG809（全DB21,337,529byteを一般8MiB枠で拒否、SAVE/start/DB変更0）。
修正前915/YKT578→SQLだけ既存32MiB→独立9境界/negative→v2 actual0で全24/442二読一致。
永続5root/102要素・metadata/hash二読一致。006 old runtime/startup/4volatile消失、old retirementProven=false。
新boot cc9ed874-7f4f-450e-a188-8de1e42c8441/QEMU26737、host RO bind消失。
G13初期joinの当範囲とCold物理前提のみで、全WBS/新INVALID/typedBOM所有帰還は未受入。
SSC206先行登録/設計onlymain反映後、別fresh冷準備→runtime→通常親/nativeへ継続する。
結果/command/exit/hashはevidence/provisional/PG500-cold-readonly-v1/manifest.json。
v1と初回fixtureDEVNULL欠落は非合格で保持。PG4953411/正式1964/53scope不変更。
