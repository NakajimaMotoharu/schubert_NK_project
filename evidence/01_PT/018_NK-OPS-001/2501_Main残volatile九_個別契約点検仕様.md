# 2501 Main残volatile九 個別契約点検仕様

2026-10-29、PG-D816予定、START2880/開始0.5/2/4pp cap10/freshused27残73/reset1793774153。source17ab52b25/保存2523453f3e0cf3716d437f3cd26a2444fba4d081/push98027真正0/remote一致。主F03・canonical費P01806/P00604/P00502参照のみ/追加予算0。normal13596/静的13599同source参照、成功確認再演0。

## 読取範囲と個別判断

管理server303行/Runtime447行/Replay132行/ReplyConsumers190行の宣言・全対象field利用箇所とstart/health/ready/closeのguard/lock順を確認したsource契約レビュー。Main method/constructor/fixtureを呼ばず、実VM/HTTP/DB/broker/native/Root/鍵/Graph9/permit/私有rawログアクセス0。旧1822管理/1291workerの理由は関連参照で、当sourceのPT/XML/実競合成功へ輸入しない。

|ID/field|現在の必要性・限界|token出現数（コメント/string除外）|
|---|---|---:|
|07226 Management.started|stopLock内でserver.start正常後true、lock外promote/readyへpublication。closeのselector確認も同flagを使う。volatileだけでserver停止/複合readyの原子性を証明しない。|6|
|07249 Runtime.replies|ownerLock内でbind捕捉後start、health/closeは別経路でlocal snapshot。nullは未捕捉、volatileで後取得referenceの可視性を確保。|5|
|07250 Runtime.replay|ownerLock内のworker取得結果をhealth/closeへ公開。fieldをcompound counterへ利用しない。|4|
|07251 Runtime.retry|ownerLock内のretry worker取得結果をhealth/closeへ公開。actual worker終端は別契約。|4|
|07252 Runtime.http|owned callbackが部分ownerを先に捕捉、health/closeがlocal snapshotを読む。publicationsは一fieldごとで全graph atomicではない。|5|
|07253 Runtime.management|start前bind結果を捕捉、ready/closeはlocal snapshot。所有保持とactual socket/ready終端を混同しない。|5|
|07303 Replay.lastReport|単一workerがnonnull immutable四int Reportを置換、snapshot readerはjoinしない。volatilityはreference publicationだけでAtomicLong二counterとの同epochを約束しない。|3|
|07329 ReplyConsumers.stopping|stateLockで一度trueにしてcontext.closeへ、lock外readyが先に拒否。UNKNOWN closeの完了印ではない。|4|
|07330 ReplyConsumers.started|stateLock内のopened.start正常後true、lock外readyへ可視化。stopping/terminalとのtupleを線形化したとはしない。|3|

411 shared mutable state規則、SS342/343/351/352・UI243253/SS321、旧monitorを規約都合で書換えない。現在九件はfield reference/booleanの単純publicationで、++やread-modify-writeをvolatileへ依存させていない。安全なimmutable Report/適切なlock/atomic flagとの役割分担を記録し、未実行HOLDのactual競合や起動停止を静的レビューで代替しない。Main/Testの変更0・新動的PT/coverage0・新受入0。

13714はnormal13596全input/元13253の完全SHAと原catalog九ID、正しいPMD半開span、全field token位置/数・source guard・canonical owner/costを結合する。13716は別の公開XML/current source offset・token点から照合しtyped metadata反例を拒否。current source依存の個別review理由を機械的意味証明とせず、人（親）による可視性/反証の二視点を上記に残す。既先行理由と新sourceへの照合は新機能PGと数えない。

traceへ九ref追加時もraw6247/Main1491/Test4756/corr3194を保持、refs3358→3367/pending2497→2506/noRef2889→2880は実証前予定。995旧runtime/原941943/予算受入・正式1964-53/17-190/工数null/QA051final/全actualHOLD/二held工具/全保全物は変更しない。
