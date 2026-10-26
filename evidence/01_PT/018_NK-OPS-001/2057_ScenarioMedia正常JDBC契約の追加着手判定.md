# Scenario/Media正常JDBC契約・追加着手判定

2026-10-26、assessment群2366/P00801主・P00901関連0、開始.25/1/3 cap10、sourceb120eebab。Source/既存PT仕様/後続索引だけを確認し、**新fixture・harness・製品実行を作成/起動していない**。

後続索引はScenarioRepository=2044/1936、MediaRepository=2044/1936/1247。2044はSQL前の22methodだけをPT_DEFAULTとして限定し、SQL/row/readonly/autocommit/close失敗・実DB/実file/graph等のHOLDを保持している。今回の正常SQL候補は、この22の結果を拡張した合格ではない。

ScenarioRepositoryのgames/speakers/routes/filesはrows→read transaction確認→SQL/bind/row mapping→固定layout validation。SQL/不正row等の失敗はpreserveFatalを含むcatchへ接続する。MediaRepositoryも実DB/metadataを扱い、既TestのBeforeAllがApiLogDatabaseFixtureを生成する。既ScenarioRepositoryTestも同じ実DB fixtureを開始し、normalの名義で元Testを発見・実行すれば実DBを起動してしまうため、今回実行しない。

ScenarioのPT-SCN001～006にはgames/speakers/routes/files/searchの正常0/複数row・表示順・filter・page/上限、独立offset/DB ID集合・値bind・caller TX等が既登録。PT仕様にはQuery部品範囲PASSの歴史記載と、実PostgreSQL18.6/Flyway/限定roleを使用しH2等へ代替しない指定がある。MediaもPT-MED008～011/016～018/036等に8 stored query・descriptor/list/並び/値bind/caller readonly/TXが登録され、実PostgreSQLを指定する。

本確認は上記歴史runのXML/CRCを再回収して現sourceb120の実行合格へ再認定したものではない。既定の正常形を新proxyへ写しただけでは、承認済みの実SQL/DB後条件を代替できず、元WBS受入待ちの新規消化にはならない。独立した追加port品質確認自体を一般禁止する判断ではないが、今回読んだ正常形に新たな未登録契約は確認できず、重複実装/検証は採用しない。

判定=候補不採用（CANDIDATE_NOT_ADOPTED_DUPLICATE_OR_UNQUALIFIED_SUBSTITUTE）、追加Test/fixture0/製品実行0/新規受入0。現sourceの実DB SQL再認定はNOT_EXECUTED_HOLDとして残し、旧successを転用しない。SQL/row等のHOLDを別fixture・別routeで試す許可へしない。将来別の新欠陥/契約が見つかった時は、その必要性・実作用・拒否範囲からの独立性を改めて判定する。

次はG03の残golden65等、既存sourceの期待値起源・必要PG是正へ戻る。全HOLD/正式1964-53/17-190/工数null/QA051finalは不変更。今回の選定調査を製品PT/PASS/全体完成率に換算しない。
