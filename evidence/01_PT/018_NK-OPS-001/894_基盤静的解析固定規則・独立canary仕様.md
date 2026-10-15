# 基盤静的解析固定規則・独立canary仕様

WBS-F03、NK-OPS-001、SS354、411 §2/4～9/11/12、451。Test ID=PT-QUALITY3382-001～006。Productionはa9cb0ac9a3a0f9bc37d0952943a98016c7a25f25/PG2802、Java25。私有失敗原本を消さずnew-only slotで実行する。

| ID | 入力・操作 | 独立期待値・根拠 |
|---|---|---|
| 001 | 全六module Main Java（生成record/package-info含む）・既終了3372六Jar/依存 | 全849fileをgit a9・3372開始input hashへ照合、全1643classを3372原class hashへ照合。欠落・改変・source混用は拒否 |
| 002 | PMD7.28.0、凍結三category全priority、実auxclasspath、cacheなし | 指摘・処理errorを別集計し、非0をPASSへ変換しない。初回診断値は事前期待0を捏造せず実測して分類対象とする |
| 003 | Checkstyle14.3.0・凍結XML・全同849file | 既Spotlessと役割分担し命名/構造/文字を実測。終了codeは指摘数の8bit折返しがあり、exit133をOS signal終了と即断せず原XML645件と照合。全gate未合格を維持 |
| 004 | GatePositive/GateNegative、各javac25 warning error化 | Java25のsuper前localを含む正常constructorはcompile0/解析0。合法だがNPE空catch/不正method名/空statementの反例はPMD二ruleとCheckstyle二ruleで拒否。Production生成expectedなし |
| 005 | 合法GateRecord nullable byte[] component/close、通常static GateFieldのlazy初期化 | 公式PMDでrecord内部例外を独立再現、通常fieldのNonThreadSafeSingleton指摘1を確認。工具修正後record処理error0、同通常field違反1を維持。私有fixture外のnative/DB/Unit操作なし |
| 006 | 一class限定PMD overlay＋全元849file/全aux/rule/前後hash | 正式規則を無効化せず、処理error1→0かつ元2220指摘のfile/rule/line/message tuple全件完全一致。候補が非0のままなのでF03受入0・Production PT加点0 |

規則は`tools/quality/static/{pmd,checkstyle}.xml`、canaryは同`canaries/`。同時実行/再送は新業務操作を発行せず、mkdir新規slot・exclusive output・既job終端確認で二重書込みを拒否する。欠落null/未知値はsource/hash/Jar/XML等のassertで拒否。Production全coverageとは別の非Production品質工具検証であり、当scopeからJava除外や全体率を作らない。

実command: `pg3382_static_gate_server.py`（aru、実byte/source確認付き）、`python3 -B tools/quality/pg3384_static_gate_canaries.py`（v2 before）、同`--after`（v3）、`pg3386_pmd_record_after_server.py`（aru、元入力同一を前後確認）、`pg3388_static_diagnostic_collect.py`（RO回収）。runごとのcommand/exit/全input/Jar hashとraw XML/logは公開manifestのhash/私有locationで一意に追跡する。

秘密・session・鍵の実体は扱わない。HardCodedCryptoKeyの初回1件は違反確定ではなく、ResponseSnapshotCodecの外部入力key→長さ検査→cloneと表示label引数を追跡して分類予定。実keyを表示して確かめる操作は禁止。既Root/VM/Backup/ADMIN/Browser/Maven全体の再演は不要で実施しない。
