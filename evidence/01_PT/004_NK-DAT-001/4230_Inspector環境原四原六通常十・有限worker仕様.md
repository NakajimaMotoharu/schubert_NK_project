# Inspector環境原四・原六通常十：有限worker仕様

対象P00404 InspectorRunEnvironment/InspectorStaticEnvironment全source、関連P01702 BatchRun。OPS009/UI251/SS3436.8/341/354/451、BUG2830/YKT2387。Main全3sourceをPGreviewし実装追加不要。元wholeENV001..004/CFG001..006の10定義・入力・独立期待値を保持し、試験executorの有限化だけを是正する。

ENV: UUID00000000-0000-0000-0000-00000000005e/cutoff2026-09-17T00:00:00Zの固定2lineASCIIgolden、全byte置換/全短縮/128bitUUID差/±1micro/0001..9999上限/null/新配列identity/64並行を元literalで検証。CFG: 固定2lineURL/versions、公開templateの3placeholderを固定値へrenderして独立golden一致、不正shellmarkup/CRLF/unknown/byteencoding・port1..65535/db1..63/version1..16と総65535/65536/65537/dup/case/null/max65848を元独立fixtureで検証。実環境fileやcredentialを読まず、公開template1fileだけsnapshotへpinする。

Concurrent2methodはinvokeAll(work,5,SECONDS)で有限収集し、cancelled/timeoutを合格へ変換しない。finally shutdownNow→awaitTermination10SECONDSをassertし、TWRcloseの無期限待ちを除く。既get5SECONDS・全64期待値/identity分離/入力不変を保持。元sourceへ逆変換+Rootformatter比較で全10oracle不変を確認、旧無期限文字列/終了欠落の構造negativeもmetadataとして保存し製品PTへ算入しない。新ProductTest定義0。

RootJava25/NullAway/Werror、全RootPMD/Checkstyle/GJF/SpotBugs、全Main3/physical3、同一固定source/whole2class10/XML/FESabort0/CRCとinit/独立postを要求。対象RunEnv/StaticEnv2全source四100を確認し、関連BatchRun未網羅は全scopeへ保持。旧exec合算/独自除外なし。No realDB/Root/native/VM/鍵/actual4.class/authorityfixture、SrcMain変更0。コマンド/時刻/OS/JDK/実終了/input/source/hash/coverageは各manifestへ記録、旧同byte証跡は歴史保持する。正式1964PT/53scope、P00404/2、工数nullは更新しない。
