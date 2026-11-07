# ReleaseContents公開データ型・単体テスト仕様

Program NK-OPS-001、WBS-P018-02（親owner/費用保持）、StartupReleaseManifest.Contentsの全custom Codeのみ。SYS002/004/OPS009/UI251/SS342343/SSC089095、原PG314 limited-3の6line/2methodは旧sourceの歴史証拠、今のaccessor拡張へ転用しない。Main7aedのnormal22084 bootstrap Jarを再利用しMain再buildしない。Java25/JUnit1.13.4、専用Test StartupReleaseContentsValueTest、対象physical一型、親StartupReleaseManifest全体は未受入HOLDのまま。

実施前判定NORMAL_PT：public value recordのconstructor/全copy accessor、供給するSchemaHistoryAdmission.Rowは公開schema/SQL metadataの値だけ。固定の公開synthetic version/digest/属性であり実manifest/署名/key/password/DB/run/permitを発行・読取しない。外側create/hostCreate/read/open/verify等、native/inode/Root/VM/DB/guarded四型/元RootTestの実行・compile/新回復fixtureはない。既存Test抽出ではなく独立した公開値型のwhole Code試験、親の経路へcoverage/完了を拡大しない。class-init/同exec実methodを独立照合し供給DTO以外のMain動作があれば資格化しない。

Test ID PT-OPS-RELEASE-CONTENTS001..008：①五引数のdefault mapとliteral values、②七引数のoriginal collection変更隔離、③両constructor scalar null、④各collection欠落、⑤null要素/key/value、⑥戻りcollection変更拒否、⑦schema row順序とconstructor時snapshot、⑧二worker/32独立copyとfinite5s join。fixture期待値はliteral version PG2802/公開digest 0を64文字、独立Map/List/Row定数から作り、対象accessorでexpectedを生成しない。正常/空/境界/null/例外/並行、外部I/O/再送はdata-only型で非該当。

coverageは当physical全Codeのline/method/class未達0、自然branch0ならN/Aを明記し100%と偽らない。record自動生成filterだけ、手動除外0。support Rowのcoverageを対象へ加算しない。Main/親sourceのwhole追加0・八Testだけ新unique候補、親whole94/正式1964-53/工数null/全HOLD維持。compile/lint/Werror・GJF/static・frozen八件一回・CRC/raw/方法/init/独立postを必要とする。失敗は先行BUG/YKT、source/command/終了code/XML/coverage/環境/hashをmanifestへ保存。原2/5/9pp cap10、WBS-P018-02 ORIGINAL_PLAN、追加tool費/N/T不明null。
