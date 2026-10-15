# 現行Null解析gate実証

2026-10-15、PT-QUALITY-001/QLT-NULL-01～05、WBS-F03の部分品質根拠。Production a9/PG2802、工具実行HEAD ae38681e5。PG3360-current-null-canaries-v1、11:43:39.093293～11:43:45.675844Z、元wrapper0。既001_verify_null_contracts.pyを新-only私有出力へ実行、JAVA_HOMEはwork/toolchain/jdk-25.0.4、offline Maven repositoryはwork/toolchain/m2/repository。実command/全四POM-fixture hash/開始終了/元manifest-log SHAは公開manifest。既evidenceを上書きせず、Main/Jar/設定/VM/既3350のsource treeは変更0。

453の独立oracleどおり、valid nullable明示分岐/non-null collection参照はcompile0・NullAway診断0。invalidはcompile1、nullable dereference/return/collection element/argumentの四固定診断がそれぞれ一致、実診断数も四。expected compile1をProductionの失敗へ算入せず、compile-only canaryをProduction PTやcoverageへ加点0。4input hashは実行前後/current/a9のgit blobとも全一致。親POMのdefault-compileを実際に継承して拒否能力を確認したもので、文字列設定の存在確認だけではない。

この結果単独でF03全scope、全Production NPE不存在、正式451/四coverage100%やPGPT完了を認定しない。全Production clean compile/関連negativeと全3704の同source結果、format/staticの別検証を接続する必要がある。WBS受入差分0、正式1964/53・工数null・QA051final保留は不変。private fileは600/dir700で保全、公開は固定fixture診断とmetadataだけで秘密値なし。
