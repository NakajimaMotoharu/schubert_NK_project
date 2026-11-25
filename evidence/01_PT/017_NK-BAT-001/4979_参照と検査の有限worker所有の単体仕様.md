# 参照と検査の有限worker所有の単体仕様

NK-BAT-001、DAT-009、SS332／354、P004-02／03、F03、RRF-PURE-010、BUG-3842／YKT-2997。RunReferenceRepositoryとInspectionSummaryRepositoryのJDK代理試験で、元の32 task／10秒、親子の割込み／5秒の契約を維持する。追加試験は5秒と10秒を各独立に与え、各合成poolが停止一回、予定期限のawait一回を受け、falseを返す。一次例外は同じインスタンスで二次失敗は抑制配列に一件。元10＋13の各独立期待値も維持する。DB接続・実運用ファイル・サービスは使わない。
