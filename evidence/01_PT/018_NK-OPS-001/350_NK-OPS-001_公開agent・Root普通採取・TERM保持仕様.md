# NK-OPS-001 公開agent・Root普通採取・TERM保持仕様

PG470/SSC193194/BUG752753/YKT532533、RD SYS002004/OPS009/TST004、UI212251、SS342343/451。対象Source及び終了条件はsafe manifestの当実byteで束縛する。既定起動及びbusiness仕様/DIF不変更。

| Test ID | 対象/fixture・操作 | 独立期待値 |
|---|---|---|
| NCHECK193001..006 | FixedNativeCoverageCheckpoint.fromCurrentJvm/ordinaryProfile/capture；Agent public version/session/data port、4role/phase・7byte独立exec header vector | version0.8.15.202606040825、ROLE-INV-phaseとbefore/after session、5～16MiB/header01c0c01007。point名literal、defaultはIO0、attemptをagent前に一回消費、null/未知/short/large/header各byte/途中session変更でexport0。普通before-exec拒否、known/unknown非正常化、32並行1capture、byte複製でprovider配列不変更 |
| NEXPORT193001..005 | NativeCoveragePrivateFile.write/checked及びprivate file/directory/hash/digest、実hostLinux保持FD/TempDir；literal7byte・owner/mode/nlink/dev/ino oracle | owned new0600をwrite/force/通常close→dirsync→同name inode/fullbyte、既存/リンク/partial再使用0、null/size/owner/group/mode/ACL/type/欠落/未知/links拒否、create/close/sync/name replacementの非成功とFD帳尻・partial保存。pin/固定namespace/native exportは別実VM受入でありTempDir結果を代用0 |
| NHOLD194001..006 | FixedNativeCoverageStopHold.open/verifyOwner/install/shutdown/close/removeNative、公開Runtime provider境界、独立latch及び実host子TERM | default mainはhold無し。ownerだけactive、closed/notinstalled/foreign/null拒否、install/close一回消費、not-owned/null/unknownを成功にせず再試行0。元application finishedでもouter hook待機、interrupt保持、元provider停止操作0。実子JVM OLD_HOOK_RETURNED/APPLICATION_SCOPES_RETURNED後に生存→client C→CAPTURE_COMPLETE→exit143、0へ補正0。これを実API/Web/main受入へ算入0 |
| API/WEB MAIN001..004・RMAIN001..006 | RootServiceLauncher main/preflight/proof/environment、Api/WebProcessMain main/run/startNative/fatal；旧独立catalog/外部拒否試験 | default旧argv/5env/2FD、nonsecret stopped/fatalと50/70/30境界を保持、unknown原identity。PT有効時だけpin/ordinary1argv/Root before-execとowner-budget再照合、普通outerhold→全既scope帰還→stopped→terminal→capture complete→hold close→termination。native authorityは正規signed全gate及び実kernel/manager、fixture no-opなし |

public reflectionはRT/IAgent公開methodだけ、Privateアクセス/attach/reset/TCP/JMX/Production JaCoCo compile依存なし。Root Source及びruntime資格は実pin jar/CodeSource/RO・同boot/INV/PID/ticks/cgroup/NSS/current/sourceで別認証。Root before-exec dumpだけではreplacement/普通ready成功を表さない。普通terminalは所有停止・full journal・全kernelと結び、partial/fatal/失敗/未実行/異sourceを合格へ混ぜない。

実行は当12suiteのみ選択、Mavenprivate log・開始/終了/actualexit、Ubuntu26.04/JDK25.0.4/Maven3.9.12、dev-foundation/対象source各hash/XML/staticをsafe manifestへ記録。v4はstop-hold前72、v5はhold後78。coverageは開発累積の参考だけ、必要native/allcounter100未達。次は当群source固定fresh全6・正常署名配備・真正Root ordinary/TERM capture/全Scope/nativesource整合。既D3正常親/CHR/原本Backup/旧exec/stash/Scenario3/Currentを全保全、Root私有rawや秘密Git0。
