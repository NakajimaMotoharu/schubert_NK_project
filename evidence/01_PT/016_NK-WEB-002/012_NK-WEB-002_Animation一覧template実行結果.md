# Animationメニュー・一覧template実行結果

PG205/PT-SCR046～053、仕様011。正式21/sourcee4eb018d817bf234d646246f8a5166c21868b3b4、2026-09-20 08:05:26～08:17:17 JST、clean verify 11:49/exit0で認定。全1625PT/Web366、failed/error/skipped0、6Java4coverage100%・Production5静的解析未解決0、JS3coverage100%、41scope/70負canary成功。PG204と合わせ2部分成果16PT追加、88部分成果835PT。Animation HTTP/MQ/動画視聴・stream/実Browser/実NKgate・PGPT/IT/ST完成ではない。実行command/環境/対象commit/各hashはevidence/manifest.json、raw log SHA256=d841d9b16cbea9b2e76a4e0b36955941206cc151689dabebb8accfdc31a5a2f3。以下は選択試験記録。

`/tmp/pgpt-pg205-green.log`、2026-09-20 08:04:18 JST終了、51.096秒、exit0。SHA256 `617379e8cedfbd548d5e72f5eb41a8919b98d9ef7a018df1a87eb8d0424bd0d7`。Web77（新template8/model8/Search template8/本文8/階層16/検索HTTP12/JS1/Menu6/Error10）と依存選択成功、failed/error/skipped0、NullAway/Spotless/SpotBugs未解決0。WebMvcConfiguration1class9method34line・branch0/0全missed0、追加除外なし。PG204新4class28method91line52branch全missed0も維持。新規障害なし。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,AnimationTemplateTest,AnimationViewModelTest,ScenarioSearchTemplateTest,ScenarioDetailTemplateTest,ScenarioControllerTest,ScenarioSearchControllerTest,ScenarioSearchScriptTest,MenuMvcTest,ErrorMvcTest
```

sourcec9ef00bf＋PG205作業tree/dev-foundation、Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12/Node24.19.0、tool変更なし。入力/独立期待は011のCurrent literal・3card/5本3row/4OVA/0・50・MB丸め/escape/CSRF・64並行。実際は全assert成功、CSS7desktop＋900px1規則全宣言・順序を照合、実Browser画像ではない。029は53Test ID/26source hash/5固定trace/JS JSON/011012、015はPG204の8ID/016017を追跡。01969canary＋0171＝70は次正式gateで確認する。manifestへcommand/環境/commit/時刻/exit/coverage/hashを固定し、公開trace以外のraw HTML/CSRFはGitへ保存しない。
