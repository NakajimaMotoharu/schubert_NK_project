# Snapshot scratch限定結果（2026-10-19）

親指定GPT6.1Sol/high、実アプリ設定は未検証。Linux/JDK25.0.4/Maven3.9.12/子umask0027、PG5540固定archive。VM/原DB/Backup操作0。正式1964PT/53scope・QA051finalと別の単体測定。

|元run/session|Source|真正結果／判定|
|---|---|---|
|red-v1/65292|a78b94c62|1/六format0後Protocolの非零test guardで0件、予定Red不成立/BUG1456|
|red-v2/73357|c75052c1b|1/22件到達、依存18/negative二PASS、Main二はclass copy検証失敗・予定Red不成立/BUG1457|
|red-v3/90628|0bc2b81a5e7ccc822c9e6e3385bcb340ebf183a2|1/22件、001/002だけnative取得0期待・実1の予定Assertion、他20PASS/error0/skip0、予定Red成立。合格へ算入0|
|green-v1/19180|a19a9f7d940b4f9fba47e51bd9be675f4420401b|0/29件・5suite・failure/error/skipped0、source固定、全六format先行/built四SpotBugs0/NullAway-Werror compile0|

private `pg5540-snapshot-scratch-red-v3/manifest.safe.json` SHA **5631973e95503d23953d42dbfdc26b1f2e0196d7b736d9adc44ead94ab6e6c0a**、green-v1 SHA **fb49c8579faff830f2df86f80286f9073392d436b0b986a537b3a0bbbf8e6a78**。元log/XML/archive/ownerは各runに保持、書換え0。Mavenの赤終了を正常0に変換せず、理由を固定count Assertionのみに限定した。

Greenの対象ResponseSnapshotCodecは**LINE154/0・METHOD14/0・CLASS1/0・BRANCH70/0（covered/missed）**、四counter100%。whole/API全体coverageではない。実四built Main779の物理比較はRed全同byte、Greenは当codec一だけ変更/追加0/削除0。他三moduleの未実行試験を成功にせず、依存契約18を当source選択結果の内訳へ明示する。旧296 native/全3896を新Sourceの成功へ加算0。新Mainの修正commit a19a9f7d9、PG-D434・BUG1453/YKT1217に対応。

当Main二の失敗前nativeなし/固定Error同一性、negative二の旧型検出と最後の実end、元独立JCE/圧縮golden七の正常/境界/null/未知/暗号provider/破損/trailing/dictionary/bombを検証。expectedは固定count・独立vectorで、production methodから生成0。class copyは静的対象methodの命令/handler保持・scratch前Error/観測挿入だけで、JVM検証を無効化せずMain他methodのcoverageの代替0。

PG5542/元11257真正0、当実class SHA9edf1d418944aba0b1add8d599356379f0ce0e42d8c3931d785714518ca207abでscratch PC3がcompress ctor11/decompress ctor10より先、post-prefix本文/handlerはlocal slot1/2とpool indexだけ正規化して旧版と厳密一致。endはcompress73/108、decompress125/169の二siteを維持。全八fixture（修正一/非該当七）も即時store後の次命令がany-finally保護内/normal・exception end二を確認。private receipt SHA **cc4b8e5ccd0b1f359b9acd1bb44e1d0cefad390cc5a48bc99b7c5219965fcbb1**、独立否定Python二成功。old jarの当classも元全体actual SHAへ照合した。

公開[データmanifest](evidence/output/PG5544-scratch-v1/manifest.json) **e8f6006e3c0bfef23d730b9337551f73fa4ae67934dcc1af3999800078ab5f96**／[実行context manifest](evidence/manifest.json) **6ee205b87bbc664c1bef0a34cc4b9c70a7ae22017a5567511670502bd517d5f6**。全API selected XMLはsession IDをSHAへ変換しcounter/意味を不変保持、target外も報告から除外0。OS/JDKは元五suite XMLのcoherent propertiesから抽出し現在環境で過去を埋めない。branchは実行直前source commit/pushのdev-foundation記録を根拠とし、元runnerが独立branch field未捕捉だった事実も明示。publisherの初回unused import一はcommit前に除去/lint0、既出力を再生成・上書きせずcontextを新canonical manifestへ追加した。

BUG1453/YKT1217は当codec単体・全八横展開の是正/再発防止まで確認。新Source whole3900等はまだ実行しておらず算術加算で認定しない。F03/CHR/全四100/451/trace/引継ぎ・新Source実経路は未受入、全体資格前状態を維持。BUG1455歴史stderr同一性UNKNOWNも保持。全raw properties/秘密はprivate、公開hash/数値のみ。
