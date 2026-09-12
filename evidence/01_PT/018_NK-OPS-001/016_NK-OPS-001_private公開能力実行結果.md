# NK-OPS-001 private保持file・名前付き公開能力の実行結果

正式確定: PT-WEB-20260912-03/source194667c104b091e2f303805b1a908602bbe52319、2026-09-12 21:44:36～21:52:02 JST、終了0。全1133件（Storage58/Batch79を含む）、4coverage100%・Production静的解析PASS、35scope/17負canary成功。PFILE001～008はOPSだけに所属し、同scope全66 PT、共有storage全class coverageは全回帰から取得。BUG150/YKT116は全対象修正/非該当根拠と再試験を完了。manifest.json・checksums.sha256を正とする。以下の探索記録は履歴であり正式runの代替ではない。

015/PT-OPS-PFILE-001～008、PG-D-153。2026-09-12 21:41:40 JST終了のStorage58/Batch79＝137 PT探索は成功、4coverage100%・静的解析PASS。正式20260912-02へ遡及算入しない。次のsource固定全reactor/collector照合を待つ。root/属性/同run/parent lifecycleを満たす上位publisherは別残件。

実行: JAVA_HOME=work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-batch -am verify（work領域の絶対pathを使用）。終了code0。新8件にfailed/error/skippedなし。証跡所属検査017/019の17件成功。BUG150/YKT116はcollectorの反復matrix修正でありProduction障害ではない。詳細はevidence/logs/BUG-150-YKT-116.md。
