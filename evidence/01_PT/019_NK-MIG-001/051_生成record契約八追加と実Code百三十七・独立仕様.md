# 生成record契約8追加と実Code137・独立仕様

NK-MIG-001、RD MIG-DAT004005/TST・UI254・SS343 SSC342/451、BUG2899/YKT2431。AssetMigrationManifestTest既12へ新8を追加しwhole20、必要他138を含むwhole170/全9Main16physicalを同source/単一execで再検証する。Production Main全byte/外部値/Root filterを変更しない。既162の成功確認再演ではなく七未実行methodの修正に必要な同source回帰。

- PT-MIG-ASSETGEN001: Kind.valueOfの固定4name→4literal Kind、未知/空/case/spaceはJDK契約のIAE、nullは標準Enumのnonnull契約違反NPE。ProductionへNPE catchや正常変換を追加せず、nullをApp受入入力へ変更しない。
- 002: Entry.equalsの同一/別instance同値、全5component一つずつ差、null/別型を独立booleanで確認。
- 003: Entry.hashCodeは31の32bit多項式で別Python算出。Kind.hashCodeはJava25 final EnumがSystem.identityHashCodeを返すので、期待値のkindだけJVMidentity primitiveを用い、Entry.hashCode/Kind.hashCodeでexpectedを作らない。係数31^4と残りの固定算術vectorを保存。全4Kind/Unicode path/MAX longとfinite8worker64/Future5/finallyshutdownNow-await10。
- 004: Observation.equalsの全3component差/同値/同一/null/別型。
- 005: Observation.hashCodeのASCII/Unicode UTF16・Long.MAXの独立固定vector。
- 006: Comparison.equalsの全6component差/同値/同一/null/別型。
- 007: Comparison.hashCodeの零/1..6/Long.MAX各固定vector。
- 008: Comparison.toStringの既生成literal二vector（集計数値だけ、raw path/hash/credential無し）。Entry/Observationのredacted toString契約は維持。

String hashはUnicode codepointではなくJava UTF16単位、long hashはlow32(value xor unsignedShift32)、record結合はJava25.0.4 ObjectMethods.hashCombinerの31*left+right（32bit）。独立PythonはProduction Java/fixture getterを呼ばずliteralから数値を固定する。これらはJDK固定versionの内部値契約で、canonical移行ID/電文やpersisted hashへ使わない。

期待結果: 全170/F/E/S/flaky/notrun0、Root通常compile/NullAway/lintWerror/GJF/CS/PMD適用未分類0/SB0、同一source/runtimeの全16CRC/init/既定四100に加え、独立無filterで全137Code・instruction・line・branch・classのmiss0。原default112とactual137を別列に残し新execを旧execと合算しない。新8だけをdefinition増分、支援162は重複定義へ加算しない。toolselfcheck12はAppへ混ぜない。

fixtureは既abc/空fileのsynthetic metadataのみ、DB/素材/Root/native/held class/VM/aru操作0。対象commit/日時/OS/JDK/tool/branch/command/exit/入力/期待値/actual/coverage/BUG・hashは新normal/独立postとraw-reportへ保存。YKT2431はManifest当部分だけを閉じ、383file/539typeの他対象はPENDING/既HOLD維持、全横展開完了にしない。正式1964/53・元190・全451・工数率nullは更新しない。

当追加費はTest8/oracle/静的準備.5/1.5/3＋必要whole170/無filter.8/2.4/4.8=合計1.3/3.9/7.8pp、cap8、REWORK。元費用/原S-V各10pp/群開始値を保持。PGPT専有費・実tokenはnull。
