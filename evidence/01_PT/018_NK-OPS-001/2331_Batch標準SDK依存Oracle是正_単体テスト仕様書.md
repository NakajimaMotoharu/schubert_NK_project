# Batch標準SDK依存oracle是正 PG/PT仕様

## 同一source固定前の品質併行（2026-10-28、BUG1971/YKT1719）

oracle差分12404/252f1348と中間source92941a174c9dc82289addcc20ef6d95f5f53314eを保持し、同Testの既知五重複String/33参照を同値定数へ整理する。新12405で当五だけを展開して先行sourceの全tokenを復元し、先行二新定数・明示二承認座標・新283C以外の元token保持も12404と鎖で結合する。これは追加発見の品質是正で元計画完了へ加算せず、元群1/3/5cap10を減額・変更しない。二段source変更後の一つのsourceでnormal/原二＋新一/static/postを一回実施し、成功確認だけの再演を避ける。F02主担当/F03副担当・追加費0、正式受入は不変。

2026-10-28/PG-D740/BUG1970YKT1718。開始source14198cb1878ec73319511ba1067133992d335e63、savec4c505cc8/push32928真正0。対象whole BatchRuntimeDependencyTest、原PT-BAT-283/B283Bと追加PT-BAT-283C。F02主担当、原artifact owner/costはtrace正本を照合する。着手前1/3/5pp cap10、fresh共有62残38/reset1793599188、専有費・実N/T null。旧計画/v4等は変更しない。

RD171常時監視Micrometer指定、origin/main8b91944dfのSS351標準metric規定、既PG-D536/615/1750/1810の公式SDK1.17.1の採用を独立根拠とする。新仕様や未知依存の許容ではない。既sourceの閉鎖八座標に io.micrometer:micrometer-core と io.micrometer:micrometer-registry-prometheus が欠けるため、承認済み二座標を明示追加して十座標とする。Production Main/POM/外部仕様は変えない。未実行の旧caseを実測失敗にせず、source-level不整合として記録する。

独立oracle：二座標の固定literal XML、version1.17.1、既定compile及び明示compile、既定jar及び明示jarを受理。各欠落/重複・version1.17.0・scope test/runtime/provided/system・type pom・classifier foreign・group foreignを拒否する。元BAT283の未知依存/禁止API-Web-Protocol/Flyway/Bootstrap main依存検証、BAT283Bのtest fixture誤scope/type/version/classifier/重複検査は維持。expectedをProduction関数又は実POMから生成しない。

PT_DEFAULT：whole Test全文確認済み、JDK regex/collectionと固定normal snapshot内Batch POM readだけ。`-Dnk.pt.repository=<当source正常snapshot>`を固定し、POM前後hashを照合。new owns空CWD、@Test全三methodだけをclosed JUnit catalogから実行。Product Main呼出/起動0、実DB/JMS/ネットワーク/VM/Root/鍵/Graph9無し。Main coverageはN/A（実行0）、全Mainの非実行と全1843 byte同一を検証し、TestのcoverageをMain100%へ転用しない。ConfigurationTemplateContractTestは全resource準備をしておらず当群へ混在/部分抽出しない。

変更前sourceの八→独立十座標の差二を公開metadataへ固定し、是正後の元method tokenは明示二座標・新helper呼出以外を保持したことを独立照合する。新283C/新helperは固定versionと全負例を別に検査。normal六PT0、原二＋新一の3/1suite、PMD/CSと処理異常/残文脈、同sourceXML/one exec/CRC/全Main/Test byte、traceとcurrent集合を保存する。失敗/未実行/skippedを合格扱いせず、既成功確認再演無し。commandはchecked entryを用い実argv/環境/JDK/OS/commit/終了・input/期待/実際/証跡hash/BUGをmanifestへ記録する。451/正式1964PT53scope・17/190・工数null/QA051final/全HOLDを維持する。
