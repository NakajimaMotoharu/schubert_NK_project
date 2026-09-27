# 165 新版実候補：同bytes RW拒否/host RO受入

Program NK-OPS-001。RD SYS002/004/OPS009/DAT009、UI212/251/253、SS343/SSC097098。PT-OPS-NATIVE-028、BUG305306/YKT238239。source db4c6a7c6d8eb2b55af35b334df5b720fa185f49、dev-foundation。生成済tool sourceと実artifactのhashはmanifestに固定する。

06:43:41 JST package/runtime inventory assembly exit0（skipTestsはPTではない）。new0.1.0-PG316は169payload/61GAV/23SQL、manifest38,003byte SHA2154c63c8895c1fa25fe2ed9e6a6abba0c47ebe7127d4e50cfbce2106e0498bd。GA重複0、一次Flyway13.4 checksum expectations、Commons Logging1.4.0/JSpecify1.0.1。旧315候補/署名/exec/原本は不変更。

候補外の新fixed tool cohort /opt/pgpt-native/PG316、既存fixture pinned Ed25519公開鍵と新manifest316.sigを真正root/MORNING/M/A下で消費。秘密鍵はHost Git外のみ。06:47:28～29 JST hostRWはREFUSED、start1/ExecMainStatus1、署名milestone成功。停止/PID0/真正固定leaf不存在後にcoverage退避。host bind/remount ROにだけ変更し、06:48:01～02 JST同candidate bytesでstart0/ExecMainStatus0/PASS、fullBOM/23SQL/旧current不変を実測。初回旧315のGA不適合RWとは違い、この組は同valid bytesのRW/RO比較である。

RO成功後のstopは完了したが、不要reset-failedでUnit GC not-loadedとなり保全shell exit1（BUG306）。修正前起票し、同保持execを再試行で上書きせず別保全commandでinactive/dead/PID0/親cgroup存在・固定leaf不存在を再確認、RO execをcopy/hash。再実行のprobe成功へ捏造しない。原本3hash/current旧pgpt-native-301/approval不存在を再確認。

provisional/NATIVE028-PG316に公開manifest、sanitized結果・input/期待/実値/source/tool/exec hash、Bootstrap同class-byte host2217＋RW/RO coverage reportを保存。private exec/署名/key/tarはGitへ保存しない。Current baseline不変更。真正host factoryの実行は限定受入であり、Production pin custody/approval発行・RootReleaseAdmission/schemaDB・V023・全親/M-A-全Unit-INVALID・permit/main/実NK/R2R3は未達。正式run24/1964/53scope/48.3%は不変更。
