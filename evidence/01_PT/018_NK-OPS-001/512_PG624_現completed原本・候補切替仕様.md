# PG624 現completed原本・候補切替

SS343/SSC227、WBS-N15.04共通native接続内。管理工具PTのみでProduction PT加算0。

## 固定context・独立期待値

OLD PG600/source23b14a44b10504172e030bbd6625926bf049fb5c/BOMa6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f。NEXT PG621/source72fb7440697ee1048a5c0145055dc1cc3c577914/BOM4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e。SQL28/history29、runtime actorはOLD PG600 ABI。

真正旧run3a53b979-fa01-47dd-92a6-7b26affcfb5c/cutoff2026-10-08T15:32:46.368375Z/activation970bbce1-6bba-4db0-ace1-680ee7dfde92/DONE15:57:38.735146Z/end87761979588。PG611after SHAa7e90f2973f966def39d473f09274383bc866ad37d98b73c96658ece0a09c849/full24/492batch/十Unit18fields/config20/PID1四row。現在値として再読し、過去safeだけで代用しない。

| Test ID | 独立期待値・検査 |
|---|---|
| PG624-C001 | verify/activateのみ、null/empty/foreign/resume拒否。literal20CLI/data：run/cutoff/activation/end/outcome/missingとcurrent/source/BOMを個別比較 |
| PG624-C002 | contract4：19全field保持、各欠落/null/type/値変更拒否、epoch七field/UUIDv4/state/permit、有限deltaのみ |
| PG624-C003 | binding2：両configure直後SQL28、OLD runtimeABI、baseline/receiptsha・492・INV/end・8stop完全set、verify-after/complete再認証 |
| PG624-C004 | owner3：封印AST全global・verify/activate/foreignclass/mode/M-A FLOCK不一致拒否・tmpfsatomic heldFD保持 |
| PG624-C005 | receipt1：独立literalPID1/job/start/budget/time/cursor/全identity欠落/null/異値/重複/timeout/DONE異値拒否；unit2はcanonical十/18Unit-source/alias拒否 |
| PG624-VM001 | stage new-only tools6payload/dependencyhashpin/Root400/dirsync、business0 |
| PG624-VM002 | verify freshM/A/専用RODB71419602/十Ref/privatebus/heldFD、全19二読→candidatehostRO/typed187→全原値保持→RODBclose/逆Refclose/M-A正常→complete。全scope独立post |
| PG624-VM003 | activate別fresh全再認証＋verifyafter equality、元cohortのfreshUUIDv4INVALID/currentNEXT/approvalNEXTだけ変更、旧permit含む全原値保持・全新normal・resources0 |

## 実行

JDK25.0.4 `bash tools/quality/vm/050_s1/pg624_compile_contract_v1.sh`：actual0/Werror0、Python12test・独立Java20条件。新未実装時の不足receipt test参照は工具開始前に追加し正常、VM/PT加算0。

`python3 -B tools/quality/vm/050_s1/pg624_completed_native.py stage|verify|activate` はclean/operatorcommit固定で各new-only一回。現時点未実行。再実行しない。UNKNOWNは保持、旧closed操作/旧completed再開なし。

証跡はPG379/pg624-{mode}-v1.safe.json/exit、Root-private19before/after/complete、公開sanitizedmanifest/hash。rawDB/credential/native/session/key/permitはGit0。source/run/終了code/全field/資源後条件を独立確認後だけ当範囲限定受入。新candidate通常親/native/global100/formalは別未受入。
