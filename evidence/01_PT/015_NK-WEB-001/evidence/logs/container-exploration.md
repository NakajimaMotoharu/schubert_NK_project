# 実Servlet HTTP境界探索（PT-WEB-109～112）

Branch dev-web、production基準321ed2d（Caddy source d95ce81）＋PG-D-109の未commit Tomcat依存/実HTTP fixture。Java25.0.4、Maven3.9.12、Tomcat11.0.25、PostgreSQL18.6。localhost以外へ接続せず、合成requestだけを使用。raw Cookie/CSRF/password/HTTP body/JVM出力はGitへ保存せず、この集約と原本hashだけを記録する。

Command（repository root）:

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am '-Dtest=EmbeddedWebSecurityTest,FieldCodecTest,OwnedTransferDirectoryTest' -Dsurefire.failIfNoSpecifiedTests=false test
```

| run / log原本（/tmp、Git外） | 終了JST / exit | 期待・実際 | SHA-256 |
|---|---|---|---|
| PT-WEB-container-20260909-explore-01.log | 2026-09-09 00:49:18 / 1 | fixture準備compile警告7件でWeb PT未実行。AutoCloseableのthrows Exceptionを具体LifecycleExceptionへ、deprecated mapping APIを現行公開APIへ変更。初期TDD準備失敗でProduction障害ではない | 0980bd828c56e5a908e0dc0252cd7a8a84e3c2038c4faca57c937c2dbf1f8a80 |
| PT-WEB-container-20260909-explore-02.log | 2026-09-09 00:57:37 / 1 | Web4件、109/111/112成功、110失敗（監査期待1件→実際2件）。proxy403/空body/error servlet0までは一致。後続assertは未実行で成功扱いしない。BUG-070/YKT-062を修正前起票 | da90c28c89c76863ed8fb4b766fd412be10d9986fa6fd04faa173e8904f42089 |

全production sendError検索はCaddyTransportContextFilterとWebCsrfDeniedHandlerの2箇所。前者は信頼context未確立の拒否にERROR再dispatchを発生させるため修正対象。後者は信頼済contextを保持するCSRF拒否なのでerror画面へのdispatchが必要で非該当候補。PT110の同一ID/件数とPT109/112の実HTTP回帰で確認してからYKTを完了する。

探索は全coverage/全module/正式gateを代替しない。全MVC・実TLS/Caddy・production bootstrap・NK Characterization・IT/STは未実施。
