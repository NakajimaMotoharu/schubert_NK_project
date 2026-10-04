# NK-OPS-001：当該timeout世代の限定復旧・Caddy是正 PT仕様

関連：RD OPS-009/TST、UI251、SS341/342/343（SSC179・承認QA047内、SSC178）、BUG671～677/YKT476～482。Productionと私有operatorを区別し、工程認定/IT/ST合格ではない。正式run24/1964PT/53scopeをこの限定試験で更新しない。

## 1. 対象と独立期待値

| ID | class/method・対象 | fixture・入力/操作 | 独立期待値・観点 |
|---|---|---|---|
| CADDY457001 | BackupUnitStartClient.caddyFence、Attempt.preserveObservation | Caddy非所有fence、正規保有確認・close-only、null/例外 | retire/requireRetained/closeObservationは元fence確認だけ。API/Web intentのunlink・owner close・新retirement権限0。発生例外の同一性、固定順序をliteralリストで確認 |
| CADDY457002 | Attempt.preserveObservation | API/WEB/CADDY、全worker target | API/WEB/CADDYだけservice close契約、worker拒否。既存worker receipt/全kernel/retireAfterを緩めない |
| CADDY457003 | MorningCaddyReadiness.profile | 実systemd normal0と既存0/0、00/1/30/0/1/1/0/0/00/0/0/0/0x0/空/未知/非exited | SS342真正validate正常0の意味を保つ。表示文字列は実観測normal0と独立literalだけを正、他status/unknownは拒否。正常0をProduction正規化methodでexpected生成しない |
| ROOTPAIR179-001 | StartupPermitFiles.revoke→RootFailedStartRecovery.quarantinePair/retirePair | 実FD・明示synthetic Root/tmpfs fixture。独立ASCII ISSUED/current＋元permit/owner/launch2＋空API/WEB intent、publication欠落exact7 | ISSUEDではfailedPair拒否、同epoch正規revoke後もpub欠落Pair拒否、publication-first隔離後だけ正規Pair可。WEB→API→publication固定順、INVALID literalと残4byte不変、最終exact5、readIssued拒否。parent/worker成功やnative資格は生成しない |
| ROOTPAIR179-002 | StartupPermitFiles.revoke | 元permitと異なる固定digestのISSUED/current＋pub欠落2intent | foreign currentを修復・失効せず全byte/2intent不変、publication追加0 |
| ROOTPAIR001～008/PERMITFILES既存 | RootFailedStartPairRecoveryTest、StartupPermitFilesTest | 各unlink/sync/proof/IO/Runtime/Error、欠落/未知/衝突、同epoch/foreign、不正/空/null | typed退役の各失敗境界でpublication-first再隔離、両子を個別試行し成功偽装0。既存normal30/Web50仕様・旧結果を変更しない |
| TIMEOUT457-ENV | Pg457TimeoutPairRecovery.terminal/launch | 18field固定literal3role、全field欠落/null、status30/0/不正/異世代/PID、固定launch10line/8key・boundary/未知 | 親timeout143とAPI/Web owned stop143を限定受理、古い正常30/0/10拒否。parse成功は権限でない。hashは固定独立64hex vector、canonical順/ASCII/LF/UUID/整数境界を直接検査 |
| TIMEOUT457-PHASE | retirementStage/quarantineAfterUnknown | 独立exact8→7→6→5集合、backward/jump/foreign permit/owner/part/thirdintent、IO/Runtime/Error/同じprimary | WEB→API→publication以外の退役・追加/後退を拒否。再隔離一回、元primary保持・secondary同一性、self suppression0、失敗を成功へ変換せずcallerがM/A retain |
| TIMEOUT457-NATIVE | Pg457OwnedIsolation、Pg457TimeoutPairRecovery | 隔離VM既存boot/固定実世代。root0700/21file集合pin、署名PG456/source559、原本pending/261全14列/23business/Backup20/非空Transfer | 真正M→A→batch DB/advisory＋readonly schemaを継続所有。全9kernel/旧PID不存在、元失敗full18、捕捉普通identity/argv/ticks/launch/owner、全BOM/current/approvalを照合。verifyは変異0。変異直前・SAVE後に全保存再一致、正規同epoch revoke→publication-first quarantine→typed順序→INVALID/exact5/全保存不変・全owned正常close後だけ限定成功。中途・close不明は再隔離/M-A保持、new permit/epoch/start/deploy/DDL/DONE0 |

## 2. Sourceと環境の分離

nativeは署名Production source `559bf7eacb401d6d07037dbdd295b32f174976a0`、release PG456/manifest `21affa1850d60f3a7d54f5dbcc37e12c6460563865771fa49a52a433fe91b424`。hostのBUG672673修正と新連結試験はHEAD9d1f29f5e＋当変更群の別source、限定XML/実targetを別保存。別sourceの新Caddy成功を旧guestへ流用0。元PG456 fresh3249の480XML、PG457選択60/新86と中断PG442を加算しない。

host JDK25.0.4/Maven3.9.12/SpotBugs4.10.4/JaCoCo0.8.15/NullAway0.14.1、guest Ubuntu26.04/kernel7.0.0-34/PostgreSQL18.6/JDK25.0.4。JDKインストール先/実hashはtoolchain正本421と各manifestへ。guest工具は旧16class閉集合＋新timeout/isolation2classをRoot0500/0400でnew-only stage、host compileも同16閉集合に限定する。秘密はGit外WorkPG379・guest保存namespaceだけ。

## 3. Commandと評価

Production選択は全6reactorに正規canary5classとCaddy3class＋RootPair/PermitFilesを指定し、spotless:check/test-compile/jar:test-jar/test/spotbugs:check/jacoco:reportを実行。failIfNoTests/NullAway/独立oracleを弱めない。選択v3の8class60、連結追加の10class86を区別しXML実数/実終了を確認する。新連結初回compile失敗はPT未実行のまま保持する。

工具：固定署名JAR/runtime libs＋guestと同16classに対して`javac -Xlint:all -Werror`、`Pg457TimeoutPairRecoveryTest`。197独立assertはProduction PT件数0。既存12isolation assertも同様。新only stage→実VM `Pg457TimeoutPairRecovery verify`→照合後だけ引数無し限定復旧。既存隔離操作/失敗工具/署名配備/DDLを二重実行しない。

coverage：開発選択はcleanなし/既存exec appendのため4指標を認定しない。sourceを固定したfresh clean全6と同byte native採取・451全scope/CHR/secret/traceが必要。旧coverage/XMLを補完しない。正式閉鎖は未達のまま。

## 4. 証跡と停止/再開

325実行結果、安全provisional manifestへTest ID/XML/hash/command/終了/実source/対象byte・検証時刻を対応させる。失敗と成功/未実行を分離する。private captureは集合SHAと非秘密flagだけを公表し、raw owner/permit/launch/session/credential/DB dump/原本データを公表しない。次callbackや同じstartを重ねず456先頭の現source/process/SAVEを再照合する。限界/不明は不明とし、限定復旧が成功しても通常自走を停止しない。
