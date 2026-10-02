# Web全業務固定通信単体テスト仕様書

2026-10-03、Program NK-WEB-002。PG-D-342、S3/D05の全業務assemblyに必要な通信port。実装と並行したhost PTでありHTTP/native起動を代用しない。

対象: `QuestionWireClient`、`NotificationWireClient`、`UserAdministrationWireClient`、`LogoutWireClient`、`MediaDescriptorWireClient`のconstructor/exchange、既存`ProtectedReadWireClient.exchange`。RD FUN-005～011/AUT/MQ/QST/NTF、UI232～236、SS311/313/314/321/322/323/324/333/352。既存Scenario/Music/Animation/Log wire suiteを回帰対象とする。

| Test ID | 目的・fixture/操作 | 独立期待値・根拠 |
|---|---|---|
| PT-WEB-S3WIRE001 | 18固定requestを個々facadeからsend、9000 response | UI232 header絶対offsetとUI234～236 dataの1-based offsetを手書き配列へ転記。clock固定UTC/µs→JST/millis、QSBだけA/他S、全byte・reserved・UUID/context一致。Production codecでexpectedを生成しない |
| 002 | QSB/QDL/NTC/User5/Logoutの0000/0200 | UI236 receipt26/N12/時刻、User ID/version、CANCELLED/取消時刻、UI234失効時刻の手golden→型/値照合。payload秘密を表示しない |
| 003 | 全18×他4facadeのcapability誤用 | 全72入力をsend前INVALID_INPUT、HTTP選択layout能力なし |
| 004 | 5constructor各null依存、0/負/2秒超、input/context null | invariant拒否・送信0、NPEを正常扱いしない |
| 005 | A→S、response kind、correlation/context/length/receipt/予約byte変異 | 正常request後INVALID_RESPONSE、pending0・send buffer全0。別layout responseも拒否 |
| 006 | 18layoutの0100/0102/0103/0104/0105/9000/9001、timeout/JMS/未知Error | error fillerからsuccess payloadを得ない、1送信のみ・再送なし、未知Error同一性・正常化なし、pending/byte後条件 |
| 007 | 同QSB tokenを3回、新Messageごとに0200 | UUID3 distinct、本文/tokenは同じUI golden、transportが自動再送しない |
| 008 | 8thread/180独立requestとcontext | 全18種×10、full wire一致・独立180UUID、相関混線0、全byte消去/pending0 |

実行環境は既存JDK25.0.4/Maven3.9.12/Node24.19.0、依存reactorを含む6moduleで新suiteと既存関連suiteを選択する。strict compile/NullAway/Spotless/SpotBugs6、JaCoCo4counterを併記。source固定前はWIP限定結果、Source固定後全回帰と全scope/native/CHRは後続。Failed/skipped/not-runを加算せず、現在正式run24を更新しない。DB/crypto/HTTP/Media配信/owner/role判定はこのspecの対象外ではなく未接続後続受入として460で追跡する。

実command、時刻、commit/dirty、終了code、独立fixture hash、結果/coverage/BUGとsanitized manifestは050実行結果へ保存する。fixtureは合成値のみで実credential/session/token/password/key/原本dumpはGitへ格納しない。
