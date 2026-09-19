# 検索HTTP実行結果

PG203/PT-SCR034～045、仕様009。選択12PT成功、正式reactor未実行。正式1597PT/85部分成果へ未加算。検索HTTPは実MVC/loopback HTTPと実Web session DBまで接続し、業務電文応答は独立synthetic fixture。実broker/API/本番起動/REQUEST log/実NKgate・PGPT/IT/ST完成ではない。

## 失敗・修正・横展開

初回 `/tmp/pgpt-pg203-green.log`、2026-09-20 07:42:26 JST終了、35.810秒、exit1、SHA256 `79ad7a975cafd01eecb5504073fc5444509395f2c942cf13cac5b6a067a87440`。新12PTの2failure（BUG219/220）、他10成功。BUG219はSPK Game12byteの手書きexpectedへspace3を付けた13文字oracle、UI234の10byte code＋space2へ訂正しliteral長12・電文全長268も独立確認。YKT175で新SRC全672byte比較と全fixture固定幅・他NUKITASHI空白literalを検索/確認し、同誤値は1箇所だけ。helperは指定幅へcopy前にbyte上限検証、他oracleへproduction encoderを導入しない。

BUG220はMockMvcが内部描画したHEAD HTMLをHTTP transportのbody空と混同したassert。YKT176でWeb全head呼出を確認、新検索と既存JS resourceの2箇所。resourceはResourceHttpRequestHandler自身のHEAD処理として既認定なので非該当、検索はSCR041でMVCのsearch選択/正常描画/3要求、SCR042で実Tomcat HTTP HEAD200/body0/no-store/3要求を両role検証する。失敗を無視せず検証境界を分け、HTTP期待body0/Production/上位仕様は維持。台帳先行commit310f1cc3、修正commitは次source commitへ記録。正式再試験まで台帳未完了。

## 選択成功

`/tmp/pgpt-pg203-green2.log`、2026-09-20 07:44:38 JST終了、36.000秒、exit0、SHA256 `21b4d2aa872339a1d31fb8359953a642257d0216849f2cc387b54c59c1c39ce9`。Web37（新12＋階層16＋template8＋JS1/内数Node8）と依存選択成功、failed/error/skipped0、NullAway/Spotless/SpotBugs未解決0。ScenarioController全体1class14method107line33branch、全missed0、除外なし。入力不正はMQ0、SRC/GAM/SPK各失敗段階で後続0、0102終端、最終page補正/不一致、両role実HTTP/HEAD/session失効、64並行192相関/全buffer消去を確認。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,ScenarioSearchControllerTest,ScenarioControllerTest,ScenarioSearchTemplateTest,ScenarioSearchScriptTest
```

source6680450e＋PG203作業tree（台帳commit310f1cc3）、dev-foundation。Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12/Node24.19.0、tool変更なし。029は45Test ID/21source hash/4固定trace/JS JSON/009010へ拡張。019は新12method inventory・fail/error/skip/flaky/欠落/重複/未知/trace欠落を拒否し67canary成功、017の1と合計68は次正式gateへ。raw logにはsynthetic秘密値を含み得るためGitへ格納せず、公開trace/集計/原hashだけ保存。正式command/環境/commit/時刻/exit/coverage/hashはmanifestへ固定する。
