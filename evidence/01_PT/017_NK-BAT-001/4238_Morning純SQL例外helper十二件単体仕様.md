# Morning純SQL例外helper十二件単体仕様

NK-BAT-001、OPS009/DAT009/UI251、WBS-P017-01.03、SS332/354 SSC341（main03794704417）、BUG2852/YKT2359。内部実装詳細として既private preserveCatalogFatal/closeReplaceをpackage-private MorningSqlFailuresへ整理し、MorningDatabaseSession private wrapper・全20捕捉/outer primary・SQL/TX/資源ownershipの動作を保持する。新wrapperは実Root/DB能力を持たない純関数。原holding Test65の抽出/置換ではなく、既仕様の例外型選択を新しい独立classのwhole12として検証する。

PT-MDB-PURE341-001 primaryなしはnonnull cleanup3型を選択。002 SQL/Batch/checkedIO primary＋非SQL cleanupは既cleanup選択。003 未知Runtime/Error primaryはfalse/fresh固定Batch secondary、provider graphをcopyしない。004 checkedIO primary＋SQL secondaryは既false/no一律graph分類。005 SQL/Batch pairはprimary graphの元Error優先。006 primary非fatal＋SQL secondary graphの元Error、両非fatalはfalse。007 SQL/Batchの非fatal自己next/相互cause/suppressed循環は有限帰還。008 SQL/Batch以外の入力型をcatalog専用portで一般化しない。009 helper failure/secondary非NULL契約、primary NULLは許容。010 共有StorageIoException三reason/固定message/NULL契約。011 共有finite graphのcause/suppressed/SQL next/直接Errorの固定object identity。012 suppression無効の未知primaryも既選択を保持しraw secondaryを付与しない。

期待はSS341の型表、事前に作成するError/Throwable object identity、固定literal message/原因/secondary件数から決める。production methodでexpected生成しない。共有StorageIoException/ReasonとBatchRepositoryExceptionも全source/全physicalに含め、constructor/enum/NULLとgraph全分岐を測り、未使用support classを除外して100を作らない。JDK Throwable/SQLExceptionとJUnit/JSpecifyだけ、Connection/proxy/fakeDB/Root/authority/反射/worker/FS/network/native/credentialなし。新helperのnull拒否は内部nonnull invariantの確立で有効な本番入力を変更しない。

費用は既残Testability/Test/static .3/.9/1.8を、source＋12定義.1/.3/.6、通常資格.2/.6/1.2に分けるだけ。原費/S-V/既各群開始見積り保持、追加gross0。source段はMain2（Morning wrapperと新helper）/独立Test12のGJF-CS/逆変換・owner/trace。通常段はpure Main3/Reason enumのphysical4を明示したRootNullAway/PMD-CS-SB/一source一whole12/CRC/初期化/四counter独立post。実測不足をPASSへ変えない。

本pure12はPT-MDB-CAT341-001～009の分類/型選択の部品根拠だけ。実Morning whole65・20経路への接続・close/wipe/Session失効・DB/原本/同run/同期限/全ownership・新native/CHR/451/元190は別未受入。純関数の結果を実所有や起動許可へ変換しない。PG2852/YKT2359全体は実経路の必要証拠が揃うまでOPEN。
