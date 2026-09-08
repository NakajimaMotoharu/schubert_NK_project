# User照会request / snapshot 探索・障害監査

2026-09-08 JST、dev-admin。Java25.0.4、Maven3.9.12、既存隔離PostgreSQL18.6/Flyway、合成fixtureのみ。ProductionはUserQueryRequest/UserQueryReplayService、PT-ADM-040～047。探索は正式合格に加算せず、下記raw logは/tmpのみ、hashとsanitized分類を保存する。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,UserQueryRequestTest,UserQueryReplayServiceTest test org.jacoco:jacoco-maven-plugin:0.8.15:report`

| Run prefix PT-ADM-query-explore- | 結果 | 原因/対応 | raw SHA256 |
|---|---|---|---|
| 01 / 17:41:45 | exit1、API compile失敗、PT未実行 | BUG-050: Optional.map/orElseGetのnonnull generic推論。afb3b8eで先行起票、isPresent/get明示分岐へ。NULL LPの意味とProduction期待値は不変 | 426557684f62c67e97de24bcdd4af7a1d4211659bbe6d1ddc7b7299236be3e3d |
| 02 / 17:43:05 | exit1、8件中2failure、skip0 | BUG-051: 元と同じUSR recordCount1を「改変」とした入力、1800年を不正日時とするoracle誤り。fe7e398先行起票。別値2と差分assert、1800年正常、負年/5桁年拒否へ訂正 | 0f9106ec8e7d3d30c8542e40a2bf09a33016987bed8a4011d4cb94094d78f007 |
| 03 / 17:44:27 | exit0、8件全PASS | 新Production3classのline/method/class/branch100%、他moduleの探索coverageは累積で正式結果ではない | 6b52512e31a43c47fbcf30d228060a4204d1df32cc6d46bf88aa4bc0c8968b7e |

## YKT-045

探索04は新規negative fixtureのenum名誤記（ASYNCHRONOUS、実名ASYNC_ACCEPTANCE）でtestCompile失敗・未実行。Production不変更、初回test wiringとして訂正。17:46:22、raw hash249ddec1196e887da66b4374a17ecc47620573e6fc5ba44bd622dc35cf6fdb42。探索05は17:47:40、exit0、8件PASS、新3class全coverage100%、raw hashc9b243ed73af69893ea6a137a6e3d776de02f58c889342ae7a2cc4e684d77c5f。時刻/version/hashで前回query repository探索と区別する（旧sanitized履歴query-exploration.mdを保持）。以降探索run名はquery-request-replayを使用する。

全`src/*/src/main/java`の`orElseGet(`検索は修正前UserQueryRequest1箇所だけ。修正後0。CanonicalField optional mappingはScenarioRequest.textがisEmpty/明示return、MediaRequestは必須field、UserMutationRequestは必須fieldで同じgeneric chainなし。既存CanonicalField自身はnullable byte[]の入力/コピー/closeを明示し、NULLを空配列へ補完しない。全対象は静的解析の対象に残す。ADM040は3optional項目の欠落/存在全組合せをNULL長-1/独立JCE-HMACで比較、ADM043は100並行canonicalのclose後zeroと他buffer非破壊を確認。annotation/suppression/coverage除外なし。

## YKT-046

QueryReplayの全header改変に元bodyとの非同値assertを追加。recordCountはUSR元1/UDT元0に対して2となる。Kindはoffset22で実Q/Sを切替（version末尾21と区別）。MutationReplay ADM030のheader/target/version/reserved改変は全て元値と異なる（元recordCount0→1）、ADM031の日時はInstant.MIN/MAXで表現範囲外。共通JstWireTimestampは17 ASCII桁/strict calendarを要求し、1800年禁止は規定していない。FieldCodec/HeaderCodec既存日時試験を正式非回帰へ含める。QueryReplay ADM046に1800年正常wire比較と負年/5桁年拒否を残す。Production日時仕様・Current baselineは変更しない。

24h Inbox保持期限は本snapshot部品のcompletionではなく外側InboxRequest.expiresAtの責務。ADM044の範囲表記を明確化し、24h確認義務は次の照会application PTに残す。現在認証/ADMIN/Inbox/監査/実JMS/HTTP/起動/実NK CHRの完了を宣言しない。
