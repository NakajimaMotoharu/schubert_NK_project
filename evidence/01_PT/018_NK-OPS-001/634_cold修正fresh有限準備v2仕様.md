# cold修正fresh有限準備v2仕様

NK-OPS-001 / SS343353 / SSC243244245246 / QA047 / BUG1017～1020・YKT786～789。旧1039失敗143/frozen1038、退役1060実0は不変更。新sourceのhelperはPg1062ColdOwnedPreparation/pg1062_cold_refs.py、hostW/guesttool pg1062-cold-tools-v1、SAVE pg1062-cold-prepared-v1。元slotを再使用せず、署名payload/原本/DB/Backup/Currentの期待値は不変更。

PT-DEP-1062001：生成ファイル集合3、新class/tool/SAVE/childpathだけで旧予約/源を引用しない。1062002：原本before→refs.prepare→原本after→hostRO→fullimmutableverify→有限5dirのphase順、数値SQL空白、既maintenance strictfixture/保持FD、nullargs/unknown ownership非正常化を独立literalで確認。host2 PASS。Java argument/readonly mount options goldenは変更せず同新classにcompile/run、null/未知operation・各flags異常を拒否する。

実段階command：`python3 -B tools/quality/vm/050_s1/pg1063_cold_preparation_compile_v2.py`（host/clean source/Werror・new-only frozen出力、未実行）、`python3 -B tools/quality/vm/050_s1/pg1064_cold_preparation_native_v2.py stage`（元PG932ABI固定/署名tools転送だけ、未実行）、同`prepare`（M/A→専用RODB+actualpulse→tenRefs/held signed189＋原本FD→全原値・完成原本独立二読→必要hostROだけ→既fullimmutableverifier→既maintenance不変で5空dir+6nativeworker finite→全原値/DBclose・server0/RefsFD正常close、未実行）。開始source/frozen SHA/実exit/時刻/input/expected/actualは各new manifestへ。

期待値は既SS/original fixture、Rootlinks3→8、maintenance0:0700/links2/empty、coverage711/子6各role、他全24-594/原本59/Backup47/credentials19/旧proof28/187release+2manifest/SHA/pin/signature/approval同byte・metadata。新epoch/原本書換/Rootpermit/業務start/DBcommit0。unknown/callback/DB喪失/close不明はscope保持し、別Source成功で補完しない。並行/再送は予約再発行0・第三client拒否/全元値二読・有限厳密whitelistで確認、実fault注入は別未完。

Tool-only実装、Production四coverage/正式53scopeの新認定ではない。実cold準備正常と独立afterまでBUG/YKT全体完了0。SSHprivate/credential/DBdump/原本内容/heap/tokenをGitへ入れず公開manifestは数値/hash/source/保存場所だけ。旧原本Current/stash7/COW/前失敗を保全する。
