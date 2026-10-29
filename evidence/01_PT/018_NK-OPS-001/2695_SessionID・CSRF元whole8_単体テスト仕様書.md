# 2695 SessionID・CSRF元whole8 単体テスト仕様

Program NK-WEB-001/NK-AUT-001、source6b53efeec87f3ec36a840dd8e7759656cb4aee5c、Git96a02285f/dev-foundation。RD FUN-001/AUT-001..004、UI226、SS314 §7/8.1・352 §3、PG-D093/097/912、Test WEB001..004/032..035。元Test140+131行/Main76+76行、全body/初期化/fixture/JDK依存確認済み。PG14522/14524、event3085見積.25/1.5/3pp cap10。PT_DEFAULT。旧source2361は比較履歴のみ、新sourceの合格へ転記0。

|Test ID|操作/独立期待値|
|---|---|
|WEB001|固定32-byte zero/sequence/ffのcanonical Base64url43とPython独立SHA256三vector、REDACTED表示|
|WEB002|欠落/null/42・44文字/不正alphabet/unused bitsを拒否、固定安全message/cause無/suppressed0|
|WEB003|自己FixedRandom正常三vector/失敗を通し自所有32byte消去、caller RNG呼出一回|
|WEB004|自己CSPRNG・10thread100task、重複0/32byte/JDK別SHA256計算と固定vector、各get20秒|
|WEB032|0..31byte→固定hex64、provider異常→固定安全例外/cause無/自所有buffer消去/null契約|
|WEB033|全長64..128、先頭/中/末尾の差と長さ差を拒否、同値のみ一致|
|WEB034|欠落/null/空/63・129・巨大/非ASCII等拒否、例外の機密非出力/REDACTED|
|WEB035|自己CSPRNG10thread100task・各get20秒、64hex/固定shared参照と不一致、100unique|

有限taskをown180秒JVM timeoutで囲む。invokeAll/TWRの局所無期限は外側制限と区別する。実セッション発行・認証回避・実cookie/token/鍵/DB/HTTP/Root/VM/graph9/cohort操作0。公開XML/manifestへ乱数・session値は保存せずcase名/PASS/件数・hashのみ。固定公開dummy literalは資格情報ではない。

normal14216の全input/六Jar/JDK25.0.4依存と独立static14224を固定、元whole二classのみfreshコンパイル後一回実行、原環境prefix・一execCRC・元XML・Source全physicalを14524へ。Main/Test変更0。二Test ownerUNKNOWNは保持、Main既ownerP01501/02を継承。期待値をProductionから作らず、coverageは当二Sourceのみで対象外分母/別exec合成/正式更新0。独立postは不足があればstrictFour100GateExit1を保持する。

command: python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14522_session_csrf_whole_eight_pt.py。後続14524も同entry。環境/version/command/exit/日時/branch/source/inputhash/exec/coverageは両manifest、結果2696へ。秘密scanは限定三書式のみでwholeG07の保証に拡張しない。
