# WBS66 F03 現行静的検査の担当引渡し

判定ID W66-HANDOFF-F03-20261118-02。F03担当への公開用。2026-11-18 JST、Core `b00f871804b6d25f1c3e5e6d3b77d7bcca340923`。実受領は未確認。11月25日23:29 JSTまでの4役割引渡しのうち、F03の009を更新する。F02・C02・F04は012の前回判定と各既存記録を参照する。

| 製品module | 現行MainのCheckstyle | SpotBugs Max/Low | 残条件 |
|---|---|---|---|
| Protocol | 169、指摘0 | 176 classの物理hashが元PG37646/48と一致、既解析の指摘・欠落・エラー0 | 現行全451と横断条件 |
| Storage | 25、指摘0 | 80 classの物理hashが元PG36820/22と一致、既解析の指摘・欠落・エラー0 | 当sourceの実native・全451 |
| Bootstrap | 87、指摘0 | PG38206で200 class、数値終了0、指摘・欠落・エラー0 | PMD適用性と未実施native／Root recover |
| Batch | 200、指摘0 | PG38206で646 class、数値終了0、指摘・欠落・エラー0 | PMD適用性と未実施native／Root recover |
| API | 283、指摘0 | 当Coreの選択部品のみ、全module未実行 | QA056型チェーン、全体解析と451 |
| Web | 262、指摘0 | 当Coreの選択部品のみ、全module未実行 | QA056型チェーン、全体解析と451 |

CheckstyleはPG38200の同一run・全1,026現行Main。SpotBugsは4moduleの1,102 classを現在の物理class単位で照合し、元run・再解析・未実行を区分した。PG38206の初回2件はMaven解析準備で終了1、BUG-3211/YKT-2671で是正し、再実行で初めて両解析が終端した。

比較工具のPG37322は独立したtool source `fd69f7d62595c021ceff48509ea032a5ff17c5d2` の142成功。元SSC447はPG36620の152成功・失敗0・エラー0・skip 0・未実行0。現Coreの製品PTや実CHRへの加算は0。独立判断証跡は [PG38218 manifest](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG38218-wbs66-f03-current-owner-handoff-v1/manifest.json)。

F02の宣言依存はPG38186、実classfileの4moduleはPG38202。QA056対象を含むAPI/Web全体と実Artemis境界、各SYSのruntime、451、両親の終了依存は継続。正式17/190、1964PT/53scope、当群増0。
