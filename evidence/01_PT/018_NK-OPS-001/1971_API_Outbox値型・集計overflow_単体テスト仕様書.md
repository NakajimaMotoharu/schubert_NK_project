# API Outbox値型・集計overflow単体テスト仕様

2026-10-25、群API_OUTBOX_VALUE_OVERFLOW_V1、原owner/cost WBS-P006-02、開始1/3/8pp/cap10/freshused11残89/reset1793513544。旧sourcefd3d04のBUG1760/YKT1511を修正前登録。仕様はRD MQ006/008/ASY001、UI242、SS324§8.3/331/332/SSC155。PG-D672。OutboxRetryScheduleの1/5/30秒/1/5分cap±10%はapplication send接続retry、QA050の別保守15分間隔やBroker redeliveryへ転用しない。

## 対象・独立期待値

既OutboxPolicyTest4・OutboxModelTest4・OutboxDlqMetadataTest2＝10method/3suiteを実source/hashで固定し、新OutboxDispatchReportBoundaryTest3（OVF001～003）を加える予定。対象MainはDestination/RetrySchedule/Entry/Request/DlqMetadata/DispatchReport/IntegrityException/SendExceptionの全8source unitと全nested class。DB/JMS sender/dispatcher本体は対象外。単体対象constructor/accessor/guard/redactionを省略しないが実測未網羅はそのまま残す。

| ID/対象 | fixture/入力/独立期待値 |
|---|---|
| PT-IDEM-009/010/011既8method | 二destination固定文字列、明示1/5/30/60/300秒と独立jitter下中上配列、attempt0/101・jitter±101・null拒否。Entry/Requestの固定UUID/Instant・byte1,2,3・全accessor・copy/redaction・N12/attempt/body/layout/version/lease nullと境界 |
| PT-QST-DLQ-MODEL既2method | 二つの固定架空UUID、明示UTC1～9999年microseconds/transport1～128ASCII/count>=1。DLQ profileの元messageとdispatch非同一・320byte/layout/version/metaありの固定条件、ASYNCはmetadataなし、外部exception/credential原本0 |
| PT-IDEM-REPORT-OVF001 | 新Testで0/0/0/0、MAX/MAX/0/0と各分割MAX一致を受理し全accessor固定値一致 |
| PT-IDEM-REPORT-OVF002 | 0/MAX/MAX/2、1/MAX/MAX/3及び内訳各位置の周回入力を拒否。和は2^32/2^32+1でclaimed0/1とは数学的に不一致。期待は固定literalでありproduction methodで生成しない |
| PT-IDEM-REPORT-OVF003 | 四count各負値、単独/複合不一致、long独立和の固定table比較。BigInteger/longの独立演算をgolden表の追加整合検査にのみ使い、production値からexpected生成しない |

## PG判断と実行前判定

コード点検でAPI reportはint和、Web同型は既long和＋claimed<=100である。既非負invariantの内部是正で上位仕様変更なし、QA/SSC不要。外部の許容count上限を推測で追加しない。BUG1760修正前の固定normal9694/API Jarに対し、所有した有限witness JVMで不整合受理を失敗1として保存する。新しいMain/Test修正はsource固定commit後、normal六moduleコンパイル/NullAway/lint、選択13PT/4suite、当session/CRC/全8unit counterと必要なMain/Test静的検査を当sourceで行う。全4222の確認再演や過去sourceの動的成功転用はしない。横断/正式451の必要全回帰は保留状態を維持し、小群成功だけで正式化しない。

PT_DEFAULT：constructor/pure enum/Duration/Instant/Optional/UUID/byte copy/明示合成例外とJUnitだけ。通信先なし、実DB/JMS/VM/Root/権限/外部file/鍵/permit/実停止/私有raw操作0。compile/JUnit/reportの自己所有new-only slotだけ書込み、旧source固定正常slotはread-only。Test3/Main8全sourceを読取確認済み、新Testは実行前に点検する。未知refusal/HOLDの再試行ではない。branch/lineの未到達は明示し0/0を合格へ加算0、独立postは実JUnitを再起動しない。正式1964-53/17-190/工数null/QA051final/全actualHOLDを保持し通常区切りで止まらない。
