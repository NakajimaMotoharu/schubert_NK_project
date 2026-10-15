# F02基盤build・依存境界の限定照合

2026-10-16、PT-OPS-3550-001～003。WBS-F02/SS311/342/421/451、current4856/3414元3712/545/1643。親F02はSYS13要件を持つため、toolchainの限定成功で全leaf受入にしない。

独立期待値：Java25（Ubuntu版25.0.4）、Wrapper固定Maven3.9.12、Production六moduleと別Characterization。SS311のcompile/runtime辺はProtocol/Storageなし、Bootstrap→Storage、API/Web→Protocol/Storage/Bootstrap、Batch→Storage/Bootstrapのみ。Web→APIは既PT専用edgeだけ。移動済api.* binary名は物理Bootstrap所有で照合し、名前だけで業務API artifact依存と誤判定しない。StorageのJDBC/JMS依存、Bootstrapの業務HTTP/JMS依存は拒否。

操作=導入済toolのversion/実行file hash、全七POM/wrapper/正本、既真正3712 build/Jar/Source hashを読取。全回帰/VM/業務/再配備/新install/upgradeは発行0。正常及びnull/欠落/未知/禁止Web→API/Storage→JDBC/cycle反例は純fixtureで検証する。toolchain単体に業務再送/transaction/並行処理やJava coverageを適用せず、6module全PT/global四100/F03/ITST合格の代替にしない。

コマンド：`python3 -B -m unittest pg3550_current_toolchain_contract_test`、`python3 -B tools/quality/pg3550_current_toolchain_contract.py`、PYTHONPATHは既tools/quality/vm/050_s1。spec/manifestにactual exit/版本/Source/hash・SYS未確認範囲を記録。初期ad-hocの誤ったstandalone Maven pathは127/Maven未実行、既Wrapper cacheを実探索して3.9.12/Java25.0.4を確認。build失敗に算入せず、環境障害と誤認しない。

未完＝SYS005全業務MQ、SYS006全画面互換、SYS007安定性、SYS010実local素材、SYS012～014入口/TLS/交換可能性等のcross-scope join。これらと他SYSを個別に証明してからF02三criteriaを認定する。外部承認の再質問・WBS期待値緩和・費用/coverage除外0、通常区切りで停止しない。

## 結果追記

3550 actual0/純2成功、公開manifest **8147690882fc46b9544169b08e1f1333c2f2455a72a38a65fe72e8b0210ddd59**。実local Java25.0.4/Ubuntu build25.0.4+7-1-26.04-Ubuntu、Maven3.9.12/848fbb4bf2d427b72bdb2471c22fced7ebd9a7a1・UTF-8/Linux7.0.0-38をcapture、binary/wrapper/七POM/依存/文書hashを保存。全六graph/compat分離/Storage-bootstrap境界0、Batchでapi.*と見える五型も物理Bootstrap所有を照合。6moduleの新buildを発行せず3414真正3712/545/1643の既実証へjoin、F02/F03/正式受入0。

PT-OPS-3550-004＝3552 signed current187/BOMdc535のProject Jar全1643 classを実読、全header major69（Java25）、重複class0/各module class数は3414独立inventory一致。公開manifest **1ea935ec969316dd05b38b6a44e122fec39cf56137a2df920eab9e1dc136a49e**。golden header `cafebabe00000045`、null/空/短縮/誤magic/major68/70拒否を純2で確認する。3rd-party JarへJava25 majorを強制せず、Production六Project Jarだけを対象にした。

これはF02のtoolchain subset終了であり、SYS13項目のcross-scope受入やIT/ST物理環境・公開経路確認を完了としない。既13要件の発見でscopeを増やしたのではなく、labelだけから過小範囲へ限定しないための照合である。実際の業務製造/PT費は各既owner、F02の残りは証拠join/受入判断だけにし、共通費を二重計上しない。
