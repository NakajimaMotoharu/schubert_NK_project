# NK-OPS-001 固定native採取profile・同source集計仕様

PG470／SSC193、RD SYS002004/OPS009/TST004、UI212251、SS333342343451。独立期待値をproductionで生成しない。実親受入と正式coverage認定を分離する。

| Test ID | program/class/method・入力/操作 | 独立期待値・根拠 |
|---|---|---|
| PT-OPS-NC193001..005 | FixedNativeCoverageProfile.parse/argument/forOrdinary、API/WEB×ROOT/ORDINARY、32hex Invocation、null/欠落/未知/重複/拡張option | literal pin/path/output=none,append=false,dumponexit=false/sessionid=ROLE-INV-phase。default/unrelatedhost agentはempty・Invocation読取なし、予約prefix不正はIllegalArgument・NPE catch正常化なし。固定vectorと独立文字列比較 |
| PT-OPS-REXEC193 | FixedServiceExecArguments.arguments(profile) | 同role ordinaryだけindex9にliteral agent1項、除いた全旧引数は既literal API/Web goldenと一致。Root/別role/null拒否、immutable、5env/2FDの変更0 |
| PT-OPS-NFILE193001..004 | OwnedTransferDirectory.createPrivateEntry、PrivateDirectoryEntryTest、host実Linux calls／TempDir | 新規0600/nlink1のheld `/proc/self/fd/N`、rename後の置換pathへ書込0、既存/symlink/partial再利用拒否。null/不正名/closedでmutation0、create/write/close/compound故障でFD1回消費・partial保全。16並行1writer。独立unix metadata/byte/FD帳尻 |
| PT-OPS-NATIVE469COUNTER | pg469_child_native_counter_v1、既NativeCoverage、D3 frozen6＋今回親/Backup/Cleanup/Expiry exec4本 | 同source/class byte NoMatch0、各1session/親元budget内。全B/L/M/C未網羅はhost以下、parent及び子4本以外のoldexec混入0。rootAPI0byte未算入/ordinaryWeb agentなしを明示、100%/正式加点0 |

入力fixtureに秘密/DBdump/原本実体をGit保存しない。private実exec・tool/logを600で保全し、safe manifestへhash/counterだけ保存。D3親Unitは実効`--resume`のPT profile：361行のsame run/10step SKIPPEDは既承認resumeであり、SS190日次new-runへ転用しない。parentの正常判定は同PID1/boot/INV/job done＋owned後条件、dump存在だけで正常としない。

環境host Ubuntu26.04/JDK25.0.4/Maven3.9.12、guest同boot e07aa706…/JDK25.0.4、branch dev-foundation。選択command `bash tools/quality/vm/050_s1/pg470_profile_selected_v4.sh`、log私有077/試験子0027、終了marker・対象source各hashをmanifestへ格納。既存control MessageCodec/ResourceScope/FixedServiceIdentityも実行する。XML対象6suiteのみ数え、残存XML/失敗/skip/not-runを混ぜない。

Coverageは開発累積execの参考値のみ。profile/argv/entryの限定成功を公開API export・Root checkpoint・ordinary終端本体接続・fresh全6/native100/正式へ代用しない。次=同SSC193接続群の独立oracle→source固定・451所定fresh全6→正規署名/所有配備/同source native採取。関連BUG751/YKT531、正式run24を維持。
