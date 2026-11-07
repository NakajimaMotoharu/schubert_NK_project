# Storage八null・Proxy診断・個別レビュー結果

PG22842の八site理由/source witness・PG22844独立0、manifest `0cedf69d41aefd1cae1a0eefe1dd7d96de386311f473ad3c8bf9181e3d520dfc`。current source全29hashとraw102を保持、当八classified/適用0・残94未分類/全適用数null。source/rule/期待値変更0、engine/元Test再演0、元native/Root等compile/run/fixture置換0。metadata否定5を確認。

NullAssignment4は、fresh六root配列の欠落negative一、故障なしsentinel二（null時はguardで注入せず、故障種別と後処理期待は別assert）、捕捉→null消費→throwによる一回限りfault一。ReturnEmptyCollectionRatherThanNull一はinvalid proof providerのnull arrayを明示NPEと両close期待へ対応し、空arrayへの修正で負例を消さない。これは現実Root失敗cohortの回収ではなく既sourceのTest入力契約レビューだけ。

Proxy三siteはstandaloneの固定DirectoryCalls proxy。installed PMD7.28 ruleのJ2EE resource-loader contextとは用途が異なる。指定loaderからinterfaceとsignature型が参照可能であることが必要という[Java25 Proxy API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Proxy.html#newProxyInstance(java.lang.ClassLoader,java.lang.Class[],java.lang.reflect.InvocationHandler))の契約も記録した。実target loader visibilityは未測定・元Test未実行のまま。Proxyを実際に生成したりHOLDを解除していない。

原八の規則非該当理由を限定記録したもので、元native PT PASS/coverage/親品質の受入ではない。新unique/whole/leaf0、438/Java334/whole94/正式1964PT-53scope/工数null・全HOLD不変。次は残94を個別review、実違反は先行起票する。
