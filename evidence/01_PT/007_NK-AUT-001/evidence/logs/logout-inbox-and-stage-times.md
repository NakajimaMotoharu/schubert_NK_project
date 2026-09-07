# Logout Inbox・監査IP・時刻stageの単体試験

対象: SSC-015/016、PG-D-051/052、PT-AUT-LOGOUT-INBOX-001..006、PT-AUT-AUDIT-IP-001、PT-AUT-CLOCK-001/002。RD AUT-004/MQ-006..010/MON-004、UI226/232/234/241/242、SS314/324/332/351/354。

## 入力と独立期待値

隔離PostgreSQL18.6へAPI限定roleで合成User2件/session3件を作成する。Context lookupのSHA256はtest側JCAでASCIIを直接hashする。Session ciphertextは復号対象ではないstorage fixtureであり、Login AES試験と混同しない。Inbox snapshotは実AES-GCM/Deflaterを使用し、独立280byte literalを期待値とする。暗号自体の独立JCA vectorは既存codec PTで毎回非回帰する。HMACはtest側DataOutputStreamの固定LP owner7/LOGREQ01/001/REQUEST:LOGREQ01/field0からJCAで算出する。

| 観点 | 期待値と確認内容 |
|---|---|
| 原子性 | commit前別connectionはInbox0/revoked0/audit0、rollback0、commit後各1。追加session0 |
| 再送 | 同Messageの100並行は0000が1/0200が99、全DATA一致・新response ID一意、監査1。別Message既失効は元時刻0200と監査1追加 |
| owner/認証 | 同owner別contextで同Message再送は元操作結果だけ、別session失効0。別owner再使用は恒久拒否。Unknown0102/Inbox0、期限一致/過去/disabledの既知ownerはERROR/NONE、元0102を後から成功へ変えない |
| 保存検証 | 280byte、layout/version/相関、state/ref/AAD、owner/session存在/revoked/hash/元時刻、reserved/Numeric日時、未知key/改ざんを個別に検査。成功推測なし・9000型cause/suppressed0 |
| fault | owner/Inbox/session/監査/完了/restore SQL、required NULL、statement close、crypto/HMAC key閉鎖で全rollback。current/previous読取/current書込を確認 |
| 監査IP | Logout/管理ADMIN・DISABLED・PASSWORD_RESETで現在IPが無い場合はSQL NULL。Login時に記録したfixture IPやloopbackを代用しない。明示IPと既存Login/REPLACEDは正しい当該IPを維持 |
| 時刻 | 人工Clockで受信t→業務/監査t+1秒→Inbox完了t+2秒→header t+3秒。期限はt+2+7日、wire DATAは元業務時刻のmillis。再送headerだけt+4、DATA/DB期限/監査/照合不変。SQL日時とbyte fieldをliteralで独立比較 |
| null/境界 | 依存/公開引数null、owner範囲、別layout、autoCommit、閉connection、処理完了が受信より過去、不正failure codeを拒否し正常に算入しない |

## 実行・証跡

探索1回目は新規Logout6件/任意IP1件を含む347件、全coverage100%・SpotBugs0で成功（時計進行2件はまだ含まない）。正式証跡は時計進行を加えた`PT-AUT-20260908-13`のrun-summary/manifestを正とする。対象commit、実行日時、OS/JDK/Maven/DB/Artemis、終了code、JUnit method、全coverage counter、hashを固定する。成功前にSSCを完了にしない。

Raw電文/context/password/HMAC/key/DB dump/JVM properties/標準出力は保存しない。fixture再現source、sanitized JUnit XML、数値とmetadata/hashのみ。全layout dispatcher/実起動・Web/HTTP・Authentication CHR、OS process kill/rebootのIT/STは未完了。
