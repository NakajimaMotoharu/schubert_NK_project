# 原4040 trace・Web送信横展開PT仕様

## 原4040の実trace反映（PG6276）

1340/sourceb423の真正原4040/607・独立6274を前提にWBS metadataだけをstage/apply/report、全て0。stage SHA256 `48b7e71e46efcac3a9f60071dbf7075c85eedfd4aff4eb39b25dbc6e91545bc6`、apply `1f6fe97f7c86d266b2a4076e1ca5c179bb72c1b65f8ccce1ed5410f1d45c51d0`、公開PG6276-current943-trace-v1/manifest.json `b53cfee6f4c0b933886bb5b676a3d21a70d667926c282fe636ab79a0d2e2e43a`。metadata/private before-candidate/hash保持、485/486のexisting943だけを更新し、歴史941/17受入・481/484予算不変更、support追加0/fee0。

更新前auditは旧97dd candidate対新b423の既知STALEで1、更新後audit真正0。Java owner116はtechnical counter閉鎖91/未網羅24/別CHR1、正式/工数率へ変換しない。class-family line miss3562とmodule sourcefile line miss3554は集計domainの差として両方保持、0へ補正しない。新原全体を再実行せず、旧native/runtimeの成功を移植0。このstageはWBS JSON候補だけであり、配備place/stage/Unit操作ではない。

PMO-20261021-1003指摘に従いevent1528一件で1525/1526/1527のleaf参照を追記訂正。元event原行は不変更、1525は1524/K01.01＋既component、1526/1527は1519/F03＋P018-05/P005-03へ結合、各凍結群見積り・source/run/actual=null/既cursor/費用0/受入0を維持。返信待ちや試験再実行を作らない。

## 横展開発見・設計公開

YKT1323のAPI直接対象は当原51/4040で是正を確認したが、ArtemisRequestSenderのmanual closeとWebLogMessageSenderのTWRにmixed cleanup Errorの同種残存を見つけBUG1569、WLG TWRのsame Throwableによる元fatal置換をBUG1570/YKT1326へ**修正前**起票。直接JDBC setup原因BUG1567/YKT1324、工具1564/1321は当scopeだけ完了、BUG1566は当API修正再試験済・1323横展開未完を維持する。

SSC321のSS324/354と914（SSC320当API状態も含む）だけ3file/15insert1deleteを隔離treeから通常PR182へ反映。design source `698bf46b1d2fcf4b1d779938b53374529983180d`→main `e96d09f8a36fdec1bf17d9a17d6248c75a3b41d8`、2026-10-21T01:12:16Z merge、fetch確認済。CLEAN/必須check[]/reviewDecision空、match-head通常squash、admin/self承認/保護迂回0。実装/Test/工具/証跡をmainへ混ぜない。artifact添付は100上限で一回失敗、再送/既添付削除0。

## Program別独立PT（未実装・未実行）

|Program/owner|class/method|Test ID/目的|独立期待値|
|---|---|---|---|
|NK-MSG-001/P005-02|ArtemisRequestSender.send/closeAfterFailure|PT-IDEM-WEB321001：mixed fatal/元fatal/normal・same Throwable|固定RTE/Error/JMS marker、SS323 request byte golden。一回close、mode失敗はstage/commit/rollback0、checked stage failureは既rollback一回、cleanup Errorは元nonfatalより優先、primary Errorは元identity、sameはsuppressed0|
|NK-MSG-002/P006-04|WebLogMessageSender.send/owned close|PT-IDEM-WEB321002：normal/nonfatal/fatal×cleanup正常/RTE/Error|SS3232336byte WLG goldenとsynthetic keyの認証済input row。期待型/優先は固定table、異なる失敗だけsuppressed。正常wire/property/commitと全終了wipe、未取得close0/one-close|
|NK-MSG-002/P006-04|WebLogMessageSender.send/TWR失敗境界|PT-IDEM-WEB321003：body/close same Error及びsame RTE|同じ固定Throwableを二箇所で再送。元Error identity又は既typed failureの元cause identity、自己suppression0、mode失敗後stage/commit/rollback0、close1|

関連RD MQ004/005/006/008/MON003、UI212/231/242、SS321323324354/SSC321/411。Testは既ArtemisRequestSenderTest一method・WebLogMessageSenderTest二methodを追加予定、既全Test期待を維持。input作成の暗号化をexpectedの生成へ使わず、failure oracleは固定marker/型/回数/table、wireは独立Test golden。matrix入力をJUnit件数へ加算しない。新3はまだ宣言/成功ではない。

事前判定PT_DEFAULT：既承認の自己所有未接続JMS dynamic proxy・synthetic codec/key/wireだけ。実VM/current/Root/原本DB/failed-cohort/intent/permitへ接続しない。red限定は全Mainをb423に固定し、Test二pathだけを保存pushclean後に一回実行する。元whole/実trace済みを前提に新sourceを固定し、元赤の失敗/未到達入力を保存してから二Web MainのPG、同じ独立oracle greenと既real-broker/DB正常/duplicate graph関連PT、原artifact資格/型null/静的/実counter/必要同source品質へ進む。具体command/branch/対象commit/全input・期待/実際/coverage/BUG/SSC/hashは実施前後の新manifestへ固定する。実行不能/未実施を成功扱いしない。

PGPT元sourceはb423/当4040資格済、正式1964/53・17-190/全global100/F03/native/CHR/451/QA051final/PTALT不明/実環境HOLDは別未完。群1529 WEB_JMS_FATAL_ROLLOUT321は主P006-04、P005-02他component込み共通予算.5/2/6pp一回、追加発見/横展開手戻りと原計画完了を分ける。原/v4/1490/1520/群開始見積を減額変更せず、実N/T/専有費工数null、fresh共有used34/残66。通常小群/commit/レビューで停止しない。
