# 3408 保持Expiry監査・Caddy残budget原十五PT仕様

NK-OPS-001/主F03/関連P018-09追加費0、Source6b53/normal14216、開始HEAD705dc616f6beeb7438652ced4a237a5331c473e6、群PG17580/見積1.5/4/8共有pp cap10。RetainedExpiryAuditTest全177行・CaddyParentRemainingBudgetTest全31行と呼出しstatic bodyを確認。Main CleanupExpiryExecution424全体の既17479、MorningStartupLaunchOwnerの既16617/2534/2536同byteレビューを参照し、今回の全Main新読取と称さない。新Test byte940314bd…/4597cedb…、Main f7100ed3…/caca5ef9…。

Program CleanupExpiryExecution.verifyPriorAudit/verifyPriorExpiry、MorningStartupLaunchOwner.caddyRemainingFloor。RD DAT009/OPS009/UI251/SS331341343 SSC302、SS342 SSC186。PT-OPS-EXPIRY-AUDIT-SSC302001..014とPT-OPS-CADDYFENCE004、whole二Test十五methodのみ・抽出/改変なし。

## 独立期待

監査001は固定UUID/runとcutoff2026-09-30、audit cutoff09-23、終了00:00:02Z・before3/after1/target-success2/failure0/null code-summaryを受理、0とLong.MAX_VALUE境界も算術一致。002～012はSTATUS WARNING・終了不一致・七日前cutoff+1s・before/after null・before<after・差不一致・target差・failure1・errorCode/summary値を一項ずつ拒否。StorageIoException UNAVAILABLE/固定文言/cause-null/suppressed0を独立assert。013のnull reference/auditはNPE契約違反。014はnonSkip又はselected1をStorageIoException、connection/request nullをNPEとしてJDBC proxy呼出し数0を必須とし、DAO/実DBへ進まない。invalid data recordをDB DDL合格としない。

Caddy004は残100e9ns→floor70e9、同floorに95e9/80e9/70e9+1はtrue、70e9/70e9-1はfalse。18e9/30e9→0、30e9+1→1、1800e9→1770e9、0/-1/Long.MIN/1800e9+1/Long.MAXはIOException。固定Test literalがoracleで実時計・Root budget renewalなし。

null/境界/異常/例外とgetter invariantを全wholeで確認、並行・再送・資源はpure static値比較/整数演算につき当callに存在せず、injected proxyも全call禁止で所有資源0。現在DB/FD/原本/実native/鍵/permit/VM/Unit操作0、四held/六native true0/RootFailed absenceをpostで確認。二全Source十二physical（Code六/NoCode六）を全て分母に置き未実行Codeを0coveredで保持するが、旧17482/16620全Sourceproofを置換/exec合算せずscope-only追加とする。

command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17580_retained_audit_caddy_fifteen_pt_v1.py。Java25.0.4・固定六normalJAR・SDK/reporter資格参照/新SLOT/append=false/180s、元全正常compile/署名/成功PTの確認再演0。raw/post/独立元method catalogとliteral oracle/Test CRC・registry/WBS/環境/command/exit/counter/hashは3409/3410へ保存。Failed/flaky/skipped/not-runは合格にしない、coverage未達は未達、formal1964/53・工数null/QA051final/HOLD不変。
