# Broker固定catalog・個別受入監査（当source全体終端待ち）

WBS-P005-01、NK-MSG-001、PGは既BrokerTopologyをレビューし実装変更不要。着手予算は481既値.1/.35/.8ppを固定し、全回帰K01.01へ重複計上しない。受入のための数字合わせや品質条件変更はしない。Source2e3cdb6ff6b0b7c3af0e33413affbda6fdbb2c3fの元4213は実行中。以下は個別の仕様/oracle点検であり、PT実行済みPASS/新全体coverage/ACCEPTEDではない。

## 対象scopeとPGレビュー

481のownedArtifactsはprotocol/transport/BrokerTopology.java一件、sharedClassReferences空、依存P002-03/C04。六enum定数の順序・全fieldはfinal、外部設定/producer/consumer/IOを持たない。constructor入力は固定六定義だけであり、runtime caller入力の妥当性と混同しない。requireAddressはnullの契約違反を即時拒否し、完全一致の閉集合のみ返す。未知値・末尾空白・queue名でAddressを代用することは不可。mutable state・transaction・並行worker・取得資源は無い。static final enum初期化/文字列の値検証以外に副作用なし。仕様変更/Main変更/新PTの起動は不要。

## SS321§4からの独立catalog oracle

| 定数 | Address | Queue | FQQN | body上限byte | TTL ms |
|---|---|---|---|---:|---:|
| SYNC_REQUEST | nk.sync.request | nk.sync.request.q | nk.sync.request::nk.sync.request.q | 1000000 | 5000 |
| SYNC_REPLY_WEB | nk.sync.reply.web | nk.sync.reply.web.q | nk.sync.reply.web::nk.sync.reply.web.q | 1000000 | 10000 |
| ASYNC_WORK | nk.async.work | nk.async.work.q | nk.async.work::nk.async.work.q | 1000 | 0 |
| WEB_LOG | nk.web.log | nk.web.log.q | nk.web.log::nk.web.log.q | 10000 | 0 |
| DEAD_LETTER | nk.dead.letter | nk.dead.letter.q | nk.dead.letter::nk.dead.letter.q | 1000000 | 0 |
| EXPIRY | nk.expiry | nk.expiry.q | nk.expiry::nk.expiry.q | 1000000 | 0 |

PT-JMS-002/005のBrokerTopologyTest.sixDestinationsMatchTheIndependentPhysicalAndLimitOracleは手書き六vectorをexpectedに使用し、expected由来addressからQueue/FQQNだけを組み立てる（production methodからexpected生成0）。enum個数/順序/全六field・TTL有無・各requireAddressを検査する。nullUnknownAndNearMatchAddressesAreDeniedはnull/queue名/末尾空白を拒否。loop六vectorをJUnit6件とは数えず二methodとして元XMLへjoinする。

## 要件の責務分担（全要求の単独充足と誤認しない）

RD131のMQ001はWeb/API Artemis、002は同期correlation、003は非同期永続Queue、004はWeb業務DB禁止とAPI context検証、005はAPI service振分け。catalogはこの通信構成の固定宛先・上限・TTL部分を担当し、requirement全体の実JMS/transaction/認可/dispatchまで単独で実装したとはしない。関連P005-02/03/04・P006/007の受入は別必要。SS321§4の六durable/ANYCAST/ACL実効設定は依存C04、本文layout/codecはP002-03へ参照し、ここへ実装費を重複計上しない。

## 個別criteriaと未完依存

| criterion | 現在確認した内容 | 未完 |
|---|---|---|
| P005-01:contract | 上記SS321六vector/二method/PG契約を目視照合。RD五IDのcatalog責務と他担当を明示。 | 当4213真正元XML二caseとsource/body/期待値hashのjoin。 |
| P005-01:scope | 481所有一Main/共有0とsource Testを照合。下位型は同enum、外部JMS/DBや資源ownerを内包しない。 | 485/current943・元Jarの当一physical所有照合。 |
| P005-01:quality | 旧全体counter・過去XMLだけでは認定しない。 | 当source実四counter/全関連PT0失敗/該当静的指摘・期待値/traceを元4213原資格へ結ぶ。 |
| 終了依存 | P002-03/C04はcanonical7fffの既受入であり、そのまま新2e3cの受入に流用しない。 | その二依存の個別criteria・当source/byte・current TestID/設定原文の再認証。historical17は保持。 |

現WBS正本のcheck_acceptanceはcanonical snapshot.sourceと各受入/依存/evidence.sourceの一致を要求する。current943のcounterを更新しただけではcanonical7fffの17件が新sourceへ受入更新されたことにならない。この制約を外したり、当候補を古いsourceへ偽装して一件加算しない。正式1964/53・canonical17/190・工数null不変。新sourceのcriteriaと終了依存が揃わない間はNOT_ACCEPTEDを維持し、何が確認できたかを本matrixへ追記する。

実Root/cohort/VM/鍵/原本/permit/ACL変更・service操作・拒否部分の追加調査/動的再試行は無し。F03のRoot11未分類/QA051final/PTALT未特定をcatalogの合格へ紛れ込ませず、独立性のある範囲だけ継続する。

### 再認証を反復しないための境界

既17件のcanonical所有artifactは187件、現sourceとのbyte差は41件（protocolのenum/codec等とstorageのownership/FD/ResourceScope等）。旧3916の独立Test source65file中、現sourceと異なるのはSyncRequestListenerTestとLinuxStartupAdmissionTestの二fileで、後者は既旧Testを保持した二method追加。したがって「現sourceの全体が成功した」というだけで17件を自動再受入することも、別sourceの旧nativeを継承することもしない。一方、一つの小群ごとに41件の意味差と全canonical設計を再レビューする無根拠な反復も避ける。当catalogはlocal契約/元二case/当四counter/所有scopeの監査証跡を保存し、終了依存は未受入のまま明示する。canonical受入sourceの切替は個別criteriaと全依存の再認証が揃う必要工程として一度に処理し、技術測定の更新と区別する。

## 当元4213からの監査結果

6906原監査manifest1e0b9289e61c97da663043dbb0999ed09491630e201ab97a010ebd49b454eb58、当元全体Q80ad328f/二caseのsource/body/XMLとMain hash・正の実四counter各100を照合。local所有scope/既独立六vectorと元二caseを結び、全要求behaviorをcatalog単独で満たしたとはしない。依存二件はrecorded7fff/required2e3cのためHOLD_CURRENT_CRITERIA_REVALIDATIONを明示し、acceptance=NOT_ACCEPTED/新leaf0。管理二0・工具pyflakes0、追加PT/実broker操作0。F03を迂回して受入数を増やさない。
