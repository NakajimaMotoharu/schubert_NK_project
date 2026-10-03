# 077 NK-WEB-002 Logout継続再送単体テスト仕様書

未実装・未実行。S3/D05の既存全Web起動経路に必要なQA050依存。RD AUT004/MQ/MON004、UI226232234242、SS314§10/QA050補足・331§9.2/332/343/352/354、QA050/SSC171、API前提007031032/BUG618/YKT437。最新source/processは456を正とし、API固定fullの終了/capture前にProduction sourceを変更しない。

対象予定：末尾V027（既存V001..026不変更、pending expires_at NNだけ解除）、revoke専用NKENC1 codec/row identity/payload、pending repository/claim・retry service、local Logout coordinator/HTTP、既存WebNativeCodecs/runtime ownerへの接続。既存SessionPayloadCodec・WebLogOutboxRepositoryをpurpose違いのまま流用せず、既存JmsRequestReplyClient/LogoutWireClient・JdbcWebSessionStore/EncryptedWebSessionRepositoryを必要な境界に接続する。内部名・補足確定は441/431へ記録する。

| Test ID | 目的・fixture/入力/操作 | 独立期待値・根拠 |
|---|---|---|
| RERUN002 | V027適用前後、隔離PG各role/既存row/index/constraint/hash | 新NULL期限insert可、既存値/lease/index/grant不変。requested<known expiry/time order・attempt0..100・cipher/key/leasepair制約維持。NULL/期限経過を削除proofへ使わない。SQL catalogとV001..026の独立SHA |
| RERUN003 | 専用revoke256bit current/previous、固定nonce/context64ASCII/row UUID・日時、改竄/別table/別PK/別format/鍵version | NKENC1 envelopeとlength-prefix AADは独立DataOutputStream/JCAで算出、production methodからexpected生成しない。別purpose/session ciphertext拒否、未知鍵/破損で別context捏造0、ownedcopy・一時plaintext消去/redacted表示。鍵はpublic test-only vector、実秘密をevidenceへ保存0 |
| RERUN004 | enqueue/claim/failure/confirmed delete、NULL・過去/未来期限、due境界、100/101、実SKIP LOCKED・2worker/lease競合 | 短TX・最大100/一意lease CAS、commit-close完了後にだけremote。expiryをclaim除外/cleanup/delete理由にしない。5秒/30秒/5分→以後900秒、100飽和後もretry。一般0102/未知/復号不能はrow保持＋fixed error、他lease上書き/削除0 |
| RERUN005 | genuine LOGREQ256/LOGRSP280、freshMessage/元context、0000/0200/0102/error/timeout/false reply、同Message再利用負例 | 独立UI232234 goldenと現在API SQL。検証済0000/0200のみ自lease row削除、一般0102/期限不明/expired/undecryptable保持。JMS待機中active DB connection0、100競合でremote重複claim0/stalelease CAS0 |
| RERUN006 | 現localsession Logout/CSRF・queue登録+localrow削除、enqueue/commit/close failure・応答喪失・停止 | 登録/row破棄は既存短TXへ原子的接続、失敗時も独立local破棄試行。DB破棄/永続retry未成立をLogout成功表示にしない（既定503）。Cookie/local context再利用0/raw記録0。HTTP drain→retry join→replies→outer DB/JMS/key逆順、元Unit期限内/owner保持 |
| RERUN007 | 残row/借用中の旧key・current入替・close/復号不能 | row又はborrower>0なら必要旧keyを保持し、0になるまで削除不可。以前のversionを読めない場合保持/警告、偽失効proof/秘密log0。native credential/保持資源は同sourceの実起動で別途確認 |

正常/境界/異常/例外/null/collection未知値/並行/再送、JDBC取得/statement/row/commit/rollback/close未知とfatalを含める。constructor/factory invariantとnull/static gate、全対象line/method/class/branch100、独立SQL/HTTP/byte/JCAを必要とする。TDD初回未実装失敗はBUGにしないが、実装済み仕様違反は修正前915/必要916へ起票する。

実行command・OS/JDK/tool/source/branch・日時・終了code・XML・coverage・BUG/SSC・入力expectedactual/hashは078とsanitized manifestへ保存する。選択検証→同所有/DDL/security群source固定fresh全6→native全WebとCHR/native coverage/正式scopeへ進み、skipped/failed/別source/未実行を合格へ算入しない。IT/ST混在/性能・間隔調整は後続Linux工程、ここで合格宣言しない。
