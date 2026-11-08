# 042 OwnedOutbox 正常EMPTY cycle 独立単体仕様

Program NK-MSG-002; class OwnedOutboxDispatcher 全9方法/1physical; Test PT-OWN-EMPTY001 / OwnedOutboxNormalCyclePortTest.ownEmpty001NormalEmptyClaimsCommitAndCloseBeforeOwnedStop。関連RD ASY001/MQ006、UI213/241、SS324§8/332§7.1、BUG2524/YKT2258。着手見積と費用は0183864/PG24270。原6のBUG2523是正後source0ddeは変更しない。

fixtureはConnection/PreparedStatement/ResultSetの宣言memory port・固定UTC2026-01-02T03:04:05.123456Zと空result。全cleanup callbackは無条件return、失敗注入なし。SQL条件のliteral断片はSS332のPENDING/ERROR、next期限、lease期限、order/skiplocked/limit/owner、boundUTC・10秒leaseから独立に作成。期待値はproductionから生成しない。claim二cycle以上を5秒以内に観測し、healthy true、finallyでownerstop・join後healthy false、二度close可、wake/start拒否、新open0、JMSopen0。全cycleでsetAutoCommit/get/prepare/bind1..5/query/nextfalse/resultclose/statementclose/commit/connectioncloseの正確順・各一回・rollback0を確認する。原六の正常/境界/null/例外/fatal/interrupt/selfjoin/並行と合わせ同source単execで全target L/M/C/B100を要求する。

実DB/JMS・SQLエンジンのlock/concurrency/crash/retry/権限・Root/nativeはHOLD、これを確認する代替fixtureではない。追加caseはownerと宣言JDBC portの通常empty契約のみ。元6のexec/coverageをmergeしない。Main7aed/22084・静的22086のbyte同一再利用。format24272/compile24274/static24276・preflight24278、固定sourceを通常push後24280 whole7、独立24282で原XML/FES/実終了/command/OS-JDK/currentCRC/held四初期化/全counterを照合する。native/CHR/全451/正式1964-53/個別leaf受入への転用0。Test一追加のunique更新は独立検証の真正成功後だけ。
