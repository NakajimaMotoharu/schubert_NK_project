# 605 SSC239 fixed fresh system-manager reader：PT仕様と限定結果

Program NK-OPS-001、RD OPS009/SYS002004、UI212251、SS342343354/SSC239、QA047、BUG949/952～957、YKT718/721～726。対象=RootStartupContext.NativeIo、LinuxSystemdQuery/Owner/Property/Budget、LinuxSystemdSession/Native/Factory。Productionはsrc/batch、試験は同module/src/test。Current baseline/oracle/業務仕様は変更しない。

## 独立oracle・Test ID

| Test ID | class/method・目的/入力・操作 | 期待値の独立根拠 |
|---|---|---|
| MANAGER817001/002 | QueryTest.exactFreshFullAndDeadlineGoldenBytes：全7field/期限4field、別Session・前後owner | 手書きASCII literal、全キー/順序/改行/値とfresh生成回数。一方の結果からexpectedを生成しない |
| MANAGER817003 | QueryTest owner不正・変更：PID!=1/EUID!=0/unique不正/前後変更 | PID1+bus EUID0+同uniqueだけ許可、IO拒否・当scope閉鎖 |
| MANAGER817004 | QueryTest property境界：4096超/空・ASCII以外/control/欠落、null/未知projection/異thread | 出力4096以内・printable ASCII・fixed whitelist、constructor invariant。nullは境界契約違反でNPEを正常処理しない |
| MANAGER817005 | QueryTest everyBoundaryIoRuntimeFatalAndUnknownCloseRemainFailure | 全start/owner/field/close故障の元例外同一性・不明closeでは次factory発行0、primary/secondary契約ResourceScopeと独立照合 |
| MANAGER817006 | QueryTest originalFiveSecondsWholeQueryNotPerRpcAndSubMicrosecondBoundary | 元時計±1ns/5秒/LongMAX/途中interrupt、残1µs未満拒否、次RPC0。各RPCごとの期限renew0 |
| MANAGER817007 | SessionTest.nulDecoderReadsOnlyActualAllocationAndBoundaries | 0/1/short/4096/NUL無し・null。独立byte列の実index読取数はNULまでlength+1、末尾後のbulk読取0 |
| MANAGER817008 | SessionTest.literalAbiAllKindsAndUniqueDestinationClose | D-Bus固定GetNameOwner→uniqueのUnixProcessID/UnixUser(EUID)。独立request ABI/argument/schema、PID1/EUID0/unique literal、auto-start0 |
| MANAGER817009 | 同test/SessionTest null/wrong status/array | Unit=Id/Load/Active/Sub/Invocation、Service=ControlGroup/PID/START。unsigned32=4294967295/64=18446744073709551615、ay=001122…eeff/長0、他長/NULL拒否。systemd公開vtable/ABIを根拠に手書きfixture |
| MANAGER817010 | SessionTest everyNativeCallExceptionIsNotNormalClose | native全呼出のIO、constructor/null/status/owned pointer/unref failure/異thread/duplicate/未開始。unknownではclose成功扱い0、次操作拒否 |
| MANAGER817011/013 | SessionTest.authenticationAndSuccessiveRpcUseOneOriginalBudget | 手書き5,000,000µs時計。接続wait2秒×反復は元5秒で拒否、接続1秒後RPC予算4秒→2秒で拒否、後続0、timeout正常終了はowned close別確認 |
| MANAGER817012/STATIC825001 | actualImmutableBinding、platform/ancestor trust、native invocation追加試験 | Linux/LP64/固定三arch、null/missing/未知型/nonroot/0022拒否、missing symbol、void/checked/runtime/fatalの独立MethodHandle port。固定security pathのみEXACT局所分類、global suppress/coverage除外0 |
| MANAGER824001 | 同source jarを配備せずhost/VM fresh read比較 | systemctl before→native→systemctl afterが全Map等価。5Unit×2projection×4反復、元5秒・FD/子process後条件、全十Unit停止原値不変。DB/permit/原本/配備/start/stop変更0 |

正常/境界/異常/例外/null/所有thread/再照会/期限/closeを上表で網羅する。JMS再送はこの純読取component対象外、業務再送のoracleへ流用しない。全traceはこのTest ID・actualsource/run・code comment・ledgerで対応する。

## 実行・環境・証跡

Java25.0.4/Maven3.9.12、Ubuntu Linux x86_64、host/VM systemd/libsystemd0=259.5-0ubuntu3.4。C ABIは公開v257ヘッダーとcontrol/dbus実装を独立照合し実259.5で確認。FFM固定`/usr/lib/x86_64-linux-gnu/libsystemd.so.0`のrealpath全祖先root/nongroup-other-write、環境bus/lib override0。Ubuntu既OSpackage由来、新version導入0。参照：<https://github.com/systemd/systemd/blob/v257/src/systemd/sd-bus.h>、<https://github.com/systemd/systemd/blob/v257/src/libsystemd/sd-bus/bus-control.c>、<https://github.com/systemd/systemd/blob/v257/src/libsystemd/sd-bus/sd-bus.c>、<https://github.com/systemd/systemd/blob/v257/src/core/dbus.c>。

私有root=`/home/mini/codex/project1/work/pgpt-runs/PG379`、guest=`/var/lib/pgpt-s1-preservation`、raw credentials/DB/session/原本はGitへ格納0。run.safe.jsonに日時/command/source/終了code/sourcehash/XML/exec/static/JAR hash、native result.safe.jsonに同candidate/helperhash・FD・比較/経過・候補未配備・正式未認定がある。公開結果は非秘密集約のみ。

