# Log要求・保存応答 部品探索（PT-ADM-061～066）

NK-ADM-001、FUN-008/AUT-003/MQ-006～010、UI235、SS323 §9.5/324/332/352、SSC-037/PG-D-091。環境は421および正式manifestのJava25/Maven/PG18 toolchain。raw logはローカル/tmpのみ、以下は秘密値を含まない要約とhash。正式clean verify以外はProgram合格へ算入しない。

| run suffix | 完了JST | 結果 | raw log SHA-256 |
|---|---|---|---|
| PT-ADM-log-request-replay-explore-01 | 2026-09-08 18:41:53 | LogRequest3件中2PASS/1failure、error/skip0。USER拒否の期待型を一般validationと誤指定。BUG-054/YKT-049を修正前88f879dへ起票 | 5ed8ebdef28fac9d8e2e22609850392fe4e9c66cc0135bcf3b1af669faedb583 |
| PT-ADM-log-request-replay-explore-02 | 2026-09-08 18:45:04 | 新規6件＋Log query6/User query7/User request4のAPI計23件PASS、failure/error/skip0。追加3class全line/method/class/branch100%（clean前の探索計測）、NullAway/format/compile合格 | 2e3f60eb4bd50b7cd6d1d8bc3fa61161d4a1df9ca3d44c1e4ccbb26092a8c933 |

commandは`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,LogRequestTest,LogReplayServiceTest,LogQueryRepositoryTest,UserQueryRepositoryTest,UserQueryRequestTest test org.jacoco:jacoco-maven-plugin:0.8.15:report`。01はLogRequestTestだけをAPI対象とした。初期test配線時に既存factory名/FingerprintKeyRing・FixedPayloadのrecordLength引数・AuthenticationContext Optional・InboxResultReference.numericをsource確認して実行前に接続した。Productionのpublic APIや既存codecは変更しない。

BUG-054はLogRequestTest062のUSER期待をAuthorizationExceptionへ変更し、FORBIDDEN(0103)/causeなしを追加。認可は既存AuthorizationService.requireAdmin契約どおりでありProduction不変更。

YKT-049対象を全query/requestのRole.USER/AuthorizationException検索で照合。LogQueryRepository058、UserQueryRepository004、UserQueryRequest042は既に認可型をassertしており非該当、02で再試験PASS。ScenarioRepository/MediaRepositoryおよび両RequestはUSERが正規の許可actorでADMIN専用ではないため同じ拒否期待を追加しない。これらの既存権限/owner負例は正式全reactorで再試験する。Replayはcurrent認証ではなく部品invariant違反を固定Temporaryへ変換する別契約で、ADM065のUSER/owner/scope負例が確認する。HTTP0103変換/外側applicationは後続PT対象のまま残す。

独立oracle: UI235の656byte要求・256byte header/48byte頁/2088byte recordをtest側固定offsetで作成し、production codecからexpectedを生成しない。NKOP1は手組LP/UTC-T1とJCE-HMAC、保存暗号は手組AAD/JCE-AES-GCM/Deflaterで独立検算。synthetic固定key/nonceはtest vectorだけ。0/1/100 record・全optional・9001 filler・暗号として有効な不正電文・100並行を確認。検索原値とtrim後SQL値を区別し、欠落はNULL LP。header ID/context/timeはHMAC対象外で、再送headerだけ現在値へ更新する。

正式対象commit/時刻/OS/JDK/command/終了code/全coverage/静的解析/Test ID/hashはmanifestへ確定する。BUG054/YKT049/SSC037の完了は正式gate確認後。Log外側認証/Inbox24h/監査/JMS、Web/起動/実NK Characterization、IT/STは本探索では完了していない。
