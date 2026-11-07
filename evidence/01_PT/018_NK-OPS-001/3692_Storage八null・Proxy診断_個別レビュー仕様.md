# Storage八null・Proxy診断の個別レビュー仕様

F03/411451/SS311352354、原1/3/7pp cap9、CONTRACT_AUDIT/SOURCE_REQUALIFICATION。current Storage29 raw102のNullAssignment4/ReturnEmptyCollectionRatherThanNull1/UseProperClassLoader3だけをsource・rule・owner・意図へ対応する。元source/ルール/期待値の変更0、native/Root/process/filesystem/credential/元Test compile/run/fixture置換0。レビューをPT PASS/coverageへ計上しない。

nullはすべて同じ理由で除外せず、独立array欠落negative、故障注入なしのsentinel二箇所、一回限りcleanup障害の消費、invalid proof providerを区別。sourceのguard/assert/expected exception/消費順を確認し、空arrayへ直して負例を消さない。Fixture fieldは実Rootの失敗状態とは区別する。

Proxy三箇所はstandalone Testの固定DirectoryCalls interface proxyで、J2EE resource読込ではないことをsourceから確認する。Java25公式APIの指定loaderからinterfaceが参照可能という契約を記録する。実targetのclassloader visibility/実native結果は未測定のまま、実行で確認しない。Root11/拒否対象未特定操作や親runtimeのHOLDを解除しない。

SDK src.zipは当JDKで利用不可だったため、Java25公式Proxy APIをread-onlyで参照： https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Proxy.html 。これは引用した型契約の確認で、元Proxy/fixtureを生成・呼出しする代替実行ではない。

八件の理由・関連source hash/明示witness・独立post/否定guardを保存し、raw102は不変のままclassified8/未分類94と分離する。その他の適用数はnull、全F03/451/正式1964PT-53scope/工数null・全HOLD不変。
