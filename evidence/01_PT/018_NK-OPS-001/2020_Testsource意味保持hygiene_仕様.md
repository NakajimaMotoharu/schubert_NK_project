# Test source意味保持hygiene仕様

初回10012診断：832source/CS2705（star2149/同時宣言556）、raw exit145/診断工具0、manifest2ca11b812be3c4feda2b9236eaf6956f38f8e521a5ba2b137865b12c3f7679f2。BUG1787/YKT1538を修正前起票。Graph9三/鍵witness二/製品Mainは不変更、品質PASSとしない。

2026-10-26 07:38 JST、F03_TEST_SOURCE_HYGIENE_V1、開始.5/2/6pp cap10、fresh used24残76/reset1793513544。WBS-F03/411/451/SS354、コードsource bba24d15923831a17e5464328b70fdb950fb2fcf（HEAD c171696df）。元Main hygiene936/3702は既完了の歴史として再実行せず、今回未是正の**Test側**を別対象とする。元PMD2217/Main CS645→0を今回の成果へ再計上しない。

## 着手判定と固定scope

許可済みcompile/静的checkだけ。正常PG9992 inputでMain965/Test835を固定、src/test/javaの835からGraph9 HOLD三file（TemporaryFailureGraph329Test/ApiStartupGraph330Test/WebStartupGraph330Test）を除く832を対象候補とする。Graph9三fileは原byte保持、鍵closewitness二工具はsrc外であり列挙/読取/実行/変更しない。実Test/JUnit/JCE/provider/native/DB/Root/VM/HTTP/JMS/旧job/権限/配備操作0。

最初に同規則・同Checkstyle14.3.0を当832sourceへ実行し、raw指摘/実exit/入力hashを保存。実違反は915/916へ修正前起票する。グローバルの広いException assertion二候補（ReplyCorrelationRegistryTest/OverflowSafeHttpMeterRegistryTest）は原因型/元例外identityの後続assertionが既にあるので今回のoracle不具合として起票しない。既DB/Graph9/PTの再演を伴う是正に拡大しない。

## 機械是正・独立後条件

既SourceImportExpansion.java（JDK Compiler parse/analyze、-proc:none/-implicit:none、**製品classを実行しない**）・SourceDeclarationExpansion.java/IsolatedSourceOutput.javaを完全読取し、独立new-only候補へだけ適用する。旧LAN/VM stage工具は実行しない。JDK25/元normalの正確なMain/Test/dependency classpathをhash束縛し、before/after全resolved member/type/constructor bindingとAST declaration/literal値が一致する候補だけを採用する。

wildcardを元解決先へのexplicit importへ展開、同時宣言を対応AST変数順のまま分離、literal内TABは同値escape、固定GJF1.36.1（長literal非再flow）で整形。未知/重複/曖昧/原本重複/範囲外/symlink/未解決は拒否し、guardを緩和しない。コメントを含む等の自動不適箇所はhold、別途記録し全是正と偽装しない。Main/fixture値/TestID/assertion意味/期待値/上位仕様/既抑制は不変更。candidate差分だけapply_patchで当treeへ反映する。

当sourceを固定した正常六module build（PTは未実行）と候補再Checkstyleを行い、全Main1843同byte、Testの対応source/AST/解決先・可能なCode属性のdebug差を分離して検証する。import/表記だけの意味保持を既成功PTや新coverageへ換算せず、当source whole runtime qualificationは未実行のままにする。必要な非機械変更が見つかった範囲は別修正/必要PTへ分ける。

## 証跡・終了

元rawCS/候補rawCS/工具・全source・dependency hash/実command・日時・終了/差分対象/除外三根拠/未処理理由/正常build・同値postを保存する。元WBS担当費/歴史source/runtime/予算/受入は保持して変更Test hashのtraceをbatch反映。費用は元計画と追加発見/手戻り/tool修正を分け、N/T/専有配賦/工数率の不明はnull。正式1964/53・17/190・QA051final・全安全HOLDを維持。群区切りだけで停止せず、当scope又は具体的残件から独立PG/PTを続ける。
