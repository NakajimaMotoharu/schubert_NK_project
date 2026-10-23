# 1725 HTTP極小/MAX累積 追加品質単体テスト仕様書

NK-OPS-001/WBS-P018-09/C07/RD171 MON003/UI252/SS351§6・1573/PG-D575。前1724のHDR doubleとは別の整数ns Timer累積リスクを、HTTPREC010一つで検証する。Production Main/既九Test oracleを先に変更しない。元製造/190受入ではなく追加品質ID。

自己所有InspectingRegistry/MockClock・既固定/search, GET, 200へ、二順序[0,1ns,MAX,MAX,1ns]/[MAX,MAX,1ns,0,1ns]をfresh系列で供給。既recordは負のみ拒否しMAXを合法とする。独立期待=count5/request2xx counter5・sum1.8446744073709553E10秒/max9.223372036854776E9秒、SS351九有限bucket(.05/.1/.25/.5/1/1.5/2/2.5/5秒)のnsキー完全一致・各CDF3（0と二1ns）。境界をproduction getterからexpected生成しない。型付き固定BOUNDSは元SS literal。診断出力は当fixtureの三scalarのみ、実HTTP値/時刻/識別子/Throwable文面0。

source固定→正常六compile＋正規classpath/PT0→当Web78/10（新1＋必要既77）。新oracle失敗時は元source/runを保持して修正前915/916へ採番、期待値変更なし。四counter・CRC/一exec・SB/CS/PMD個別分類・全1791physical/138source・trace/metadata/公開scanを当sourceで照合する。新Mainを要するなら依存として明示追記し、開始見積を差替えない。code生成/真の空metadataの区分は既品質契約を保持する。failed/skipped/not-run/flakyを合格に含めない。

当群P01809_HTTP_DURATION_EXTREME_ORACLE_V1/event1950、開始0.5/2/5pp・上限10、PG8052fresh14残86/reset1793382075。receipt writer最初の括弧syntax errorはappend前停止、同fresh receiptを120秒内に正常登録し二重開始0。原/v4/v5・usage db7aa7c2/旧last27区間null/共有累積null/90再基底化0・N/T/専有費/工数nullを維持。全actualVM/DB/MQ/Root/native等HOLD、実HTTP・exporterを起動しない。正式1964/53・190新受入0/QA051final/PTALT0/whole451不変更、1726結果へ環境/command/exit/対象source・証跡hashを結合する。
