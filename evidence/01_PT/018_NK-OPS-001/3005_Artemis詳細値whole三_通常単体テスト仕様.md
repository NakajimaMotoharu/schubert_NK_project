# Artemis 詳細値 whole三 通常単体テスト仕様

2026-10-31／PG-D961／群3355。主WBS-P017-10、元0.75/3/7共有pp cap10。保存HEAD4653330fc04a9d6c0e0e699ee6c8d37069f7d2dc/push37027真正0、Production6b53/normal14216固定。先行索引2299/1922と現registry15762を照合し、旧別source12136を現sourceへ転用・確認再演しない。

PT_DEFAULT：原ArtemisDetailedValuesTest全171行とMain StartupObservation/ManagementReadinessClient/QueuePressureClient/二例外を全文確認。元三Test全体を原sourceのまま新規自己所有JVMで一回実行。新fixture/保留Testからの抽出なし。Reader callback/Map/Numberと呼ばれればAssertionErrorのClientSession Proxyだけ。実ClientSession factory/start/query/close・親owner deadline・startup inspect/readEvidence・broker/Root/DB/鍵/credential/HTTP/VM/Graphを呼ばない。ThreadLocal Optional初期化はowner操作ではない。静的な型参照から実権限/実readyを推定しない。

関連RD MQ001002009010/SYS004、UI231251253、SS321§13/342§4、SSC130。Program/Sourceは上記三Main全体、closureは2+6+5=13physical（Code7/abstract interface6）を全分母に含める。Startup outer等が未ロードなら明示全covered0として分母維持、NoCode化/人工初期化しない。将来実broker・親/回収操作が必要な条件は既HOLDのまま。

Test IDは原三methodで一意：
- detailedNestedDataHasNoMutableInputOrOutputAliases：二段topology/settings/三段roles/pressureの入力map clear後、固定literal map/Valueが維持、返却map各階層clearはUnsupportedOperationException。
- brokerFieldsComeFromElevenReadsAndMutableDiskNumberIsCapturedOnce：独立固定11field・一意11read・可変NumberのdoubleValueは一回、0.125のIEEE754 hex 3fc0000000000000固定値、後の元map clearから独立、返却immutable。
- queueCountAndBytesAreNotLostAndRemainIndependentOfLaterFixtureChanges：六queue各count/bytesで一意12query、async count5200/bytes10=WARNING、後のfixture clearでも5200保持、不変map・count/bytes負数拒否・state null NPE契約。NPEをcatch正常化しない。

期待値は原明示literal/assertでMain methodから生成せず、SSの固定six queue/thresholdと既2299oracleを横断照合。immutable値に意味のない再送/並行操作を足さない。未網羅条件はcoverageに実missとして記録し100%に補完しない。

予定command：checked entry pg15772（新javac25 -proc:none -Xlint:all -Werror→元三JUnit/JaCoCo単独session）→15774受動fullSource/CRC/session/四held六native absence→15776独立oracle・metadata反例→current registry/WBSのsource/cases/cost不変検査。OS/JDK/command/開始終了/exit/XML/exec/input/source hashは各manifest、3006結果に実測だけ追記。静的14222/24は元同source証拠を参照、全F03受入とはしない。正式1964/53・17/190・工数null/QA051final/全HOLD不変。
