# PG2478 BrokerJournal独立境界

NK-OPS-001／BrokerJournalEvidence anchor/contentSha256/consume/consumeClosedHistory/fields。RDの障害検知・監査秘匿要求、UI運用設計、SS321§13/341/343、SSC125/131/132。主担当WBS-P017-10、N04は参照費0。events0639/0640の着手前予算0.5/1.5/4週次共有ppを保持する。Production cdbc07cdf77370d521e64de8b327da7f6752139b、PG2404全3637PT・1643Main、PG2474資格済みlatest九nativeのみを使用し、旧sourceのnativeは輸入しない。

| Test ID／method先頭 | 独立fixture・操作 | 期待値・根拠 |
|---|---|---|
| PT-BJ2478-001／bj2478001 | 手書きvendor2.56 JSON、boot/Unit/時刻/priority/Invocation/版/メッセージ差、0/65536/65537 byte、UTF8/null | SSの真正metadata条件。正規anchorの三固定値・redacted表示、正確65536 byteは受理、未知/欠落/異常はIOException、null契約は拒否 |
| PT-BJ2478-002／bj2478002 | 空/4MiB+1/末尾LF欠落/不正UTF8/配列/null型/二object/孤立surrogate | 正規化で欠落を成功化しない。IOException、診断へraw fixtureを含めない。null契約拒否 |
| PT-BJ2478-003／bj2478003 | 手書きTreeMapからNKJOURNAL1/ROW/ordinal/key/UTF8hexを独立構成し標準SHA256、cursor/time/digestを一つずつ変更 | 三vendor eventの完全historyだけ成功、raw SHAを独立計算。終了anchor不一致は拒否。expectedをproduction methodから作成しない |
| PT-BJ2478-004／bj2478004 | 専用test JVM、provider registryの全除去とfinallyで元order復元 | 両digest経路のprovider欠落は秘匿IOException。復元後known SHA256 abc固定vectorとgolden三eventが正常。並列無効・JUnit Isolated。VM/業務providerに作用しない |

実commandはclean固定後、固定PYTHONPATHで `python3 -B tools/quality/pg2478_broker_journal_selected.py`。専用LANのfresh PG2478-selected-v1のみ、immutable PG2404 Main/fixtures/依存JARと当九nativeの前後hashを検査、javac -Xlint:all -Werror、独立JUnit XML四件/FES/aborted/not-runを確認する。全Main classByteMismatch0と六moduleの四counter/XML/hashを保存する。未実行を合格にしない。Production変更・VM操作0、全体回帰/451正式受入/工程完了はこの選択試験では宣言しない。

既実装が仕様違反なら修正前にBUG/YKTを起票する。fixture/新工具の初回未完成は試験製造として実失敗を保存し、成功へ補完しない。実行日時/commit/command/OS/JDK/終了値/入力SHA/実XML/coverage/関連番号は結果manifestで追記する。

## 実結果（2026-10-14 07:26JST）

v1 actual1：新選択工具のGson classpath不足、四試験のNoClassDefFoundErrorを保存。v2 actual1：新closed-history fixtureに終了eventが無く正規停止条件で拒否、残三件は成功。いずれも新試験・工具製造の初回不備でProduction仕様違反ではない。各fresh namespace/log/XMLを保全、合格加算0。

v3 actual0／testSource b02133d20d4927988c486377a4bb0103b913fc37：四PT/FES/aborted/notRun0、javac warnings0、Main CRC mismatch0、同native九を使用。技術残L814/M158/C9/B594（直前L820/M158/C9/B606から6line/12branch追加）。manifest ca613fb531d13fa7ec8d898d1f18a72aac268381bec407cd453d90ddf589cab2、`evidence/current-broker-journal-boundaries/manifest.json`。

v4 actual0／testSource28f5fd390bfa9bcefda8ed9fb9090e7d25228479：anchor末尾LF欠落、空cursor、0monotonic三境界を追加。22:26:14.477761Z～22:26:21.969820Z、四PT/FES/aborted/notRun0・warnings0・classByteMismatch0、Main/fixtures/依存/native不変更・VM操作0。manifest a5a78fef12faf78adb2834caf0ee4d4c27f1ab6a55cb3fafee92e75ea02df17b、payload aa70cf2cc68679de87034dac36de1378e25e26b691b9f87bee918c56047f2422。技術残L814/M158/C9/B591、群計6line/15branch追加。対象BrokerJournalEvidenceはline181/181・method13/13・class1/1、branch99/100。残306行のstrict JsonReader最終peekの一分岐は未閉鎖。到達不能・除外・100%として扱わず、厳格parser契約と実入力条件を別途調査する。

最新証跡=`evidence/current-broker-journal-boundaries/manifest-v4.json`。環境は専用LAN Linux/JDK25.0.4、PG2404固定依存＋成功XMLのGson、JUnit並列無効・provider復元確認済み。全回帰3637件の別source結果へ新四PTを合算して全体合格としない。正式1964/53・全leaf0・IT/ST未認定は維持する。
