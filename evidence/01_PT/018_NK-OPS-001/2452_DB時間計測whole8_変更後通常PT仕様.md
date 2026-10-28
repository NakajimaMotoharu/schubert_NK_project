# 2452 DB時間計測whole8・変更後通常PT仕様

2026-10-29、WBS-P018-09/NK-OPS-001/RD171 MON006,010～013/UI252/SS332351/1714・1715/2451。Production a75a490666973b2d1fc9b4901290074aa1c32a0f、save13e9a8f1b2083e82b569ae19e44c46750adb9c1b/push44935真正0/origin一致。群DB_DURATION_EXISTING_WHOLE8_CURRENT_SOURCE_PT_V1、原低0.75/基準2/高4pp・cap10、専有費/N/Tnull/原v3-v4-v5不変更。結果2453/PG-D793。新製品機能や新Test IDではなく、2451で同値定数化した既Test sourceの必要な通常再資格である。

## 着手前の具体判定：PT_DEFAULT

対象はsrc既DbQueryDurationMetricCollectorTestの全8 method/1class、DBCONN001～008。選択wholeの全494行、Main Collector/Observation、Recorder/Query/Outcome、ExactDurationMeterRegistry/Supportの全bodyを確認。借用Functionの固定Observation、自己所有SimpleMeterRegistry・固定fake Clock、最大8自己所有Thread/有限latch/futureだけ。DB/SQL/driver/connection、HTTP/JMS、application main/Root、VM/service/配置、credential/key、TemporaryInfrastructureException/元failure graphの実行依存なし。名前にDBを含むがDB接続試験ではない。自己所有provider例外はidentity/部分counterを検査するだけでgraph walk/原cohortを呼ばない。元ApiObservationContext whole等のHOLDを分割・抽出したcaseではない。

13374は既scoped_prometheus_hostの固定SDK/clean ENV/新only SLOT・同source六Main JAR/公式JUnit/JaCoCo append=falseを使用し、既Test全class8を専用JUnit選択工具から起動。新製品fixture/入力や旧停止caseの移植はない。launcherは既ApiObservationContextJunitLauncherV2の同標準JUnit/XML回収構造をwhole8へ固定した工具で、Test bodyを複写・抽出・変更しない。無関係なsupporting Test実行0/EXTRA_TEST_SOURCES空、当既Testをfresh javacするだけ。全before/after source hashes、SDK/全dependency/工具、command/OS-JDK/選択全method/終了/8XML caseを保存し、失敗・abort・skip・欠落・重複を合格へ含めない。想定外失敗は先に915/916、同成功再演やflaky retryをしない。

## 独立期待値・範囲

1714各行が最正対応：001二Query×二Outcomeの0.5秒/呼出前0・identity、002missingとFAILURE1ns/真0、003元Runtime/Error/nullOptional/未正規化、004STD未read/nullとCONFIG_INVALID、005null/負-1/MIN/0/1/MAXとrecord五contract、006有限contender実BLOCKED/先行publication、007呼出前集計64入力・別owner、008partial factory/record後failureの元identity/borrowed close0。期待値をProduction mapperから生成せず、既固定literal・typed identity・呼出前整数集計/全assertを保持。equals(null)負oracleの目的2445も変更しない。

13376独立postで元8XML/終了・正確source/exec SHA/同一agent session/CRCと、当normal由来Collector＋Observation二物理の四counterをComponentCoverageAudit/公式JaCoCo0.8.15で測定する。constructor以外のgenerated recordメソッドは公式filter対象と区別し、DBCONN005のtyped accessor/equals/hashCode/toStringを実assertで別検証。除外を増やさず、二classだけの100%を全Main/全PGPTへ拡張しない。その他のactual module counterを合算しない。13362のNullAway/format-compileと13364/67の同source六Main静的証拠を参照し、静的207残を消さない。

製品source変更0、新Test ID0/原計画新受入0/正式1964-53・17-190・工数null/QA051finalは保持。新sourceの当8実行を旧146/18へ算術加算・旧coverage/native/正式へ移植しない。実scheduler/DB/時間測定/source真正性/外側期限/VM-native/CHR/451は未受入HOLD。原本DBBackup鍵/native/stash7/Scenario3/Currentbaseline/保留二工具/私有raw保全。fresh開始/終了はAPI直接487へ、現在残10以下又は枠不明で新規停止保全、次定期used15/通常群・commit・PMO待ちで止めない。
