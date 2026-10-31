# API借用・所有 四Source十三site 用途確認仕様

2026-10-31/PG-D1017、主・計測WBS-F03、event3482。選定前読取と後続索引を終え、追加照合着手前見積0.5/2/5共有pp、cap10を固定。HEADa39da9787012a7f7be8859279c89f26d9ac49601（push52914真正0）、Production6b53/normal14216不変更、fresh共有used58/rem42/reset1793774153/短期null/券0。実N/T・専有費・工数率null、既予算不変更。

全MainはQuestionCommandService367行、JdbcSyncRequestProcessor63行、WebLogIngestService140行、QuestionQueryRepository441行の計1011行。先行索引6/10/2/7、1439・2763/64・原SS312 SSC329/330、SS324/331/332/351を参照。Command取消/論理削除の借用write transaction、Queryの借用read-only transactionと業務拒否、SyncとLogの所有transaction/TWR/rollback/fatal分類の直接Source用途を確認する。Graph9/実DB/JMS/所有close成功・Throwable循環有限性の実証へ拡張しない。

原13253 XML/findings・全属性/診断・現Source SHAに全13warning（9catch clause）を結合し、独立検証でUTF8 byte座標・除去集合/残queue・metadata負例を確認する。Commandのescapeは後方362行で対象196/280行より後。対象末尾までのraw prefixを既16345のUTF8 adapterへ渡し、prefix内escape/CR/NUL等は既guardで拒否する。後方escapeで前方座標が変わらない限定を明示し、全文Java変換/AST証明としない。QuestionSubmission/Workerは今回非選択、RootFailedStartRecovery本文はアクセスしない。

Command2＋Sync5＋Log4＋Query2=13warning。参照1171＋用途208=1379/1491、残112を目標とするが、確認前に完了扱いしない。warning/文字列metadata検査をJUnit件数へ混ぜず、first-ever理由数・actualViolationCountはnull、raw抑制0/PT免除false。元whole HOLDの抽出/別fixture/元成功再演0。16356/16358のcommand・真正終了・path/hash・残存リスクは3167へ記録。現2174/296・四262/383・正式1964/53・歴史17/190・QA051final/全HOLDを維持する。
