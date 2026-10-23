# 1725 HTTP極小/MAX累積 追加品質単体テスト仕様書

## BUG1681是正補足（開始見積・元010本文不変更）

元7e57/8056は78/10中010一件failure、実測count5/sumSeconds0/maxSeconds9.223372036854776E9。第一順序のsum assertで失敗、第二順序とbucketは未到達。8054正常六compile0/PT0は別保持。BUG1681/YKT1432を修正前起票。

専用final OverflowSafeHttpMeterRegistry＋空capability＋AbstractTimer subclassで、SDK整数bucket/単位/wrapper/時間窓maxを維持し累積totalのみDoubleAdderとする。STANDARDは汎用registry、DEBUGは精度capability必要。他名Timerは元SDKへ委譲。HttpMetricRecorder/Valveの二fixtureを共通factory/固定MockClockへ接続する。既Main一変更、既Test二変更・新Main二file(実registry/inner＋empty interface)/新Test一file、当23Java/実20＋metadata2/physical22・全1794/141delta-125physical予定。

HTTPDUR001..012を12追加し、当Web90/11（追加品質13＋必要既77）で検証する。001九境界各±1ns/equalの27literal、count27/sum38.7/max5.000000001/CDF2,5,..26。002全七TimeUnitへ各1入力、独立sum90061001001001ns/90061.001001001秒/max86400秒。003元010の二極端順序と固定sum/max/CDF3。004 snapshot/mean/measurement count2,total2.5秒,max1.5秒,mean1.25秒。005 1秒expiry×buffer2、固定clockを3秒進めmax0でもcount2/total2.5維持。006 nullClock拒否/未知registryDEBUG拒否・STANDARD許可/既定構築。007 histogram/client percentile/境界不整合factory拒否。008四worker各64×1秒、count/sum256/max1と九CDF・別owner0、全future期限内。009 SDK Runnable/Callable/Supplierの固定1/2/3秒、checked exceptionの固定4秒も同一例外とcount4/sum10/max4。010 他名Timer3秒/Counter7の元SDK動作。011 補助gauge factory例外identity/非close/登録なし。012 nullUnitはNPE伝播、SDK negativeは非観測・合法0はcount1/CDF全1。NPEをcatchして正常化しない。

数値は上記literal/SS bucket・固定clockの独立算術で算出し、production methodでexpectedを生成しない。空markerは命令0を非初期化metadata検査し全physicalへ残す。未実行/未到達・不合格を合格へ加算せず、source固定後に同sourceの四counter/CRC/static/全物理/全owner traceと旧010oracle不変更を確認する。実HTTP/clock/VM/DB/Root等HOLDは不変更。

NK-OPS-001/WBS-P018-09/C07/RD171 MON003/UI252/SS351§6・1573/PG-D575。前1724のHDR doubleとは別の整数ns Timer累積リスクを、HTTPREC010一つで検証する。Production Main/既九Test oracleを先に変更しない。元製造/190受入ではなく追加品質ID。

自己所有InspectingRegistry/MockClock・既固定/search, GET, 200へ、二順序[0,1ns,MAX,MAX,1ns]/[MAX,MAX,1ns,0,1ns]をfresh系列で供給。既recordは負のみ拒否しMAXを合法とする。独立期待=count5/request2xx counter5・sum1.8446744073709553E10秒/max9.223372036854776E9秒、SS351九有限bucket(.05/.1/.25/.5/1/1.5/2/2.5/5秒)のnsキー完全一致・各CDF3（0と二1ns）。境界をproduction getterからexpected生成しない。型付き固定BOUNDSは元SS literal。診断出力は当fixtureの三scalarのみ、実HTTP値/時刻/識別子/Throwable文面0。

source固定→正常六compile＋正規classpath/PT0→当Web78/10（新1＋必要既77）。新oracle失敗時は元source/runを保持して修正前915/916へ採番、期待値変更なし。四counter・CRC/一exec・SB/CS/PMD個別分類・全1791physical/138source・trace/metadata/公開scanを当sourceで照合する。新Mainを要するなら依存として明示追記し、開始見積を差替えない。code生成/真の空metadataの区分は既品質契約を保持する。failed/skipped/not-run/flakyを合格に含めない。

当群P01809_HTTP_DURATION_EXTREME_ORACLE_V1/event1950、開始0.5/2/5pp・上限10、PG8052fresh14残86/reset1793382075。receipt writer最初の括弧syntax errorはappend前停止、同fresh receiptを120秒内に正常登録し二重開始0。原/v4/v5・usage db7aa7c2/旧last27区間null/共有累積null/90再基底化0・N/T/専有費/工数nullを維持。全actualVM/DB/MQ/Root/native等HOLD、実HTTP・exporterを起動しない。正式1964/53・190新受入0/QA051final/PTALT0/whole451不変更、1726結果へ環境/command/exit/対象source・証跡hashを結合する。
