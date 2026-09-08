# Login JMS client探索・横展開

2026-09-08 JST/dev-web。NK-WEB-001/FUN-001/AUT-001～004/MQ-004、UI226/232/234、SS312/314/321～324/352、PG-D-101/PT-WEB-054～059。先行仕様8ce766e。JDK25.0.4/Maven3.9.12/既存Artemis2.56.0/JUnit5.13.4/JaCoCo0.8.15。新規tool依存なし、421既定toolchainを使用。

| 探索（/tmp/PT-WEB-login-） | 終了JST | exit/結果 | raw log SHA256（Gitへraw非格納） |
|---|---|---|---|
| explore-01 | 21:59:31 | 1、新6件中1 error。BUG-060修正前登録1be190d | b107974d8080511608bdfb1ddbb08da6e239ed923726cc40fe48aa818d10723c |
| explore-02 | 22:01:47 | 0、新6件PASS。ただし0200横断review不備を後続BUG-061へ登録、最終合格ではない | 088cb6f3cf61248074e30b97219da0547da841fc5121c90711c4eae7de54b964 |
| explore-03 | 22:04:02 | 0、新6件＋既存Media4/JMS reply5件PASS、新4class全coverage100%。BUG-061登録02efd4d後修正 | 8a8dcff387d905e035dd5e903ecbf3075f96428003f2bcb2f9d5298b045b7624 |
| explore-04 | 22:13:37 | 0、新6件＋関連9件PASS、新4class全coverage100%、Protocol/Storage/Web SpotBugs0 | d8eca705a0bc1b8c30d549547b3225bd55b6ea48ca293eb0474b0fbbcb3e00bc |

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=MqLoginClientTest,MediaResponseDecoderTest,JmsReplyDecoderTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report
```

explore01/02は上記からMediaResponseDecoderTest/JmsReplyDecoderTestを除いた新client探索。04は末尾に `com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check` を追加。未通過/修正前候補を合格へ算入しない。正式gateはclean verifyで累積coverageを消し、全既存PTを再試験する。失敗Web09 raw log hashは8caaec40bca2de4611fe60951d2ee47624c6ddc869502d9c527adac38ae391af。

## 独立期待・障害

要求640byteはUI232 offset0/8/11/19/22/23/24/60/96/113/177/181/187/193/199/208/212を手書き配置し、DATAはUI234の256/320/576/621境界。応答688byteはusername256、role320、context325、issued389、expiry406、retry423、remaining429、message432。expectedにproduction encoder/decoderを使用しない。固定JST日時からUTC期待を明示し、NFC文字とUTF8境界を固定文字列で検査する。合成秘密値の内容はsource fixtureのみで、wire/char/context/raw provider diagnosticはGit証跡へ出さない。

BUG-060は共通codecのerror fillerがUnsetなのにrequiredInt mapperへ渡した不備。0000/0200だけnamed mapper、0101/0106/9000は共通codecで全byte検証後に個別projection。非lock retry/remainingは規定の0であり、任意欠落を補完しない。Lock retry0/900正常、901拒否。Errorの認証context混入も拒否する。

BUG-061はUI234初回code一覧だけを採り、UI232共通0200とSS324 §6.1/SSC-013を取りこぼした不備。先行起票後、codeとoracleを正本へ訂正した。0200を保持し成功DATA/同一usernameを検査、欠落/別usernameを拒否する。Replyは認証grantではなく、元snapshotの現在context確認を後続provider gateとして残す。

## YKT-055 全対象の修正・非該当根拠

検索: `rg -n 'PayloadTypeCatalog.decode\(|LoginResponseData.from\(' src --glob '**/main/java/**/*.java'`。20 catalog呼出と直接named mapper/定義を照合。以下全既存callerを分類し、正式全module PTで非回帰する。

| 対象 | 判定・根拠・再発防止PT |
|---|---|
| MqLoginClient | BUG-060修正。PT055の3error×message境界、PT054/057成功・不正profileを追加 |
| MediaResponseDecoder（response/request） | responseはusesSuccessProfile guard後だけnamed、requestはfalse profile。MediaResponseDecoderTest正常0000/0200とerror/no descriptorを再試験 |
| LoginReplayService | 保存0000だけnamed、保存0101/0106は元errorを保持。Auth replay/inbox PTを全回帰 |
| LogoutReplayService | usesSuccessProfile内だけnamed、失敗別経路。Auth Logout replay/inbox PTを全回帰 |
| ScenarioReplayService | code SUCCESS時だけnamed、error descriptorなし。Scenario snapshot/replay PTを全回帰 |
| MediaReplayService（capture/reply） | 両経路ともcode SUCCESS guard。Media replay PTを全回帰 |
| UserMutationReplayService | usesSuccessProfile guard、error Optional.empty。Admin mutation replay PTを全回帰 |
| UserQueryReplayService/LogReplayService | code SUCCESS時だけvalidateResponse(named)。Admin query/Log replay PTを全回帰 |
| LoginInboxService/ScenarioRequest/MediaRequest/UserMutationRequest/UserQueryRequest/LogRequest | 個別request layout検査とfalse profile。error response mapperではない。各request/unknown layout PTを全回帰 |
| WebLogPayloadCodec/WebLogIngestService/OutboxJmsSender | WLGEVT01 eventまたはQWKREQ01 request、false profile。error response非該当。WebLog/outbox PTを全回帰 |
| PayloadTypeCatalog/LoginResponseData定義 | named成功契約を変更しない。共通error codecとnamed mapper各独立PTを全回帰 |

## YKT-056 全対象と後続gate

| 対象 | 修正・非該当根拠・試験 |
|---|---|
| MqLoginClient | 0200許可・usesSuccessProfile/同一username結合へ修正。PT054/057で独立0200正常/欠落/別userを追加 |
| MediaResponseDecoder | usesSuccessProfileで0200対応済み。med037の全3type/format0000/0200独立vectorとmed040並行を再試験 |
| JmsReplyDecoder | 個別code allowlistなし、共通headerのResultCodeを検査。既存validReplyProducesAnImmutableRedactedResultへ0200 byte保持の追加assert、全5件を再試験 |
| MqAuthenticationProvider（未実装） | Replyだけでsession/principalを発行しない。本clientにはHTTP/DB/Session依存なし。SS324 §6.1の現在context確認前の0200 grant禁止を後続実装gateへ残す。未実装対象を完了とはしない |

Web10時点でYKT-055は既存全対象の正式再試験後に完了、YKT-056はprovider残gateを含むため対応中。後続Web11/sourceb295b31でprovider/probe新8件と全692件を再試験しYKT-056を完了した。残対象の修正・独立再発防止PT・全API非回帰はprovider-exploration.mdを参照。

## BUG-062 静的解析とIP契約

正式Web09/source6c29119（22:06:18～22:10:44 JST）は全684試験PASS・全coverage100%だったが、Web SpotBugs RV_RETURN_VALUE_IGNORED 1件でexit1。不合格として保持し、collectorの合格結果へ入れない。修正前54d4e0a。ofLiteralを例外検査だけに使っていた。戻り値getHostAddressでscopeを検査し、PostgreSQL inetと既存LoginInboxService/LockedLoginAttemptのscope禁止へ合わせる。入力wireの正常IPv4/IPv6文字列は変えず、suppressionも追加しない。PT056にfe80::1%1/角括弧付きscope拒否を追加、PT054の圧縮IPv6期待値を維持する。

全production ofLiteral検索は4箇所。Web Loginだけ戻り値未使用。他のLoginInboxServiceはInetAddressを渡す前にscope拒否、LockedLoginAttemptはscope拒否後getHostAddress保存、WebLogIngestServiceはgetHostAddressをinet bindへ使用済みで同static rule非該当。今回の共通原因は未使用戻り値1箇所であり、YKT追加なし。全source静的解析と既存Login IP negativeを正式回帰する。

## 正式gate

正式PT-WEB-20260908-10、source208ba474ec6f79c68de1ac3c28a77cc0cb3c1b1c、22:14:01～22:18:27 JST、exit0。全684件（Protocol80/Storage34/API394/Web135/CHR41）、Web59件、新6件を含めfailed/error/skipped0。全5対象module line/method/class/branch各100%、NullAway/Enforcer/format PASS、SpotBugs0。全7collector/manifest/hashを更新。BUG-060～062とYKT-055の再試験完了。YKT-056/SSC-043のproviderは未実装で対応中、先行仕様6d68f35。API実dispatcher、JMS経由実認証、Spring provider/handler/session保存、現在context検証、画面、実NK CHR、IT/STの完了ではない。
