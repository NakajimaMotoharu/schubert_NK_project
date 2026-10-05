# NK-OPS-001 停止後code-only移行・原本保全PT仕様

関連RD SYS002004/FIL/MON、UI212243253、SS342343/SSC190191193194195/451/PG-D377。Pg472StoppedDeployment/helper、frozen c8ad413437be409f70ec37bdba33c5e3cd21790b、署名8e6bc3c26c1d707b5873dd14c229d41fa129bf7e5547dacc2bbc3780a90df3f1。実app仕様・原本run/cutoff・元Unit期限・DB/backup/Current baseline不変更。

| Test ID | 入力・操作・独立期待値 |
| --- | --- |
| PT-OPS-SDEPLOY001 | mode verify/activate/null/未知/extra。二modeだけ受理、Source40桁/署名64桁をliteral照合、start/restore/migrateの権限なし |
| PT-OPS-SDEPLOY002 | 既run UUID/PG471同親の20:24:33～20:54:34Z正常DONE、境界±1μs、pending/旧D3activation/異run/outcome。成功・正規windowだけ受理、原本を戻さず、Unit GCはRoot同journal/原本と停止receiptで別認証 |
| PT-OPS-SDEPLOY003 | metadata key・leaf順を変えた同値、ino/mode/名前/欠落/null。同値は全field一致、変更は拒否。Map.toStringのVM salt/orderに依存0、DB/原本/Backupは既独立snapshot/typed digestで全値比較 |
| PT-OPS-SDEPLOY004 | current parser固定19field/null相当欠落/duplicate/foreign/loadstate/非ASCII、Root600/owner0/link1の素材、helper global binding、実親argv/FD/FLOCK/inode/owner/mode/link/欠lock・重複。正規だけ認証、外国failedを正常化0、ordinary143は同boot/INV/UID/全journal/cleanup→stopped→captureと全kernelで停止データだけとして認証 |
| PT-OPS-SDEPLOY005 | M/A/readonly実DB advisory/schema内、oldSigned717/全9停止/旧Scope正常receipt、371全14列/23business/原本DONE/Backup20/49startup/旧native9(8nonempty＋旧empty1)保全。候補186/SQL27/全BOM/signature/immutableROだけ新8e、verifyではcurrent・epoch・DB不変更。activateは9native actualbyte/private600と元identityを保存、現issuedを新INVALIDへ退役し原activation維持、署名approval/currentだけatomic切替。全49canonical byte/metadata（currentだけ正規変更）・全原本/Backup/DB/history/fixture不変更、全newScope通常return後にだけcomplete。start/stop/reset-failed/新permit/DDL0 |
| PT-OPS-SDEPLOY006 | BODY/DB/A/M scope close/通常・suppressed・Error/touched matrix。変更後/close未知/fatalはframe保持、旧Unknown正常化/元143を0へ変換0。子helper timeoutは新操作を隔離し再発行しない |

実行環境：host/guest Java25.0.4、JDK javac -Xlint:all -Werror、Python host/Ubuntu26.04 VM、branch dev-foundation。tool assertionsはProduction PT数・coverage分子へ加算しない。71Java＋153Python＋既TERM28/control265を独立実行し、新Root400/700 exact hashesへ固定。compile-v1 missingimport/not-run、verify-v1 helper NameError/actual1（BUG761/YKT541）・旧preflight v1～3 failure（BUG760/YKT540）は保持。

command：pg472_stopped_compile_v3.sh、pg472_stopped_native_test.py、pg472_stopped_stage_v2.sh、pg472_stopped_verify_v2.sh→actual0必須→pg472_stopped_activate_v1.sh。一回guard/CREATE_NEW、実行中はclass/helper不変更。private raw DB/permit/session/native/masterはRootSAVE/Work700のみ、Gitはcount/hash/resultだけ。新M/A/DB通常帰還・旧current/newcandidate・全原値を実接続で確認するまで未受入、IT/ST宣言なし。結果358/manifestにsource・toolhash・時刻・actual・BUG/YKTと次commandを保存する。
