# Animation通信・保護read共通化単体テスト仕様書

NK-WEB-001/NK-MED-001、ProtectedReadWireClient/ProtectedReadWireException/AnimationWireClient/ScenarioWireClient adapter。FUN004/006/MQ/AUT/TST、UI232/234/235、SS311/312/321/322/323/352、PG206。正式22で8PT合格、実行詳細は019とmanifest参照。AnimationWireClientTestの以下8methodを一意対応。

| Test ID | method | 入力・操作・fixture | 独立期待値 |
|---|---|---|---|
| PT-WEB-238 | web238AnimationRequests | ANM、ANL MAIN/OVA、固定UUID/time/context | UI232 header＋UI235 data0/16の全byte一致、各1送信 |
| PT-WEB-239 | web239SuccessProfiles | ANM0/15/999相当、ANL0/1/50、0000/0200 | menu件数/flag、record title/category/parent/path/size順、型付き値 |
| PT-WEB-240 | web240ErrorProfiles | 全定義error、両layout | result code保持、payloadなし・error profile固定値、secretなし |
| PT-WEB-241 | web241MalformedReplies | layout/UUID/context/長さ/byte/field不正・不足/過長 | INVALID_RESPONSE、後続なし、pending0、buffer消去 |
| PT-WEB-242 | web242CapabilitiesAndNull | facade間layout混入/descriptor/records付き、null構成・入力 | INVALID_INPUT/no-send、明示null契約、Scenario元6要求だけ維持 |
| PT-WEB-243 | web243TransportFailures | JMS checked/runtime、timeout相当・不正clock/ID、未知障害 | UNAVAILABLE/no retry、未知は同一instance伝播、pending0 |
| PT-WEB-244 | web244ConcurrentRequests | 64actor×ANM/ANL、共有facade | UUID/context/応答分離、全件独立、再操作は新UUID |
| PT-WEB-245 | web245OwnershipAndDiagnostics | request/response array・record collection・exception/Result | caller値保持、owned buffer0、不変record list、固定redact/causeなし |

ExpectedはUI232/235 byte offsetとliteralから構築し、Production codecをfixture/expected生成へ呼ばない。Scenario既存PT-WEB166～173の全6独立golden・境界・例外/所有、SCR001～016/034～045の階層/検索HTTPを回帰する。ANL最大50/928byte、ANM16byte、error B=spaceを独立に守る。decode完了をAPI業務認証やJMS property guardの代替としない。

Java line/method/class/branch100%、NullAway/SpotBugs/Spotless。実行command/環境/対象commit/日時/exit/coverage/BUG/SSC/証跡path/hashは019結果/manifestへ保存。raw context/token/電文を保存せず公開集計だけ。実broker/Animation HTTP/動画配信/実NK Characterization・PGPT/IT/STは未完了。
