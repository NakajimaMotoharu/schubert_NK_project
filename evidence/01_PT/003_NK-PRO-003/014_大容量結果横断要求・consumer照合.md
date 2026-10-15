# 大容量結果横断要求・consumer照合（品質接続待ち）

2026-10-15、WBS-P003-01、Production a9/PG2802。009の全五path/unit契約とBUG1292のbeforeは変更しない。6bb4473fcで最大値oracleをTest-only是正、3346-after/63675 actual0は独立4800/10000/48000000の正常最大を維持し、同9999/47995200整合縮小shadowをAssertionFailedError由来で拒否、見逃し0。012/公開afterのsource/payload/log SHAを参照。Main/resource/settings変更0。個別NOT_ACCEPTED、必要whole/native/原XML witness接続まで先取りしない。

## 全要求と実consumerの独立oracle

| 要求 | Test ID・具体的独立期待値 | 全scopeでの位置付け |
|---|---|---|
| MQ037/038 | 同a9受入済P001/P002のUI全64 layout min/max/error・反復一領域/総byte。ScenarioDetailDeliveryTest R01は0/1/199/200 inline・1984+n*4800<1000000・file publisher0。R02は201/10000で一回publish、手組DATAのdescriptor全field・反復count0、元list不変。R03はnull/port故障/descriptor不一致でfallback0 | 本codecはSCN4800一種類のheaderless stream。全interfaceの上限/未知layout検査は共通codec主担当を参照し二重製造加点0 |
| MQ039/MSG-F04 | W05 ScenarioRecordStreamTestはUI234の独立4800byteをpreflight/partialwrite/forceへ照合、null/0/10001/不正末recordをIO前拒否。W07～10 ScenarioFileWriterTestは独立JCA/golden、JST日付、part→ready/no-replace/force/fsync、全衝突の元byte保全・所有partだけcleanup・不確定公開は保全・並行100件一意/会計。Web RD03は独立record値50000-index/sequence/index+1/本文/4800buffer/二pass、1/201/10000件まで immutable ordered値へ変換 | MQ応答はdescriptorのみ、file本体はlocal。Production encodeをexpected生成に使わず、各Testの手組offset/独立hashを確認 |
| MSG-F03 | D01/D02のUUID/JST日付/ready/ASCII相対path正規形に加え、LargeResultReaderTest RD05は借用root＋NOFOLLOW保持inode/read-only channel。通常file owner/group/mode/nlink/size、symlink/hardlink/missing/closed/wrongmode/hash/record/close faultを拒否、原file/metadata不変/借用root保持/所有FD全解放。100readerは別channelで独立位置・同readybyte不変 | P003-04保持能力の受入も参照。正規化startsWithだけを権限証明にしない、root repair/deleteなし |
| MQ040 | PT-JMS003のproduction broker templateは四delivery attempts、PT-JMS004 ArtemisFileJournalTestは実delivery count literal1,2,3,4・1/5/25秒backoff・第四rollback後DLQ/重複なし。SyncRequestListenerTest PT-JMS007は一時processor故障rollback→実delivery2、PT-JMS006/009は恒久不正type/versionを業務dispatch0でDLQ commit/元request ACK/秘密property除去 | codecが恒久protocol error/内部IOを区別するだけではbroker policy完了ではない。既実provider試験の原XMLへ接続、現在VM brokerの再起動は不要 |
| MQ041 | RD05の二回読取/100並行後もfile/metadata原byte保持・IO faultでも削除なし。TransferCleanupTest TRANSFER001～003は停止guard/保持root/所定cutoff前partとready削除・独立件数/byte・空日付dirだけ削除、boundary/future/不明名/link/悪mode/depth3は保全。Failure001は一unlink故障でも対象byte保持/WARNING・他対象継続。Scenario再送/再生成試験はCOMPLETED結果/寿命不変、missingだけ新規再生成・corruptionは再生成しない | ACK依存の削除機構を追加しない。単体consumer証拠を実朝batch全体/ITST完了へ拡大しない |

MSG-F01/F02（他owner P003-02への相互参照）はD01/D02と上記R02の独立DATAでlogical UUID/path、byte長、SHA64、record長4800、件数1～10000・byte式を照合する。binary mediaのMEDIA1024とSCNRSP01のfile descriptorを混同せず、上位wireを追加/改変しない。

当五pathの四実行family全method/全三criteriaは009/上記の範囲。package-infoはnull契約宣言で実行codeなし、coverage除外ではない。未知/既知IO・null・short/zero-read・終端過不足・32digest各位置bit変更は既L02/L03/H01、最大は是正後L01で検査。caller stream/channelを閉じず・immutable結果・独立parallel consumerの資源後条件を維持する。

3356は完了済み3350の原XMLをTest byte hash/sourceへ結ぶRO witness予定で、再実行/新件数加点0。全3704/別独立/同native28を確認後だけ品質補足と個別reviewを作成する。正式1964/53・工数null・QA051final保留・原/v3費用・全PGPT/ITST未完を維持する。
