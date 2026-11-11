# Login純交換・有限所有と未知例外の通常PT

Program NK-MSG-001／NK-WEB-001、MqLoginClient.exchange／Reply、MqLoginExchangeExceptionおよび純Client/Registry。FUN-001/AUT-001..004/MQ-004、UI226/232/234、SS312/314/321..323/352、411/451。BUG-2664/YKT-2344（global2177未完）。Mainは236ffddc83から変更しない。

| Test ID | class/method・事前条件 | 入力・操作 | 独立期待値 |
|---|---|---|---|
| PT-WEB-054..059 原6 | MqLoginClientTest全原method、固定Clock/UUID・synthetic sender | manual640/688byte要求応答・正常/NFC/boundary/null/空/不正wire/timeout/並行100 | UI232 literal offset、JST固定文字列とUTC時刻、型別固定例外、password/送信buffer消去、pending0。既存assertを保持。 |
| PT-WEB-LOGIN-UNKNOWN-001 新1 | unknownProviderFailureErasesBothBuffersAndReleasesCapacity、容量1の自己所有client | synthetic senderがNPE／AssertionErrorを送出。各失敗の後にfresh UUIDで正常交換 | 元の同一exception instance、caller char配列0・sender clone640byte0、送信1/pending0。続く別UUIDの正常USER応答・caller/sender両buffer0・累計送信2/pending0。expectedはproductionから生成しない。 |
| 原6中worker二箇所 | web058 virtual／web059 fixed8 | 元のFuture/latch操作を保持 | finally shutdownNow、awaitTermination5秒をassert。無期限closeを使わず、正常/失敗時とも有限の資源後条件。 |
| 必要共有147 | Client10/Registry7/Protocol130の全class | 今回Loginの同閉包に必要な同run再資格 | 旧exec合算なし、独立golden・原fixtureを保持。定義追加や元190受入へ数えない。 |

合計154件・新定義1。全188physicalを入力に保持し、line/method/class/branchを独立postで確認する。自然Code不在と標準switchmapを区別し、手動除外しない。全12physicalはnormalと完全byte一致、現限定Maven compileのJava25/ErrorProne/NullAway0、SpotBugs全12/missing/error0。PMD raw15は個別文脈非該当（standalone所有workerの有限finally／元fixture専有monitor）、適用違反・未分類・CS0。Root/held四・実認証・HTTP/session・DB・鍵・VM/native・broker接続は行わない。IPはofLiteralのみでDNS照会しない。全入力はsyntheticで実credentialを保存しない。

製造前26518／製造26522（原6逆変換一致）、compile26524／static26526／preflight26528。実行commandは `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1256_login_normal_qualifier.py run <固定commit>`。予定run PG26530／独立PG26532。日時・OS/JDK・branch/source・実command/exit・入力/期待/実際・XML/CRC/coverage/hash・BUG/YKTをmanifestへ記録する。作成時green未実行・coverage未確定。原P00502全owner／C04／全451・正式1964/53は未完のまま。
