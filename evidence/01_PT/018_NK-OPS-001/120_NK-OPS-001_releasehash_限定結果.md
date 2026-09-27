# リリースhash限定結果（PG300）

2026-09-27。Bootstrap111PT clean成功（21:15:32 JST）、全失敗/error/skipped0・NullAway/SpotBugs0。StartupReleaseManifest全classの6counter missed0。実VM native018/019はAPI/Web順次起動で成功、実2FD/proc/NSS/actual manifest bytes/ACL/closeを確認。初回同時Unit起動はA競合でAPI拒否・Webのみ成功なので組合せ成功に算入せず、順次双方成功を別記録。

HostだけではServiceStartupAdmissionのnative成功branchが未網羅。same-source Bootstrap jarをVMへ配布し、同class byteのhost111PT＋VM API/Web2実行データをJaCoCo ExecFileLoaderでmergeした限定報告は、33class/207method/945line/498branch・instruction5272/complexity456、全missed0。21:20:59 JST既存100% coverage-checkも成功。最初のcheckはCLI dataFileがreportだけへ効きcheckはhost単独を読みexit1、その事実も保全し、設定・rule・除外変更0で正しい合成実行データに対し再check。これは本単位のmulti-environment PTであり、Production全module/全scope/R2/R3合格ではない。

raw journal・agent data・root-only材料はGit外、manifestはhash/boolean/synthetic inputのみ。VMのfixture CURRENT/MANIFESTはBOM=false、config/permit/root hashも公開vectorで未認定。正式source858713c0b/run24/1964PT/48.3%は不変更。SSC089の現在epoch原本/fullissuerは未実装で対応中。
