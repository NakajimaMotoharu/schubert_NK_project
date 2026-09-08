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

探索03は同commandのtest選択へWebRequestSecurityTestを追加し、末尾にorg.jacoco:jacoco-maven-plugin:0.8.15:reportとcom.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:checkを追加。2026-09-09 00:59:52 JST、exit0、Web12件（新4＋既存8）/Protocol5/Storage16成功、SpotBugs0、NullAway/format/Enforcer成功。原本/tmp/PT-WEB-container-20260909-explore-03.log SHA256 acb5607c2edbc68a462843c2722e2058c8c0727d32ac8f2d39697fa2e285df2c。

BUG-070はproxy拒否のsendErrorを除き、403を設定して監査後return。PT110は不正proxyの監査1件/UUID1/DB0/error servlet0を確認し、信頼済CSRFのerror servlet1・元ID一致・監査1件も確認。全2sendError候補のうち残したCSRFはPT109/110/112で実際にerror viewへ到達する非該当根拠を検証済み。PT104は削除したsendErrorの人工故障から、実際に呼ぶsetStatusの公開故障へ差し替え（status設定自体が失敗したのでMock初期200が残るが、例外は伝播し下流0）。HTTPの独立403/監査oracleは変更しない。

正式run04（source3cd44d2、01:00:53～01:05:25 JST）は全737件・全coverage100%・静的解析0/exit0。ただし015 collectorで新4Test methodの(Path)署名欠落により厳密一致検査が停止した（BUG-071/YKT-063、修正前起票）。先行6collectorは収集成功。run04だけをWeb全証跡完了とはしない。新4mappingに実JUnit署名を明記し、既存108・集合/件数一致検査を維持したまま、修正collectorを含むsourceを新runへ固定して再実行する。

探索は全coverage/全module/正式gateを代替しない。全MVC・実TLS/Caddy・production bootstrap・NK Characterization・IT/STは未実施。
