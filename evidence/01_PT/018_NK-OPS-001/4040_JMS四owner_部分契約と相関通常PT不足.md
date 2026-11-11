# JMS四owner 部分契約と相関通常PT不足

WBS-P00501/2、P00502..04/1..2、SS312/321、UI231、MQ004/005。PG26408 SHA `5420264af83e1a3b18a8c622a3e5326bc5aafc6ebcc7eef9f9cfe9da6d96ba23`。45owned sourceのcurrent Main8b/normal byteは照合済みであり、全文method確認はBrokerTopology/Registry/Pendingの3 sourceだけ。他42は未確認を維持する。

CatalogのSS321六物理宛先/queue/FQQN/limit/TTLは独立literalに一致、同source PG26310全130の既存二TestとPG26312独立XML/counterへ結合しL25/M9/C1/B6全miss0、試験再演0。ただし実broker C04終了依存未受入のためP00501/2はNOT_ACCEPTED、既/1を繰り返さない。全owner受入やArtemisの実role/schema成功を主張しない。

Registryは最大20/capacity、register先行・UUID一意、now<deadlineのみ成功、inclusive deadlineはlate、cancel/expire/completeの単一terminalとpermit一回返却、CompletionStage各呼出しbodycopyが契約。原全5Testの一ownerにTWR ExecutorService.close無期限を発見しBUG2656/YKT2336へPG26410で修正前保全。元5断言/100応答1winnerは保持、finite finally5と全6終端順列・返却futureの操作非波及/nullを新二Testで補う見積.2/.5/1cap2を着手前に凍結。

actual broker/JMS送受信/DB/API暗号/credential/Root/native/VM/held四byteは扱わない。純二Mainを明示compileしJDK/JUnit閉包のみで、実webJarやそのheld例外を実行経路へ載せない。無関係な拒否PTの再試行・安全条件変更ではなく、別の相関値管理通常経路だけ。actual原processや成功証跡・原本DB/Backup/stashを不変更。

今回製品PT0/新定義0/新coverage0、元価格.913/2.373/4.745全保持、正式1964/53・元190新0・工数率null。後続PTは4041の新仕様へ別記し、この部分記録を全検証済としない。
