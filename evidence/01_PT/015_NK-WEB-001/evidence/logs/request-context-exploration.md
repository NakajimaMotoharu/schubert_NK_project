# Caddy transport context・実CSRF拒否監査の接続探索

2026-09-09 JST/dev-web、PG-D-108/PT101～108は75a03c9/3ce44e3で実装前確定。UI222/226/252、SS313/314/342/351/352。421既存Java25.0.4/Maven3.9.12/Spring Security7.1.1/Session4.1.1/PostgreSQL18.6、追加dependency/toolなし。

| /tmp/PT-WEB-request-context-20260909- | 終了JST | 結果 | SHA256 |
|---|---|---|---|
| explore-01.log | 00:31:41 | NullAway2件、Optional fallback戻りのrequestId nullableでcompile失敗。BUG069、非合格/Web未実行 | cb241ffc405c2f28c4d1258f192efaa8542e5a1904f8d56c32c5ca44b30efa89 |
| explore-02.log | 00:33:26 | 新TDD fixtureのSpring repository constructorにClock引数欠落、testCompile失敗。Production APIを変えず正しい公開constructorへfixtureを訂正、非合格/Web未実行 | 6ee3deee088c769ac5b9bbd146ad9c91beacd4f41509c08ff6c71474342767f2 |
| explore-03.log | 00:35:30 | Web18件（新8/監査6/CSRF4）PASS、新3class全coverage100%、NullAway/format/SpotBugs0 | 43d78beae73fee661e813bead558ab32700c01c31ef9965482f8beb04f6929aa |

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am '-Dtest=WebRequestSecurityTest,WebSecurityAuditTest,WebCsrfIntegrationTest,FieldCodecTest,OwnedTransferDirectoryTest' -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

## 独立期待・実接続

偽X-Request-IDを無視しserver UUIDをrequest内へ保存する。UI222/SS313の監査/error view用途に限定して未規定response headerを追加しない。numeric loopback＋単一XFF/httpsを前段で再検査し、body/sessionを読むtest doubleのmethodを呼ぶと即失敗にする。既存内部contextの型、再dispatchのID再使用、同clientだけ維持、client変更/不正headerで403・下流0。非HTTP/null/UUID/attribute/response/chain/logger故障は正常化しない。

拒否監査はAUTHORIZATION_DENIED、reason PROXYまたはCSRF、route=/**、targetType=HTTP_REQUEST、server request UUIDを固定期待とする。PROXY拒否の非信頼IP/actorは省略。CSRFは検証済IPと閉principalのusername/roleだけを投影し、渡された例外のgetMessage/getCauseを呼ぶと即失敗にする。session/CSRF保持、Cookie新発行なし、HTTP403・本文/診断非反射を確認。

PT106はHeaderWriterFilter→CaddyTransportContextFilter→本物SessionRepositoryFilter/暗号化PostgreSQL repository→SecurityContextHolderFilter→本物CsrfFilter→Production WebCsrfDeniedHandler/WebSecurityAuditを接続。匿名/USER/ADMINと正・誤CSRF、独立fixtureの02/04×32 token、status200/403、下流1/0、DB token不変、監査は拒否だけ1件、Holder clearを検証。Login API/JMSをこのchainから呼ぶ処理はなく、CSRF拒否監査をAPIへ送らない。

PT105の直接handler状態確認には公開MockHttpSessionを使うが、暗号session接続の代用とはせずPT106と区別する。100独立request/client/UUID/response/監査を8workerで確認し、各ERROR再入は同じID、公開filter/handler monitorに依存しない。

## BUG069/YKT061全対象

1eaa62eで修正前起票。全production JavaのorElseGet検索該当は、新CaddyTransportContextFilter内のrequestIdとcontextの2箇所のみ。他Web/API/Protocol/Storageに同patternなし。両方を明示present分岐へ変更し、非null戻りを外側境界で確定する。抑止設定・nullable格下げ・test期待値変更なし。PT101/102/104/108で新規/既存/null UUID/誤型/属性故障/再dispatch/並行を実行し、検索だけでは閉じない。全moduleの静的解析と既存null負試験も正式gateで回帰する。

## 最終配線で必要な確認

本機のMock Servlet＋実DB接続PTであり、実Servlet containerのERROR/ASYNC登録、error page再dispatch、Host/origin/Caddy最終設定は未完了。特に未信頼transportのsendError後ERROR dispatchやlogger故障の外側error処理は、実containerの配線PTで403/非再帰/秘密非表示を確認する。CsrfFilterのDEBUG/INFOを許可しないWARN固定、Login success/failure/role handler、全画面/全起動/実NK CHR、IT/STは未完了。

## 正式gate

正式PT-WEB-20260909-03、sourced95ce812c1bd0a2958236de45daeb72c8e15f158、00:37:38～00:42:19 JST。全733件（Protocol80/Storage34/API394/Web184/CHR41）、Web001～108、failed/error/skipped0、5対象module line/method/class/branch100%、NullAway/Enforcer/format PASS・SpotBugs0。全7collector成功、BUG069/YKT061全対象再試験完了。実container/最終配線/実NK CHRは別gate。RERUN-001/SSC-045は独立したLogout期限論点として455で管理する。
