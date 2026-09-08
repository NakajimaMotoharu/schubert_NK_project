# Menu・MVC/Thymeleaf探索記録

NK-WEB-001、PT-WEB-142～147、PG-D-115。関連FUN-002/AUT-001～003/SYS-006/TST-001～005、UI221～223/226、SS311/313/314/352。toolchain導入元/version/hashは421 §5.10、入力/独立期待は001 §14.11。

| Run | 終了日時（JST） | 結果 | 非格納raw log SHA-256 |
|---|---|---|---|
| menu-20260909-explore-01 | 2026-09-09 02:22:39 | exit1、未実行。初期PT fixtureでdb.web()のConnectionをDataSourceと誤認しtestCompile失敗。fixture契約と正しいtechnical table名を既存fixture/DDLへ照合して修正。production仕様違反ではなく初期試験準備不備でありBUG対象外、合格へ算入しない | 160c2260df6a58e9ab108365c2d38ea8f5c4332188f7b7b1bea53a360b63a2e7 |
| menu-20260909-explore-02 | 2026-09-09 02:24:12 | exit0、Web17（新Menu6＋既存実HTTP11）/Protocol5/Storage16 PASS、failed/error/skipped0。新5classのline/method/class/branch100%、NullAway/format/Enforcer PASS、SpotBugs0。正式全回帰は別runで確定する | 49cf30f32c8df5f9e2232dee56202cd8cf1a194def3a3e6e94696eed3573e454 |

command（repo root、JAVA_HOMEは421のJDK25.0.4）:

```text
./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=MenuMvcTest,WebSecurityChainTest,EmbeddedWebSecurityTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

実HTTP fixtureではDefault Servlet mapping `/`が実DispatcherServlet/Menu/template/CSSを担当し、`/login`と`/error`だけは明示synthetic servletである。Login POSTは実security chain/providerが処理する。USER7/ADMIN9、Current最初4cardの日本語title/説明/順、Logout form POST/CSRF1個、未知静的resource404、HTML特殊usernameのescapeを独立DOMで確認した。並行100回の新Cookie/新CSRF/actor/roleを照合し、native container session/JSESSIONIDは0件。Logout自体はRERUN001の未完成処理として試験対象外であり、成功を偽装しない。

HTML/template/CSSはPG/PTでDOM・方針を確認したもので、Linux server上の全画面見た目・操作・Browser matrix/ST/実NK Characterizationを完了した証跡ではない。raw Cookie/token/password/API context/HTTP body/JVM logはGitへ保存せず、期待文字列とTest ID・counter・coverage・hashだけを収集する。正式branch/commit/環境/実行時刻はmanifest.jsonへ記録する。
