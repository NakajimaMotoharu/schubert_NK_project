# 2436 現source全Java1821・静的現況計測結果

2026-10-28 22:07 JST。2435/PG-D785、群F03_CURRENT_ALL_JAVA_STATIC_CATALOG1821_V1。Production source db33c6a371d3dbc8e84f70462e0e56351bbb18b4、operator保存HEAD218157ed7ab4b400a360adace63c5e5e8eb5fd87/dev-foundation、未配備。開始見積1/3/6pp・cap10は不変更。共有開始used8→直近fresh9/残91/reset1793774153、secondaryなし。共有観測1ppは専有費でなく、専有費/N/T/工数null。原/v3/v4/v5を減額せず、通常群の終了は自走停止ではない。

## 有限入力・実結果

固定normal13242のsnapshot/全input hashとworktreeを前後照合。Java1821=Main965/Test856、六module、Main1843/Test1974物理class、JDK25.0.4、PMD7.28.0＋既record修正JAR、Checkstyle14.3.0、全rule/tool/dependency hashをbeginへ保存。fresh六Main JAR/同source六test-classes＋固定外部auxを使用、旧project m2 JARは置換し未知project依存は拒否。対象source/Test/appの初期化・実行、VM/DB/JMS/Root/サービス/私有raw/保留二工具への内容アクセス0。

PG13252元entry5f8874370fc4d6c75ebf521780ec5fdb9634c434f18a7cee9deaa330c2d88765はfresh JARがbuild-classpathにも含まれる重複を正しく拒否できずassembly guard真正1で停止。SLOT/OUT/PMD/CS未開始を保持しBUG2044/YKT1792起票後、別immutable13253に修正。aux自己反例は正1/負4。旧停止を成功へ読み替えず、解析自体の再実行はしなかった。

13253元session5526真正0、PMD真正4/CS真正0、processing/config error0、全input前後一致。PMD8022=Main1502/Test6520、CS0、**qualityGate1・全F03未受入**。moduleはapi2302/batch3093/bootstrap660/protocol10/storage249/web1708。独立13254はXML全件/全1821source・1843Main/1974Testと全hash/command終了を再集計、typed非同値9反例、真正0。解析完了0と品質合格を区別する。

## 元catalogとの同一性

13256は旧global原catalogの現存7990ID、既追加18IDをsaved registry/原XMLから復元し、path＋位置以外の全attributes＋diagnostic文面のmultisetで今回全件と比較。duplicate-literal内の最初の行番号だけを位置として正規化し、値・出現回数・method/class等は保持する。原7990＋既追加18=8008は全件存在、消失0。重複signatureは個別発生箇所IDを推測せずMULTISET_ONLYとして保持。負3は既診断欠落/追加欠落/追加重複を拒否。

差14は全件Test CloseResourceで、PMD-NEW-PG13253-001～014として原path/全attributes/message/source SHAを保存。既存実装の資源漏れ/false-positive/是正済みとは未判定、actualViolationnull・manualPurposeReviewfalse・PT免除false。BUG2043/YKT1791へ追加調査対象とし、二Login指摘も今回全体に存在することを確認した。原全体の欠落原因・型/解析条件差・引渡し前後条件/動的所有は未確定HOLD。

13258は同source別catalog補足。現追跡8022/corr1419/refs3273/pending1183/noRef4749、元995全row/owner/cost/旧runtime/currentQualificationはbyte表現のfield値を完全保持し8反例。14追加を是正/目的確認/受入へ算入しない。原globalや原群開始8008は不変更。485のsource資格pointer13248/49はcode資格として保持し、追加catalog資格は13258を別参照する。

## 証跡

全pathは本directory下`evidence/provisional/<folder>/manifest.json`。各manifestから原XML/findings/入力/command・終了code/negative・検証JSONのhashを追跡できる。13256は保存公開結果のread-only比較、13258はmetadata補足でありProduct PTでない。

| folder | SHA-256 | 元終了 |
| --- | --- | --- |
| PG13253-current-all-java-static-v2 | 751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf | 0（PMD4/CS0、quality1） |
| PG13254-current-all-java-static-post-v1 | 541ae47d4670f4e5314be883a66442248c0da583d036265ae88d071d6bcd51e8 | 0 |
| PG13256-current-static-catalog-reconcile-v1 | 625f1b7f45924159ce8f15fb03994e0d42b71ae90f836fa03d7b00437c4c7889 | 0/session51639 |
| PG13258-current-catalog-supplement-v1 | 6e4710f066ec0a8308c7437f4c96de0219f50e3ccef2368640f762833a23bd27 | 0/session47745 |

commandは各`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg13253_current_all_java_static_v2.py`、13254_current_all_java_static_post.py、13256_current_static_catalog_reconcile.py、13258_current_catalog_supplement.py。実施済みのため確認目的で再起動しない。

正式1964PT/53scope、個別17/190、工数null、QA051final、全実経路/Graph9/保留二工具/unknown二file-primary-costは不変更。ProductPT0・coverage未測定・全451/trace gate未受入、IT/ST完了宣言なし。通常保存push後も必要な独立PG/PTを継続する。
