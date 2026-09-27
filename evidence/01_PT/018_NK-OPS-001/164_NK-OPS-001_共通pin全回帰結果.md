# 164 共通pin・boot A 横断回帰

保全後に329生成JUnit XMLのproperties/system-out/system-errだけを機械redactし、JUnit署名/件数/結果を保持。各file記録は生成原本SHAとredacted file SHAを区別し実hashへ更新した。raw JVM properties/試験stdout/stderrはGitへ格納しない。元target XMLはGit外に保持、coverage/static XMLは非秘密のclass/counter結果。

Program NK-OPS-001。RD SYS002/004/OPS009/DAT009、UI212/251/253、SS311/343、SSC097098。Test ID FULLBOM006008/LOCK008/ModuleDependencyBoundary、BUG298299303305/YKT231232236238。

source db4c6a7c6d8eb2b55af35b334df5b720fa185f49、branch dev-foundation。triggerは共通POM/JSpecify/logger/cross-role security matrixとboot A変更。2026-09-28 06:40:41 JST終了、exit0。全6 clean test/JaCoCo report/SpotBugs check、明示Node。2,217PT（Protocol80/Storage149/Bootstrap175/API742/Web555/Batch516）、failure/error/skipped各0、全module SpotBugs0。NullAway/ErrorProneを含む既定compileも成功。

provisional/PG316-regression-2217 に329JUnit、6coverage、6static＝341XMLを次Maven前に退避。各XML size/SHA、suite件数、全Production compiled-class SHA（174/70/66/320/206/220）とmodule counterを保存。manifestに実command/toolchain/source/時刻/exit/log hash。大き過ぎた一括metadata応答は不採用、完全な40class/25file chunkで保存。XMLの退避・全hash確定までsource/test/config/toolsを固定した。

Protocol/Storageの4指標missed0。Bootstrapはbranch37/line11/method4、API/Webは各branch1/line19/method3、Batchはbranch0/line42/method19が未達。Production main、真正host factory、RootReleaseAdmission/RootApproval、worker NativePorts等を除外・到達不能扱いにしない。全試験成功を正式coverage100%又はR2/R3へ読み替えない。

BUG298/299の独立境界/bin vectorとBUG303/305のboot/pin literalは全回帰成功、nativeの新版同bytes RW拒否→RO成功は次の実測対象。旧candidate/署名/native exec/原本を保存したまま、新0.1.0-PG316を実package/runtime inventoryから生成する。assembly -DskipTestsは新しいPT合格ではない。正式source858713c/run24/1964PT/53scope/中心48.3%は変更しない。
