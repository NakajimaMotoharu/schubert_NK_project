# JDBC役割metadata小共通化 結果

2026-10-31 / PG-D985 / 3082 / 群3407。対象はquality toolの純metadata部品であり、Production進捗0。

library `tools/quality/jdbc_role_metadata_v1.py` SHA cd1c4ef43d458dcb36f6a1f6f9e3e577c679b6b4e060f28c20e7e8217c379759。PG16068/c31582・公開`evidence/provisional/PG16068-jdbc-role-metadata-qualification-v1/manifest.json` SHA002ae110aef0d25c2251f1db99dd6162d46cba4d31859afa05c59452a7309462、lint/body0、Q-JDBCROLE001～008全成功/FES0。NULL/型/長さ/CR/NUL/Unicode escape/引数/throw/alias/不変位置を正負照合、現BatchRun八＋CleanupTerminal八の保存roleと現在Source byteを結合した。旧Product/旧失敗工具を実行0、新用途レビュー件数も0。

PG16070/712a86・`evidence/provisional/PG16070-jdbc-role-metadata-post-v1/manifest.json` SHAcf205ced9dbdb41894dbdd70997425c2145c58daf4193decebb24f8fd8d8d475、lint/body0・独立metadata14変異拒否・library静的pyflakes0。元unittest全八のactual output、core hash/AST依存reのみ/関数三つ/IO・eval・exec等なし/全作用0/正式未更新を独立照合した。

途中、libraryをpg11123のtop-level entryとして渡した管理command一件は、当工具がpg番号entryだけを受けるguardでmain前に拒否（ffc4ed）。ライブラリへの直接実行は再発行せず、guardも変更せず、16070の許可された静的read/lintだけで確認した。Product/fixture/拒否PT/プラットフォーム拒否ではない。core/qualifier/全旧実行済み工具を変更せず保存する。

この部品は完全Java parser/型解析/自動許可判定ではない。コメント内にもliteral candidateが現れる限界をQ004で明示し、callerによる固定source/hash/PMD span/型集合/全scope/個別根拠照合を必須のまま保持する。DBやRootを実行する機能、PT対象自動選択、期待値生成、guardの変更、HOLD解除は0。個別の独立oracle/レビューは共通化しない。

次の同種reviewでcapture済み本版を利用し、parameter/aliasの部分置換を減らす。削減率/専有token費は後続比較まで未測定であり、予測減額を工程完成率としない。着手0.5/1.5/3共有pp cap10・開始52/15:00fresh52、共有丸め差0≠専有費0、N/T/専有費null。元/v3/v4予算は保持。

current2125/284・477Source662physical・四256/374・F03用途96/残833・ordinary2116/5786/fixture九・正式1964/53・歴史17/190・工数null・QA051final/全451/HOLDは不変更。command/OS/Python/時刻/branch/HEAD/Source/tool hashは元manifest/checked entryへ結合。工具metadata検査8/14をProduct PTやJava coverageに加算しない。
