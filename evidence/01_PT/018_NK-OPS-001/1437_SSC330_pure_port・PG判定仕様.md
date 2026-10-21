# SSC330 pure graph/secondary ports and PG oracle

1436のMain8d77からTest-only source964ba455a6c9d87ffcf38f9862bce79d26d6f0a4へ固定。API元97453/6562、Web元66432/6564を独立snapshot/targetで開始（同archivef8081c2418ec7e184c6915bc598de48a19a1771ba124a9eea9bb53fc041d8ccb、UTC15:49:26.877192/15:49:28.855337）。双方の真正終端/原照合前にMain/Test変更0。並行は同一readiness群の独立fixture/出力であり別WIP経路・外部job起動ではない。

## pure portの独立期待（実装前）

新ApiStartupGraph330Test/WebStartupGraph330Test各3method、PT-API-STARTUP-GRAPH330001..003/PT-WEB-STARTUP-GRAPH330001..003。PT_DEFAULT、自己所有Throwable/SQLException/JMSExceptionだけ、非I/O。API TemporaryInfrastructureException/Web WebStartupExceptionのmodule-local portに対応する。

1. 001：JMS linked→SQL.next→causeの元Error。JMS linked/cause/suppressed/SQLnextの混合循環/重複は有限、後からfatalを入れたら同じError、graphのcause/linked/next自体を書換えない。JMS linked null/SQL next null/未知非fatalも有限帰還。
2. 002：直接Errorを先行し、通常rootのcause→suppressed→JMS linked→SQLnext FIFO順を固定。nullはNPE契約違反。新catalogはAPI literal `request transaction is unavailable`、Web fixture component `PUBLIC`でliteral `PUBLIC is unavailable`、cause null/suppressed0。既Authのsuppressed優先は無変更。
3. 003：attachSecondaryは両引数nullをNPE、同一Throwableはsuppressed0、別Throwableだけ原objectを一時attachする。suppression無効の自己所有RuntimeException/Error subclassではgraph連結ができないことを確認し、primary graph優先→secondary graphの順で元Errorを保持する。両方非fatalなら正常returnし、provider graphをcatalogへ保持しない。入力失敗のsource graphとcatalogは別object。

PGは四Mainのみ。API共通分類にJMS linked追加、WebStartupExceptionに同等のpure port、両readinessで既直接fatal優先を決めた後に捨てた非Error secondaryを一時attachし、最終固定catalog前に分類する。owned close回数/consumer/Queue/DB/Unit/権限/元診断・既優先不変更。API/Web間又はprotocol/bootstrapへ新JMS依存を追加しない。attachment中fatalでもcallerのfinally/TWRが残るcloseを完了する契約、将来のAPI transaction再利用は別scope/同source品質で確認し、この4Mainだけで当再利用を実証したとしない。

PG後も1436の二Test SHAを固定、新pure6methodを加えgreen24/11（baseline12/7＋readiness6/2＋pure6/2）で三phase/六gate0を確認し、6568原8511667/Jar/XML/static/実counterを照合する。新pure methodの未実装compileを旧赤へ算入0。個別selected四100/各domain/必要全体/F03/正式・実Root/nativeは原結果で確認するまで未受入。原-v4/正式1964-53/17-190/工数null/QA051final/PTALT代替0/全HOLD不変。
