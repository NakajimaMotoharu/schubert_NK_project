# 六表列検証の現SqlQuery

NK-MIG-001、WBS-F03/2-2-b、関連P019-03、UI242/254、SS343/354。対象は `MigrationMasterColumnVerifier` のverifyおよび内部SqlQuery、PT-MIG-COLUMN001〜026。入力は既仕様084等の独立V002列matrixとJDK Connection／Statement／ResultSetの合成proxy。6固定SQL、66カラムの値・順、NULL・未知値、close順、例外同一性と抑制順、borrowed所有、64並行を元期待で照合した。PG42834で旧1物理から現2物理への変更を確定し、既試験13箇所のchecked契約を整理した。元oracleは試験ソースの逆変換で完全一致。

PG42836、dev-foundation、2026-11-23 JST。現Bootstrap JAR二物理、JDK25.0.4、JaCoCo 0.8.15と元JUnit SDK。通常26成功、F/E/S 0、単一sessionの実CRC `52e8c095106a023d` に85/85 probe、行83、method15、class1、branch46、instruction526の全missed0。`SqlQuery` はabstractのみの自然NoCode。手動除外・別exec合成なし。SpotBugs包括型13→0、残raw1はJDK InvocationHandlerへ3種の意図的Throwableを渡す故障注入、PMD生8は有限Executor5と当JDBC型に対応するproxy ClassLoader3、Checkstyle0。抑制なし。実DB、COPY、正式451は別条件。元試験、command、開始終了、公開XML、counter、execとハッシュは [PG42836 manifest](evidence/PG42836-master-column-current-v1/manifest.json)。BUG-3629／YKT-2853限定完了。
