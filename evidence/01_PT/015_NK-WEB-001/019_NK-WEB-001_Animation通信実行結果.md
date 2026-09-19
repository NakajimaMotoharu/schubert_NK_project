# Animation通信・保護read共通化実行結果

PG206/PT-WEB238～245、仕様018。正式22/source4e942a7485899d262a6d8d4eab56aad8228f7291、2026-09-20 08:25:04～08:36:55 JST/11:49/exit0で認定。全1633PT/Web374、failed/error/skipped0、6Java4coverage100%・Production5静的解析未解決0、41scope/71負canary成功。新8PTを1部分成果として追加、89部分成果843PT。新変更7class22method106line26branch全missed0。BUG221/YKT177は全対象の回帰・上限拒否・64並行再試験完了。実行command/環境/commit/各hashはmanifestへ記録、raw log SHA256=7754fa29ac786ba1d55b42666898599a48676bc359ac77816add585972e34c89。Animation HTTP/実broker/動画stream/実NKgate・PGPT/IT/ST未完了。以下は選択試験履歴。

初回 `/tmp/pgpt-pg206-selected.log` は2026-09-20 08:20:46 JST/32.019秒/exit1、Web44中1error、SHA256=71e7b8f7a0efbd6537c84034ac3bc029f121cd61fe2354227d4b748807f18157。BUG221/YKT177を0b58319fへ修正前起票。64総要求を上限128と誤設定したfixtureだけを12/8workerへ修正、Production上限は変えない。Web全constructorを検索し、既存正常1～12・意図的0/13拒否・他fixture非該当を確認。再発防止に既存上限拒否8PTと新64並行を含める。

最終選択 `/tmp/pgpt-pg206-green2.log`、08:24:12 JST終了、35.665秒/exit0、SHA256=4cff5d973d31d88bb6af2ca5d80c21a76f71d15d50ba8938f9020036def4217d。Web52/依存PT全成功、failed/error/skipped0、NullAway/Spotless/SpotBugs未解決0。新・変更7class22method106line26branchのmissed全0、追加除外なし。正式clean verifyで全moduleを再確認する。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,AnimationWireClientTest,ScenarioWireClientTest,ScenarioControllerTest,ScenarioSearchControllerTest,JmsRequestReplyClientTest
```

source0b58319f＋PG206作業tree/dev-foundation、Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12、tool変更なし。独立期待は018のUI232/235 header/data/record配列、ANM0/15/999、ANL0/1/50、10error code/固定profile破損、相関/context/layout/byte/長さ、VID・Scenario混入拒否、null/clock/ID/JMS/timeout/未知Error、64要求、SUBTRACK親、入力応答配列不変・結果の不変snapshot。実際は全assert成功。共通engine内応答copy消去は全finally経路の回帰とcode review、外部caller配列は不変更として直接検証する。

015collectorに8ID/4source hash/018019を追加。019は70負canary成功、017の1と計71を正式gateで実行予定。正式対象commit/command/環境/時刻/exit/coverage/hashはmanifestへ保存する。BUG221/YKT177は正式回帰まで未完了。
