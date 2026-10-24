# Metric context metadata refresh／HTTP接続 単体テスト仕様

NK-OPS-001/RD171 MON010～013/UI252/SS311342351/PG-D620、group2053/主P018-09・C07追加費0。開始fresh44残56/reset1793382075、凍結3-6-10pp/cap10。既contextに非resource metadata Consumerを任意で保持するpublic三引数constructorを追加し、既constructorはOptional.emptyで互換維持する。private holderでnonnull consumerとstrong bindingを保持し、DEBUG＋presentのrenderだけprivate lock内で一回更新→stop再検査→既full payload、STD/従来constructorは未呼出。callbackはpre-owned非resourceのgetter/metadata更新だけ、I/O/接続/worker/資源取得・context再入を禁止する内部契約で、任意callbackへの絶対的security境界ではない。

Runtime/Errorは元identityで伝播、partial/ready-only成功fallbackなし・SDK/bindings保持、次renderはcaller明示だけ。refresh中close競合/再入は既unconfirmedで、callbackが帰還しても停止を再検査しdetailed成功を抑止する。source取得/全catalog・鮮度証明、manager/root实际assembly/停止budget成功をこのcallbackだけで認定しない。

|新Test ID（API/Web各role）|入力・操作/fixture|独立期待|
|---|---|---|
|MCTX027|default DEBUG/approved DB pool Gauge7.5、callback+2、二render|同一strong binding/一回ずつ・ready1→0/custom9.5→11.5固定literal/取得再試行0|
|MCTX028|STANDARD/setupとcallbackは呼ぶと失敗|両未読・ready固定byteのみ/空bindings|
|MCTX029|null Consumer|ctor拒否/登録callback0、NPE正常化0|
|MCTX030|最初だけrefresh Runtime|元identity/SDK未close/binding保持・明示次renderだけ成功7.5|
|MCTX031|最初だけrefresh Error|元Error/自動retry・fallback0/SDK保持|
|MCTX032|refreshから意図的close再入（negative）|既unconfirmed・stop通知後render成功0/SDK保全・最後のcaller cleanup|
|MCTX033|own finite latchでrefresh中に別thread close|即時unconfirmed/資源未close・callback帰還後renderはstop拒否・後で明示close。30秒上限worker/無sleep|
|MHTTP019|新refresh付きcontextを既HttpHandlerへ借用、二memory GET|ready一回ずつ1→0/approved値9.5→11.5が実HTTP本文へ、200/UTF8 byte長/二header/exchange close一回・context借用継続|

新MCTX027～033各7＋MHTTP019各1=新16。変更contextの既各26=52と影響HTTP consumerの既各18=36は必要回帰、actual104/4のうち新規化しない88。旧001～026/001～018本文の期待値を変更しない。fixtureはown official SDK、metadata array/固定literal、memory exchange、finite latch workerだけ。ActualDB/Hikari接続/JMS/VM/Root/defaultserver/ネットワークなし。期待はSS承認family/tag/手書き数値/ready/header/status/identityと独立byte長、production renderでexpectedを生成しない。

8806正常six（PT0）→8808 actual104/4→8810同source実Context二つ＋HTTP Handler二つのline/method/class/branch100、PMD/CS/SB/CRC/session/metadata negative→8812全1832/変更Context2以外旧1830同byte・元1667/二既manager不変/223owner/五edge・optional consumer/lock/stop/旧Test本文保持→1824/scan/push。Main変更2/Unit変更4/POM0、coverage除外/抑制/別source union0。範囲/実行command/時刻/tool/branch/対象commit/exit/coverage/BUG/各path/hashはmanifest/resultへ。着手時104 UNRUN、元4222確認再演0。manager動的/元F03 contract19 PTjoin/Root11・全451/CHR・正式1964/53/原190新受入0/工数null/QA051final/PTALT0/HOLDと原本/stash/元-v4-v5維持、通常継続。
