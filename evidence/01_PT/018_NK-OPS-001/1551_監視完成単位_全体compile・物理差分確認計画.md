# 1551 監視完成単位 全体compile・物理差分確認計画

2026-10-23、P018-09/同group1805の完成単位品質substep。開始見積1/2.5/5pp・上限10ppは増額しない（追加費二重計上0）。Production sourceは当48PTのc285c38ac4fcc3f16bfd3d2051ec76c352227f74に固定し、後続文書/toolのoperator commitをsourceへ付け替えない。

操作事前判定：PT実行でなく自己所有新onlysnapshotのcompile/package＋static byte読取。七POM(root+六module)にexec/antrun/native実行pluginなし、既Compiler/Enforcer/Spotless/Jacoco/Surefire/Jar/SpotBugsだけを確認。六moduleを明示選択しcommon moduleを選ばず、offline `-am -DskipTests=true package` で全Main/Testをcompileする。Surefireを実行成功と数えず全PTはUNRUN（0実行）、verify後段の全体coverage/F03も受入しない。Root/noargs/VM/DB/Broker/Caddy/service/key/配備/拒否操作を発行しない。native-access JVM設定は未実行Surefire用であってnative呼出しの許可ではない。

PG7030はcompile/package子終了codeを直ちに保存し、原source/archive/POM/全input/hash/所有process/command/log/六Jarを保存する。全元XMLが生成されていないことを確認する。既begin/終端のあるjobは再発行しない。compile-onlyの結果を元4222成功の再演/新全体試験PASSとしない。

PG7032では実六Jarの全classを元e7/PG6930 qualification728682a9/全1669physicalと比較し、原class byteの保持、追加15physical（監視実行14＋package-info1）だけがBatchの宣言packageに属すること、当c285/PG7028 class hash全15と一致することを確認する。不一致は未知/未受入として保全し、debug差を無根拠に同一と扱わない。元SS/既artifact/主費ownerを維持し、新classの主所有P018-09/C07共有0追加費を明示する。485の歴史/現候補を未完のまま偽更新しない。

同六Jarへ既ArchUnit1.4.2/固定五ruleを静的importして依存境界0を確認する。対象classのload/init/executeを行わず、旧11canary成功確認の再演なし。実class数/六module/全rule/dependency/call/hashとchild exitを保存し、旧全体PTやnative/全coverageへ合算しない。F03 Root11・allactual/拒否対象未特定HOLD維持。

新source全体451/正式PR・工程gateの全PT/CHR/native/四counter100/traceには未達が残る。今回の成果は当pure経路の実測資格と全体compile/物理joinであり、正式1964/53や工数nullを更新しない。保全前又は後続変更で必要な品質検証ができない場合は未認定として具体範囲を記録する。
