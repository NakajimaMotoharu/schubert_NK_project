# 保守metadata・OS名構文三Source 独立単体テスト仕様

群18130/3721、HEAD8a87c934ed36340b4004f29bd4cb856d3d8be3da/dev-foundation、Production6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備。事前0.5/2/5pp cap10固定、freshused84/rem16/reset1793774153、F03主費・元ownerP00402/P01702/P00305参照追加費0。

NK-BAT001/OPS009/DAT009・storage/FIL要件、UI251243/SS331§3.13・341§7.3・343§6.13/6.15・333§2、SSC049055/PG-D137156・新PG-D1121、PT-BAT114～121/058～081/PT-SCN008A01。後続3150/3144/264は実repository/file/他component又は静的参照で当三Source全資格でない。全MainはInspectionSummary/ MaintenanceRunState/StorageIdentity、純helper BatchRun/CleanupCounts/MaintenanceActivation/MaintenanceCompletionの全bodyを確認、元DB/native Testのmethod・fixture抽出/改作0。

|Test ID suffix|入力/操作|独立期待値|
|---|---|---|
|MAINT-METADATA001|OS名a/underscore/英数underscore-hyphen/32文字|owner/group同じString参照保持・固定StorageIdentity[REDACTED]。syntax値で実OS lookupでない|
|002|null owner/group、空/大文字先頭/数字先頭/hyphen先頭/33文字/space/slash/LF/Unicode|NPE invariant又はinvalid storage OS identity、owner/group両側独立に拒否|
|003|summary count0/5,2,3/MAX全保護・complete両値|run/count/flag保持・固定観測redaction。completeは観測flagで親gate成功としない|
|004|summary null run/count・flag両値|各NPE、未完了flagでも依存のnullを許さない|
|005|state Optional.empty/同値だが別instanceのactivationでSUCCESS/WARNING completion|指定activation/Optional保持、同値相関を受ける・固定redaction、権限/原本を証明しない|
|006|state各null、activationUUIDだけ不一致/runUUIDだけ不一致|NPE/maintenance completion identity differs|

OS名の詳細syntax [a-z_][a-z0-9_-]{0,31} は既実装された設定valueの内部contract（SS333343のOS役割分離を変更しない）。expectedは手書き境界文字列/元SSの相関・不変観測と固定診断から作り、Production methodで生成しない。原本/DB/readiness/OS権限/parent completionの成功証拠として使わない。再送/並行/GCはimmutable値の外のfile/DB責務で別HOLD、ここでは同値相関と不変保持だけを確認する。

固定公開UUID(0,91～93)/µs Instant/Optional/long/string/enumのみ。MaintenanceActivationのstatic ZoneId.of(Asia/Tokyo)によるJDK named-zone初期化=true（内部file/provider動作の総効果はnull）、businessDate/現在時計は呼ばない。実filesystem/OS lookup/owner変更/DB/JMS/鍵/crypto/Root/native/VM/permit/activation変更/Thread0、実原本・保全物へアクセス0。

六件/一suite/新一execで全三Source三Codeを測定、normalJar/snapshot/現在source/全closure/CRC/単一session/XML/FES・公式filter不変更/手動除外0/execunion0。StorageIdentity/RunStateの条件は全両側、Summaryの自然branch0=N/Aを区別し未達は未達のまま。normal14216/Spot14224を同Mainで再用、Main/Test変更0・新製造0。

command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg18130_maintenance_metadata_six_pt.py。3463/manifestへ実環境JDK25.0.4/OS・command/時刻/branchHEAD/input/helper/Main/Test/class/exec/XML hash/exit/coverage/独立oracle/BUGを保存。新quality六は普通5786へ加算0、正式1964/53/歴史17/190/新WBS受入0/工数null/QA051final/451/全HOLD維持。
