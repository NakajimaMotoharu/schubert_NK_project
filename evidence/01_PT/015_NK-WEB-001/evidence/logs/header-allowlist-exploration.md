# HTTP header・Login form allowlist探索

2026-09-09 JST/dev-web。BUG-067/YKT-059は9df8245で修正前起票、PG-D-106/PT091～094はe28f869で実装前確定。Web090～094、UI222/226/234、SS313/342/352。421既存Java25.0.4/Maven3.9.12/Spring Security7.1.1/SpringTest7.0.9、追加dependency/toolなし。

## 探索履歴（正式gateの代用にしない）

| /tmp log | 結果 | SHA256 |
|---|---|---|
| PT-WEB-form-allowlist-before.log | Web090のみ指定したためProtocolのno-test gateで停止。Web未実行、非合格 | 131f41f3089b4a3041824dc783988f0819d9b7553895f88c3eccffea9bb3a831 |
| PT-WEB-form-allowlist-before-02.log | Protocol5/Storage16のみ実行。並行準備中の新header sourceが未整形でWeb前に停止、非合格。BUG067修正前の実行再現とは呼ばない | 63f6fc82724ca44ff8178d43e4b7c7643879a1c2d5353cb11c76da9f5d081f26 |
| PT-WEB-header-20260909-explore-01.log | Web初期header fixtureがMock stream closeをsetCommitted callbackと誤認しPT092失敗、非合格。他追加allowlistはPASS。Production headerの期待値・実装は変更せずpublic close境界を観測するfixtureへ訂正 | 82997d4fc6d7c9231168acd0167530dee47b0995a29de0df1d8ca8c8afe52c4f |
| PT-WEB-header-20260909-explore-02.log | Web23件PASS（form9/header4/SavedRequest6/CSRF4）、新2classと修正converter全coverage100%、SpotBugs0/NullAway/format PASS | 98637de98b8a016c69d82217ac13aa404942593e956a2c7bd2b749988b7f11d0 |

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am '-Dtest=SessionFormLoginTest,WebSecurityHeaderTest,SessionSavedRequestTest,WebCsrfIntegrationTest,FieldCodecTest,OwnedTransferDirectoryTest' -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

beforeはtestまで、最初はWeb090のみ指定、before-02はFieldCodecTest/OwnedTransferDirectoryTestを追加。raw JVM/DB/session logは格納せずhashだけ保持する。

## 独立期待とBUG067/YKT059全対象

SS352 §8を正としてusername/password/_csrfの完全一致名のみ許可。旧sourceの未知項目欠落検査は静的読取りで確認した。PT090はprovider経由の未知role/空/大文字/unknown/query由来q、null enumeration/element/列挙故障を認証前拒否し、MQ0・sessionなしを検証。元のPT084はMock setQueryStringだけではServlet parameterへ反映されないため、未知queryの正常例を主張しない空query fixtureに訂正した。query由来名はgetParameterNamesへも独立追加して実際のServlet merge契約を模擬する。Productionからexpectedを生成しない。

| 横展開対象 | 修正・非該当と再発防止 |
|---|---|
| LoginFormAuthenticationConverter | 全parameter名を明示allowlist検査し、null/未知/Enumeration故障は固定LoginFormRejectedException。PT090と既存082～089で認証/並行/秘密消去まで回帰 |
| FormCsrfTokenRequestHandler | token抽出を全業務formへ共通提供するため未知業務fieldの拒否責務は持たない。PT050～053でCSRFだけの閉入力・MQ0を再試験 |
| EncryptedSessionRequestCache | request parameterを保存/再生せず、SavedRequest SPIは空Map、missing keyはnull。PT076～081で投影と非再生を再試験 |
| 未実装の業務form | 検索で不存在を確認。未実装を合格扱いせず411にallowlist/未知名PTの必須checkを追加、各後続Programで検証する |

検索条件: Web production getParameterMap/Names/Values、AuthenticationConverter、form binding。検索だけでは閉じず、上記全実装対象の非該当根拠と再試験を対応付ける。

## Headerの独立期待・scope

Test側の7header固定mapをSS352 §7.2から転記し、Production定数/メソッドから生成しない。HTML/error/media/staticと全status・HTTP methodで元status/bodyを保持し、競合/重複headerも一値へ置換。実HeaderWriterFilterの通常/finally/redirect/error/flush/resetに加え、public Servlet stream/writer closeのdelegateに到達する前のheaderを検証する。SpringTest Mockのstream close自体はsetCommittedを呼ばないため、closeを明示観測するtest doubleを使用する。private reflectionやProduction branchの除外はない。

各setHeader故障は元の公開Servlet例外を伝播し、勝手に正常応答や診断headerへ変換しない。外側error/redaction handlerは後続。100並行responseの混入なし。実Caddy/server・ERROR/ASYNC配線・role/画面/監査/実NK CHRは未完了。Current baselineは変更しない。

## 正式gate

次のroot clean verifyと全7collectorで確定する。PG/PT Program全体の完了、IT/ST完了は宣言しない。RERUN-001は455参照、独立作業として本sliceを実施した。
