# 原JUnit属性欄の構造検証

WBS-G09／G08、SS354、451、BUG-3718／YKT-2918。Surefire 3.5.4ではpropertiesは任意の一容器で、各propertyにnameとvalueが必要。 [Apache Surefire 3.5.4 XML schema](https://raw.githubusercontent.com/apache/maven-surefire/surefire-3.5.4/maven-surefire-plugin/src/site/resources/xsd/surefire-test-report.xsd)

| Test ID | 入力 | 独立期待値 |
|---|---|---|
| PT-OPS-G09-JUNIT023 | 容器の重複、未知の子、value欠落、子を持つproperty | 全形で収録を拒否し終端JSONを作らない |
| PT-OPS-G09-JUNIT024 | 容器なし、空、name/valueを持つ二要素（空valueとescaped文字を含む） | 各試験一件、元SHA-256を保存して同じ原本を検証 |

PG43606の修正前は合成負例4形が受理された。修正 、PG43608の工具32件が成功し、元Protocol二群の各39 XMLと171件を個別に保存値と照合。元試験の再実行0、製品PT追加0、正式受入0。実行command・tool／原本hashは[PG43608](evidence/PG43608-reactor-property-shape-after-v1/manifest.json)。
