# 2925 公開値四whole十八・現source限定PT仕様

source6b53/normal14216/current1810固定。四whole Test全18と対象六Main・全initializer/helperを全文確認し、Mainは元baseline、Test担当はUNKNOWNを保持する。群3313主WBS-P011-01/関連P012-02・P004-04・P018-09、元一群見積1/3/8pp固定、component追加予算0・配賦不明null。直前Hasher3群とは別試験、両群のmetadataは一度だけ結合し共通費は前群に含め二重加算0。Main/Test/元SS・新cohort非重複/全physical closureをpinし、原Test/Mainを変更しない。

| 原whole / Program / 主対象 | 関連仕様・独立期待値・観点 |
|---|---|
| InspectorSettingsTest3 / NK-DAT-001 / InspectorSettings | PT-DB-INBOX209～211、SS343§6.7/352、QA046/SSC049。絶対正規化path/root拒否・canonical loopback JDBC URL/port1..65535/DB名・version1..16の不変集合/null/赤字化。固定文字列のInspectorDatabaseConnections.databaseNameだけをhelper利用、constructor/open/DB/鍵取得/Graphは呼ばない |
| RequestLogDetailsTest2 / NK-MSG-002 / RequestLogDetails | PT-IDEM012、SS351§3.3/SSC008。4固定key、Roleはwire別fieldからだけ・JSON重複/未知/null/型/末尾/1024UTF8byte境界を固定literal JSONで照合、StringReaderメモリだけ |
| QuestionReceiptIdTest8 / NK-QST-001 / QuestionReceiptId・Generator | PT-QST-RID001～008、UI224/236/SS312331。独立alphabet32字/全26位置・ASCII外/Unicode/長さ、前後literal、26回random失敗/範囲外/null、64callの16cycle×4・計1664draw、私有lock、public値のequals/赤字化 |
| StubAnswerProviderTest5 / NK-ASY-001 / StubAnswerProvider・AnswerResult | PT-ASY-STB001～005、SS312§8.1、時計2literal/空回答/1call1clock、null/clock例外identity非成功、64独立時刻/equals/赤字化。外部Provider/DB/JMS更新は呼ばない |

Receiptの標準SecureRandomは公開IDのentropyだけで実session/token/key発行ではない。crypto=true/CSPRNG_PUBLIC_RECEIPT_IDENTIFIER_ONLY_NO_KEYS、actualSecretKeys/actualCredentialValues/actualAuthenticationOrSessionIssued=falseを明記する。固定random portの独立alphabet数学検算/元literalと標準factoryの形式assertを分離し、DB唯一性/再送SQL成功をこの試験から認定しない。Testの固定生成故障は単純例外のidentityだけ、循環graph/classifierの実行/保留Test抽出なし。

原Test二件のFiles操作は新SLOTのtarget/question-receipt-traces/PT-QST-RID008.txtとtarget/question-stub-traces/PT-ASY-STB005.txtへの公開固定文字列だけ。private原本/DB/Backup/鍵/既存証跡を読取・上書きしない。ファイル内容/全hashを先行独立literalへ一致させ、元runのpublic-test-output.safe.jsonとコピーへ保存する。productFileOperations/actualFilesOpenedByProduct=false、testOwnNewSlotPublicEvidenceWrites=trueを混同しない。

command：python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15458_public_value_eighteen_pt.py。raw/専用15460post draftは事前lint0、元terminaltrue0/実hash取得後にpostを初回実行する。全Input/snapshot/6Jar/Test/launcher/reporter、180秒上限・実XML/FES/OS-JDKprefix/一sessionCRCを照合。全六Source六Codeを個別完全class名でpassive測定し、counter未達をそのまま記録・手動除外/旧exec unionなし。helper Sourceは当target countersで受入へ加算しない。既読・既資格のpassive exec readerをruntime再利用し、元execに四固定held classのtrue probe無しを確認（Product classをload/invokeせず、全1975HOLD解除を意味しない）。

別独立15462は全18TestID/元oracle/SS正本/全JarCode/counter/owner/公固定output/flags/stage/hashを確認、意味反例で偽加算を拒否する。結果2926、実日時/JDK25.0.4/OS/branch/source/command/exit/全hash/coverageは元manifest。MorningParentBudget原wholeはnative実行を含むためHOLDのまま・安全部抽出0、他未読wholeへ拡大0。正式1964/53・歴史17/190・工数null/QA051final/全HOLD不変。
