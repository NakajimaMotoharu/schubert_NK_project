# 退役record純codec・値invariant 独立単体テスト仕様

PG17970/event3703、source6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備、HEADa050e523d59b6664930fd5a6a0b653978ee41acb/dev-foundation。主P00403/関連F03追加費0、固定1.5/4/8共有pp cap10、fresh82/18/reset1793774153。NK-BAT001/OPS009/UI251・origin/main8b91944d SS343§6.16/SSC055/PG-D161・新PG-D1113。3031/3032/3271後続索引/元normal14216を参照。

PT_DEFAULT：MaintenanceRecordsとMaintenanceRetirementの全body・BatchRun/Activation/Completionの値callee、原MaintenanceRecordsTest全344行を事前確認。新quality四はSSのNKRET1 ASCII LF/195～204byte/年0001～9999µs/厳密400日超/count1～2147483647/小文字hex64/redactionから独立設計。旧MaintenanceRetirementRecordsTest wholeはLinuxDirectoryCalls Fixture依存のままHOLDで抽出/改作/実行0。本新testをそのwhole又は実GC/退役/intent/permit/DB後条件の代用へ使わない。新memory fixtureは実namespaceへ書出さず、権限の発行/公開/退役をしない。

|Test ID|入力・操作|独立期待値|
|---|---|---|
|RETIRE-CODEC001|public固定UUID末尾0123/cutoff2020-01-01/最新終了同日/prepared2021-02-04+1µs/count1・MAX/digest0123456789abcdef×4|手書NKRET1全byte195/204・各field復元。400日は2020閏年366日＋翌年Jan31日＋Feb3日=400、+1µsだけ有効|
|RETIRE-CODEC002|latest<cutoff/>MAX/非µs、prepared>MAX/非µs/400日以下、count0/負、hex長/大文字/未知字。年上限正常例|各invariant固定IllegalArgumentException・invalid maintenance retirement/cause null/supp0。各OR条件を独立に拒否、厳密400日で可否を逆転しない|
|RETIRE-CODEC003|NKRET1不正magic/LF/byte/長さ/別record/時刻不正・alias/count先頭0・plus/hex不正|固定IOException・maintenance record is invalid/cause null/supp0。parse後に再encode完全一致しない表現は拒否|
|RETIRE-CODEC004|各null、encode二回の配列同一性/片方変更、decode後input破壊、toString|nullはAPI契約違反NPE・catch正常化0、独立byte所有/復元値保持・固定redaction。JSON/session等の外側責務へ拡張しない|
|既BAT038～045八|元literal/null/alias/全byte変異/64並行/trace|元Test不変更。新四を足した同一execでMaintenanceRecords全Sourceを測定するための必要repeat八、新規成果に加算しない|

同じProduction methodでexpected byteを生成しない。digestは公開任意64hexという値契約だけで、実plan SHA/全activation集合との整合やGC許可を認定しない。原八は自己new SLOT CWDのtarget/maintenance-record-tracesへ公開fixture四fileだけを記録、自己executor一/最大8worker64task/future5秒（actual worker数null）を正常close。新四はmemoryだけ、実file/DB/MQ/Root/native/鍵/clock0。並行のsharedformatterは元八の必要同exec測定で確認、実再送・crash/資源/認可の後条件は元wholeHOLDのまま。

command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17970_pure_retirement_codec_twelve_pt.py。normal14216/Spot14224/Java25.0.4・公式JaCoCo0.8.15/親180秒を同source/input固定で再用。全二Source二Code、旧Records partial保存・新Retirement Source追加、単一exec/CRC/全closure/四counter実測・安易な除外/execunion0。未達を未達とし、Failed flaky skipped not-runを合格へ算入しない。新quality四/必要原八/普通5786とquality別・元実行費を分ける。3447と公開manifestへ実環境OS/JDK/branch/HEAD/時刻・command/終了code/全hash・結果/coverage/BUGを保存する。正式1964/53/個別新受入0/工数null/QA051final/451/全HOLD維持。
