# API Life旧静的二行・個別契約判定仕様

2026-10-25/PG-D639後続/primary WBS-P018-05・P018-09参照追加0。P01805_API_LIFE_LEGACY_CONTRACT_V1、開始0.25/0.5/1pp cap1固定、fresh59残41/元90下限84・不明2/正確null・80大型抑制/保全buffer2維持。対象 source3641d0f49/1873が保持するLife raw PMD9中のinstalled volatile/empty Runtime catch二行だけ。既review7を変更せず独立source/vendor/JDK bytecode/SS342へ結合して、適用性と必要是正・残る実試験依存を具体化する。

純読取とjavapによるbytecode読解だけ、Runtime.removeShutdownHookやApplicationShutdownHooksを実行しない。元9183/9185と現在9210のLife source/class byte同一を確認し、前sourceのPT/coverageは現在へ移植しない。JDK25.0.4 Runtime→ApplicationShutdownHooks.removeのforward、shutdown中hooks null→ISE、runHooksが保持集合取得後null化をbytecodeで確認。現catchはその既知競合だけを捕捉し、owner close finallyがfinishedを通知する、という根拠を限定記録する。

volatileはboolean公開可視性とcompound owner claimを分け、ruleの一致を理由なく非該当化しない。完全な是正が必要と判断した行は未解決として残し、利用者向け仕様を変えず内部是正群へ送る。新試験PASS/実測counter/全静的・Program PT・451への加算0。source改変/Hook/TERM/実Main/VM/DB/native等HOLD解除0。metadata反例で未知行/例外範囲拡大/元sourceを現在資格とする誤判定を拒否し、1879へ結論/全hash/次工程を記録する。
