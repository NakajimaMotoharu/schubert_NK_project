# Logブラウザ入力実行結果（限定試験）

2026-09-23 JST。Program NK-WEB-002/PG217/PT-SCR-092-A～H。正式結果ではなく、W01途中の選択試験。対象branch `dev-foundation`、開始HEAD `759bc06c` と本書記載の未commit差分で実施。後続正式runのsource commit/manifestで改めて認定する。環境はLinux/JDK25.0.4/Maven3.9.12/Node24.19.0。JS SHA-256 `b5cfbc9a689c91d0f14461e3e46dadb88844b5d0c38358d762dd241a5458efad`。

入力は公開synthetic q/action/pathのASCII・NFC・3/4byte UTF-8上限±1、CR/LF/TAB/NUL/孤立surrogate、欠落form/control。期待値はUI225の256/64/256byteとSS313の制御文字拒否・ASCII trimから独立手計数。Node DOM fixture8caseが成功し、対象JS1fileのline/function/branchはすべて100%、failed/skipped/todo0。Server validation・実HTTP・実NK CHRは別途未実行。

選択Maven command:

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=FieldCodecTest,ResourceScopeTest,LogSearchTemplateTest,LogSearchScriptTest,WebAuthorizationFilterTest,SessionSavedRequestTest test
```

終了code0。Web選択19件（Log script1内にNode8case、既存Log template8、Web認可4、SavedRequest6）、failed/error/skipped0。`/tmp/pgpt-pmo-20260923-js-selected-5.log` SHA-256 `b8f01933ed0e0838671f4654554f01e9736079c21ad460405846e5e1ff4c2a33`。初回の選択command3本は依存moduleに一致するTest名がないため不合格/未実行、4本目はSpotless未適用で不合格。formatter適用後の上記5本目のみ成功し、前4本を成功と数えない。秘密値・cookie・session IDは本書へ収録しない。正式coverage/manifest/evidence hash、Java4coverage/静的解析/CHRは未認定。関連BUGなし、SSC073の上位仕様は変更なし。
