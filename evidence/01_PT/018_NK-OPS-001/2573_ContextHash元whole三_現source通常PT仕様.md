# 2573 ContextHash元whole三 現source通常PT仕様

2026-10-29/PG-D852/event2958/source0061・WBS-F03開始0.5/2/4pp cap10、Source canonical P00703/費用追加0。後続索引ContextHashは1241/1361/2569/70、当sourceの既12exec125method24suiteには含まれず、今回の未達は現source/runの独立whole資格である。既受入/旧Sourceの機能成功を新完成として再計上しない。

PT_DEFAULT：原ContextHashTest全三methodを非改変実行。Main ContextHash（9b0714ec）/AuthenticationContext（aaa18a4c）とTest（eafd2eb1）を全body/初期化まで読取。前者はJCA digest/private lockと配列wipe、後者はPattern/immutable値だけ。TempInfra/各held graph/Root/defaultNative factory/DB/鍵/ネット接続/host設定/実session等へ到達しない。Security.removeProvider/insertProviderAtは自己所有・専用child JVMのJCA registryだけを変更しfinally元配列/順序へ復元確認、OS/他JVM/providerファイル/アクセス権を変更しない。virtualThread/executorも当child所有、全classを実行し部分抽出・別fixture・HOLD迂回0。

| Test ID（元method） | fixture/操作・独立期待値 | 観点 |
|---|---|---|
| ContextHashTest#bug036CallerMonitorCannotBlockSharedDigest | 64 ASCII a、外からhashesをmonitor保持し別virtualThread計算。SHA256=ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb、5秒以内 | private lock、並行、境界 |
| ContextHashTest#asciiVectorsAndConcurrentCallsDoNotShareDigestState | a/b各64の固定ASCII・100task。bのSHA256=a0fab1377f49a759b57f63318262ebe89fabfc990e8e93ceac2984561482b9d4。Python hashlibで元byteから独立確認、production expected生成0 | 共有digest、null拒否、63/65/大文字/非hex/空、表示にhashなし |
| ContextHashTest#unavailableMandatoryDigestPreventsStartupAndRestoresProviders | 当child全provider配列を保持し除去、new ContextHashがNoSuchAlgorithmException、finally全元provider/順序一致 | mandatory capability欠如、起動fail closed、復元 |

実commandは14092 checked entry→javac25 release25/proc-none/Xlint-all/Werror→専用childJUnit whole3・parallel=false・既agent append=false/new session。元normal13832/全input・六Jar・全dependency/元Test/共有reporter資格13728を固定、timeout180秒は当childのみ。原成功/全回帰/nativeの確認再演0。14094はXML真件数/FES0/単一sessionとCRC・完全Main Source physical classを独立測定、protocol AuthenticationContextは補助依存でcoverage受入に混ぜない。新TestID/新機能受入0、BRANCH自然0はN/Aで四100へ補完しない。結果2574/原manifest/hash/退出・coverageを保存し未実行/途中/別sourceを合格としない。
