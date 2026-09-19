# Animationメニュー・一覧HTTP実行結果

PG207/PT-SCR054～065、仕様013。選択新12PT＋既存Animation通信8/model8/template8/Scenario階層16/検索12＝Web64件成功。正式reactor未実行、正式1633PT/89部分成果へ未加算。watch/stream/実MQ/本番logging・起動/実NKgate・PGPT/IT/ST未完了。

初回 `/tmp/pgpt-pg207-selected.log`、2026-09-20 08:40:18 JST/45.526秒/exit0、新12・関連PT成功だがAnimationController.menuの重複catch3line missedで品質認定しない。SHA256=676bd5c6f6fcc4b31d750f85857ca1d4a299fcbf3d84f1c178461749f3fd4a96。BUG222/YKT178をbf320c93へ修正前起票。ANM合計はPayloadSemanticValidatorからprivate wire Resultへ入る前に必ず検査済み。controllerだけの重複catchを削除し、codec・閉model直接invariantと不正合計503試験は保持した。listの要求category/親子/duplicate制約とScenario searchの3応答bindingは追加条件なのでcatchを維持し全負例を再試験。coverage除外/試験期待緩和なし。

最終 `/tmp/pgpt-pg207-green.log`、08:42:40 JST/44.774秒/exit0、SHA256=0966dc7afd15d2ca53f976b1d51c08e90b80820c063a9e087eec21df03f821dc。Web64＋依存全成功、failed/error/skipped0、NullAway/Spotless/SpotBugs未解決0。AnimationController1class8method51line10branch全missed0、AnimationMvcConfiguration1class2method2line/branch0全missed0。BUG222/YKT178は正式回帰待ち。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,AnimationControllerTest,AnimationWireClientTest,AnimationViewModelTest,AnimationTemplateTest,ScenarioControllerTest,ScenarioSearchControllerTest
```

sourcebf320c93＋PG207作業tree/dev-foundation、Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12、tool変更なし。入力/独立期待は013の3URL/UI235 wire・15/4/1/20・0/1/50、全error/0102、malformed・semantic binding、null/unknown、USER/ADMIN・実HTTPHEAD本文0・security header/LogoutCSRF、escape、sub先行/欠落placeholder、64actor。全assert成功。公開trace065は6固定行、raw HTML/context/session/cookieはGitへ保存しない。

029collectorは65ID/29source hash/6公開trace/5Java coverage subjects/013014を追跡。branchless扱いはconfiguration3だけ、controller2はbranch正数・missed0を独立canaryで確認。019は71負canary成功、017の1と計72を正式gateで確認する。正式commit/command/環境/時刻/exit/coverage/hashはmanifestへ固定する。
