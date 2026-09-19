# 検索template実行結果

PG202/PT-SCR026～033、仕様007。選択8PT成功、正式reactor未実行。正式1589PT/84部分成果へ未加算。template/JS配信は実装済だが業務controller/実MQ/実Browser視覚/実NKgate・PGPT/IT/ST完成ではない。

選択 `/tmp/pgpt-pg202-green.log`、2026-09-20 07:21:08 JST終了、49.504秒、exit0。SHA256 `fcf2837b2d325f2945192fb97d511751a389b31028b85e6e14659368ad09a3a1`。Web選択57（新8、JS1/内数Node8、検索状態8、階層16、本文template8、Menu6、Error10）と依存選択成功、failed/error/skipped0、NullAway/Spotless/SpotBugs未解決0。変更WebMvcConfigurationは1class9method34line・branch0/0全missed0、除外なし。新規障害なし。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,ScenarioSearchTemplateTest,ScenarioSearchScriptTest,ScenarioSearchViewModelTest,ScenarioControllerTest,ScenarioDetailTemplateTest,MenuMvcTest,ErrorMvcTest
```

source def5afa3＋PG202作業tree/dev-foundation。Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12/Node24.19.0。新toolなし。入力/期待は007のpublic fixtureとCurrent/UI固定値、実際値は実resolverのDOM、明示URL、error/CSRF/metadata/audio、100結果/500speaker/10game、64並行をassert。CSSはCurrentから独立転記した25 desktop/7 mobile宣言と順序・900pxを全照合（実Browser画像ではない）。静的JS GET/HEAD200・text/javascript（Spring7.0.9 mime.typesの固定値）・実file一致、unknown JS404はresource単体の観測。実securityでは未知assetも認証対象であり、匿名302等を404へ変えない。

029は33Test ID/20source hash/3固定trace/JS JSON/007・008を収集、019は新suite inventoryと全trace欠落/誤値を拒否。正式command/対象commit/時刻/環境/exit/coverage/source・evidence hashは次manifestへ固定する。PG201JS1PTは既存で二重加算しない。
