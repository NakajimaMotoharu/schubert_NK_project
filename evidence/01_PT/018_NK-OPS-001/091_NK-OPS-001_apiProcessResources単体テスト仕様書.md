# API process Resource単体テスト仕様書（PG288）

Program NK-OPS-001、ApiProcessResources constructor/execute/withDatabase/default factories。RD SYS002/004、DAT001、OPS009、UI212/243/253、SS311/342/343、SSC081/082/084。471 D01/02/05の取得・所有・終了条件であり、D03/04を満たす完全起動ではない。

fixture: 既存隔離PG18＋全Flyway、公開合成5材料と実一時file/channel、Linux保持directory。credential UID/ACL/readonlyは既存TestIo/TestSecurityによる明示的合成metadataで、OS配布の証明ではない。PG認証はtrust fixtureでSCRAM未検証。本番のtrustは禁止のまま。期待値はSS固定role、pool8/min2、材料kind/長さ、close後条件とarray全zeroから独立算出する。productionでexpectedを生成しない。

| Test ID | 操作・事前条件 | 独立期待値 |
|---|---|---|
| PT-OPS-API-RES-001 | 5材料取得→既定source/pool→実SQL、正常終了 | current_user=schubert_app、pool8/min2、1row、callback中だけ借用可能。pool closed、材料copy禁止、read buffer全zero、外側の試験所有rootは生存 |
| PT-OPS-API-RES-002 | callback IO/Runtime/Error×pool close正常/Runtime/Error/同一例外 | 正常returnなし。既知body＋未知closeは未知close優先、未知bodyはidentity維持・固定secondary。pool/source/material解放、close1回、秘密診断なし |
| PT-OPS-API-RES-003 | source/pool factoryのthrow/nullで部分取得停止 | callback0。渡したpassword copyは失敗でも全zero、取得したsourceはclosed、材料/read buffer消去 |
| PT-OPS-API-RES-004 | 必須mq-api欠落、LFのみ不正、root UID不正 | source/pool作成0、callback0、固定拒否。部分読取buffer全zero |
| PT-OPS-API-RES-005 | 全constructor依存/null operation、native temp FSの不適合 | null境界NPE。非適合OS metadataは起動拒否し、合成PTと実OSを混同しない |
| PT-OPS-API-RES-006 | 4worker/8独立scope、同一公開fixture | 10秒内に全成功、各scope独立取得/解放、実SQL role一致、全read buffer消去 |

実行command/環境/source/hash、coverage、結果、関連障害は092とprovisional manifestへ保存。固定監査情報以外のpassword/key/session/token/raw DB/logを証跡に保存しない。範囲内の正常・異常・null・並行・取得途中例外を対象とし、HTTP/JMS再送やroot管理側の受入を合格扱いにしない。
