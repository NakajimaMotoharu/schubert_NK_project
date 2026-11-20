# API Repositoryの依存方向に関する工具単体テスト

NK-OPS-001、SYS-005／007、SS311 §3、WBS-F02-a、BUG-3386／3387、YKT-2722。対象は `tools/quality/architecture/ModuleDependencyAudit.java` のRepository認識と `REPOSITORY_DIRECTION`。正本SS311の「repositoryから上位層を呼ばない」を独立期待値とする。

| Test ID | 合成経路 | 期待結果 |
|---|---|---|
| PT-F02-REPO-001・002 | 従来のpersistence・monitoring.persistenceの任意内部名からapplicationへ | それぞれ一件の逆方向を報告 |
| PT-F02-REPO-003・004 | security・messaging/outboundに配置したRepositoryからapplicationへ | それぞれ一件の逆方向を報告 |
| PT-F02-REPO-005 | 別packageの@Repository付き型からapplicationへ | 一件の逆方向を報告 |
| PT-F02-REPO-006 | Repository内部型からapplicationへ | 内部型を発生元とする一件を報告 |
| PT-F02-REPO-007 | applicationからRepositoryへ | 許容され、逆方向指摘0 |
| PT-F02-REPO-008・009 | RepositoryFactoryまたは無注釈・別名の通常型からapplicationへ | Repository方向の指摘0 |
| PT-F02-REPO-010 | RepositoryからJava標準Clockへ | Repository方向の指摘0 |

JDK25の `javac --release 25 -Xlint:all -Werror -proc:none` で合成classだけを作成し、固定ArchUnitで読取。合成のSpring注釈stubはAPI JARに含め、外部依存を動かさない。修正後は独立した既35ケースの位置・input SHA・全指摘集合も比較する。実製品classは未生成、業務・実環境の実行0。

実行コマンドは `python3 -B evidence/01_PT/018_NK-OPS-001/input/5382_f02_api_repository_direction.py after`。修正前の元ログとfixture収納不備はPG40566、修正後はPG40568、独立照合はPG40570。対象source、JDK command、真正終了値、各Test ID、物理hashはmanifestに保存する。業務coverage、実六JAR、F02正式受入は別条件。
