# Batch資源scopeの静的検査と通常試験

NK-OPS-001、WBS-F03/2-2-b、OPS009、UI251、SS343 SSC063／308、451 §5、YKT-2863。現 `652b79f5faa3d15686d27a1ab76d9407bbe4589f` でProcessResourceScope旧反射001を通常選択から撤去。現Batch／Storage正規JARの限定10物理。PT-OPS-SCOPEVALUE002～004は元の合成object／Throwableでnull、取得・解放順、bodyとcleanupの優先表を確認し3件全成功。実プロセス・systemd・DB・native・保留試験は作動せず、エラー・失敗・skip・選択漏れ0。

PT-OPS-SCOPEVALUE-STATIC001でfinal、private no-arg constructor一件、static二methodをclassfileで確認し、通常試験・coverageに加えない。生coverageは行32/34、method2/3、class1/1、branch22/22、命令100/107。private constructorだけが未測定。元の反射到達、他scope、全451へ認定を合算しない。

PG42928、2026-11-23 JST、対象source・原JAR・コマンド・JUnit・CRC hashは公開 `evidence/01_PT/018_NK-OPS-001/evidence/PG42928-batch-resource-scope-without-private-reflection-v1/manifest.json` SHA-256 `c40a7788ce230ea53beed527a79f9ecbfee081a1ef4d84b2f0ac503e10ef4e2a`。
