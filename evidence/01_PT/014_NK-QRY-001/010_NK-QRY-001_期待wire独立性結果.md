# 質問照会expected独立性・限定結果

2026-10-26 14:11 JST、source21228608b9defca3eb6fac7e0485f28a56925246（Production Main21d7c304不変更）。009仕様/PG-D678/BUG1811・1812・1813/YKT1562～64。実行環境Linux7.0.0-38-generic amd64、JDK25.0.4+7/Maven3.9.12/PMD7.28.0/Checkstyle14.3.0/GJF1.36.1、詳細command・各stage終了・source/tool/dependency hashは下記manifest。

公開manifestは `evidence/01_PT/018_NK-OPS-001/evidence/provisional/` 下。下表のpathはその相対名。

|path|真正結果|SHA-256|
|---|---|---|
|PG10276-api-shared-context-v1/manifest.json|42site/30sourceの文脈レビュー、41欠陥認定なし/1不足。製品PT0|67f6f37f1052e8a4787dd535258aa69cf087eec6be4ce029881233a700c50b70|
|PG10278-query-wire-oracle-metadata-v1/manifest.json|整形・定数化前の24vector/5境界/配列独立メタ確認0、履歴のみ|dffc9f4b23b7ce00bc7b46029c77ba44fa41c27673a9d6a95d6db46f24543171|
|PG10280-query-wire-oracle-static-v1/manifest.json|raw29/CS0/処理error0、exit1を保持|873e68c216c533f663dc6840924de3313ef59e1cac3d6a072106c4d0bac3f821|
|PG10281-query-wire-oracle-static-v2/manifest.json|新helper重複一是正後raw28/CS0/処理error0、exit1保持|8e68da33c559ef0de554823e6db8e0a03724dffa85619616a7e5e5be8188d626|
|PG10282-query-wire-oracle-metadata-v2/manifest.json|当helper SHAの24全wire hash一致/5拒否/配列独立、exit0|c0e532154eb45e90684a425696ec52630e4e8ef5eb6de4a8089e4d30092f4d4b|
|PG10284-query-wire-oracle-six-compile-v1/manifest.json|当source六jar正常compile/NullAway、exit0、PT0|34ab5aef610fb1352732c926c7ca56438fc38b8434d218196d34f693aa6adbf0|
|PG10287-query-wire-oracle-source-post-v2/manifest.json|独立source/byte照合exit0、元assertion108/全Main1843同byte・旧Test1939同byte/対象二変更＋新helper一|f6c380e1e7a6971e8b79eaf6da9b5df25b4efdee65c206cf3b91ef4028e29fb3|

元@Test内layout七・固定QSD/NTD二caller、wrapper新委譲一、Application直接一を分離。元二Testの75/33assertion・全method・移動したbyte配置をtoken照合で保持、GJFのSQL literal分割は同値連結して照合する。新oracleにProduction import/request判定/DB/crypto owner参照なし。メタ実行classpathは自己二classだけでProduction class利用不能。元業務PTはNOT_EXECUTED_HOLD、coverage未測定、新製品PT/受入追加0。

PG10286はcaller七を全文で数えて新helper委譲一を含む八となり、guard exit1/OUT生成前停止。BUG1813修正前起票・原工具保持、V2で元Test領域七へ限定。他guardを削除せずtoken/byte照合0。製品再実行なし。

raw28のうち19は既二Testの重複literalで未是正。残九はStandalone Testの固定proxy loader六（JavaEE rule対象外）、null constructor負例の配列一要素設定一、fixture metadataのchecked ExceptionをAssertionErrorへ変換するTest callback一、二回目openにfaultを入れるTest計数literal一。Production規約を緩和せず具体文脈のみ記録し、原28/当sourceを保持。新helperにPMD指摘0だが全F03は未受入。

Scenario/Mutation/Logの同種helperは2046の固定offset/独立LP/JCE/別固定vectorを参照し、当問題のProduction Query profile判定を共有しない。既結果を実行し直さず根拠だけ記録。全G03/451/CHR/native/正式1964-53/既17-190/工数null/QA051final/全安全HOLDは不変更。source trace当三pathは次batch登録までpending（旧行のruntimeを上書きしない）。