- 818：format1/compile-PT未実行。
- 819：NullAwaycompile1、OS/arch/metadata欠落拒否へ是正、解析抑制0/PT未実行。
- 820：nested Nullable構文compile1、821：初回testcompile1、822：初回61PT中fixture arena二重close E1、823：61PT/FES0だが固定path static1。いずれ失敗保全・再試行成功へ上書き0。
- 825 source`726d3ab973e21273ae3232d05c87a57669f37f3c`：選択7suite/61PT/FES0/静的0/Spotless0/build0、branch全閉鎖ではない。Query line/method/class全到達、branch1未到達。Session/Nativeはbranch計20未到達・Native line3未到達を明記、global100/正式加点0。
- 824 same825source/同jar`20e66d5f0aec58741865420734411451e4ed74e6045d000ed3ec60082865bee5`：host+VM各40比較/41nativequery/81reference実0。host FD50→50・median4,039,338ns/max8,764,337ns、VM FD48→48・median2,845,748ns/max6,385,169ns、referenceVM median6,240,077ns。helperSHAf6f39deb010b8c89769dd33be4dc745068abcf7021cddfc8d3cb14f7b8b3ed8b、guest private logSHAf36207f850806fe92d5a41e9f4c58a91bdb8270aed59c54432f11078f74031c3。

再現command：`python3 -B tools/quality/vm/050_s1/pg823_manager_selected.py --run <別new番号>`、成功後`python3 -B tools/quality/vm/050_s1/pg824_manager_native.py --selected <同selected番号> --run <別new番号>`。既run番号はnew-only拒否、再発行0。実受入対象sourceでこれらを再検証し、別source結果を流用しない。現在追加boundary/例外試験とpolicy分解がdirty、source固定後826選択→827native、必要全6/署名newsource→別freshresume/真正親DONE/ownedstop/nativeは未実行。

## 未受入・後続

23:02同source確定結果：candidate`2a0d5aa392c85a1dc12a1cdb423978e8500895b8`/PG828選択66PT・7suite/FES0/static0、Query/Session及び全実装nestedのline/method/class/適用branch各100（branch無しliteral/recordは自動疎counter、除外設定0）。PG827は同jarSHA d3f0f85ba839b37a931a945531d648f1c3f55325a4caf5af972f12cf937148af、host/VM各40独立比較実0・FD50→50/48→48・全十停止不変、nativeVM median2,714,505ns/max8,366,135ns、旧726成功流用0。selectedmanifestSHA c52e72241b7fb1bd10b7e799963b1846465fdae72dd2371eed5586a7576bc0a4、native結果SHA2290ac93fc42ca452a5c247877cd8b7891afcbd0c0a52c67a623396ddb479bb2/guest log61587c478bb56c85278d47c93172984470b04fc7f4e2103f846d01157f18f2a7。

451 trigger=RootStartupContext実運用IOの横断変更。PG830 same2a fresh全6 clean build/test/SpotBugs/jacoco実0（終了23:01:04JST）、PG831独立collectorはfrozen全source Gitblob/前後clean・全XML独立case/FESFlakyNotRun0・coverage同session/同JARbyte・六static0・当828batchclass/未変更五moduleのoldcurrent class全部一致を照合し実0。3534PT/522suite/1632main、前102から+17PT/+2suite/+12class、changedはRootStartupContext.class/NativeIo.class二つのみ・新class12・削除0。全体missedはLINE3808/METHOD629/CLASS40/BRANCH1137でglobal100=false、親/native受入/正式は未完。manifestSHA85c90fd6c60c88040127538ced822dce3e8260f290809635916d36871e685ede、private830/source/started/completed/build.private.log/exit/source-files.sha256・六module XML/exec/static/JARを保存。実elapsedはmanifestから記録、17:27はMaven表示（曖昧な推定秒数へ置換しない）。実行command=`python3 -B tools/quality/vm/050_s1/pg830_manager_full.py`、資格`python3 -B tools/quality/vm/050_s1/pg831_manager_collect.py`（既manifestはnew-onlyで再発行0）。

この同source二readerの単体四100/実停止比較/全6成功は952～958の直接是正を実証するが、広いP018所有scope全受入/BUG949真正親因果/global四100/CHR/正式/IT-ST完了を意味しない。次はsigned candidate832のliteral2changed/12addedを独立fixtureで資格→現在816/827停止基点の新全原値/DB/Refへ再認証→正規code-only→別fresh一回resume/元30分真正DONE→owned停止/当source native/後続。現current796/source102/原本active/Backup/runtime空を保全し、旧808再start0。

826 source70e41eee1f0d7185c95e1fc91e87b0dbd9c78905は65PT/FES0/静的0。元query/property直前Budget・policy/ABI例外試験を追加し、Queryの四counter100、Sessionのline/method/class100・branch残2を実計測。Native/Factory/Owner/Propertyは四100、空interfaceはcounterなしで除外設定ではない。残2は取得失敗後の未開始busとunref異型の独立negativeへ追加して次828を別newrunにする。旧825/824を当新sourceの完了結果へ流用0。SS239設計3文書のみPR77/main a5cd475de86ad38ced9ec88674ddfd7098660367に公開済、実装/PT/親/正式完了とは別。

952～957は直接是正・825/824限定実証ありだがYKT全対象/新source分岐/全回帰閉鎖までは未完。949親timeout原因・新真正DONEは未解決、停止中比較速度から原因や負荷中性能を推定しない。正式PT-WEB-20260925-24/1964/53、global四100、CHR・IT/ST受入を本結果で更新しない。SSC239は記述確定と設計onlymainを別管理する。
