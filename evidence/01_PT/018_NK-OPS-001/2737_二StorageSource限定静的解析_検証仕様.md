# 2737 二Storage Source限定 PMD・Checkstyle 検証仕様

## 当18行の根拠レビュー（同一群・元見積不変更）

14665/14667はXML独立post14666を起点に原18occurrenceを保持し、ResourceScopeの14固有source span/変数役割・origin/main SS333 SSC063/308・真正26PTへ一件ずつjoinする。重複4occurrenceを消さない。理由は設計上のcleanup境界・複合優先順位であり、raw qualityGateExit1/actualApplicableViolations null/currentWholeJoinPending trueを維持する。理由レビューをPMD raw0/実行PT/coverage/whole F03 PASSへ変換せず、最終global joinは別依存。source-token/role/PT偽参照・raw削除・gate昇格など十metadata反例を独立検査する。Product/analyzer再演0、Source/rules/suppression変更0。

source6b53efeec87f3ec36a840dd8e7759656cb4aee5c/dev-foundation/Gitfd11f00961163e875e8b536b56524742ce330aab、PG-D933/WBS-F03、関連P00307/08追加費0。対象はResourceScope(2733/34)・ServiceCredentialId(2731/32)の全Main二fileだけ。両Sourceの全body/独立元whole/全physical counterは既確認だが、当sourceのこの二MainのPMD/CS sliceは未実施なので必要な追加品質検証とする。元全1843Main SpotBugs14222/24は同source同byteの成功を保持して再演しない。

PT-OPS-STATIC-S2-01：normal14216/source6b53の全input/六Jar/1843Main1978Testclass/外部依存とauxのstale project Jar排除・重複producer同byteを固定する。旧14226 beginとTool/rules/JDK/dependency/testbyte hashesが完全一致することを確認。source-listはnormal snapshot内の二Mainだけ、worktree source同hash。対象追加やMain実行を伴わない。
PT-OPS-STATIC-S2-02：PMD7.28.0(record rule1298固定修正版)/Checkstyle14.3.0/JDK25.0.4・既存rulesそのまま。自己新SLOTで二analyzerだけ各180秒、rawXML/findings/actualexit/processing errorsを保存。PMD 0/4やCS actual codeを保持し、解析完走と品質PASSを区別する。raw0を仮定せず、未知rowは適用性null/未分類のまま残す。
PT-OPS-STATIC-S2-03：独立14666は返却XMLから全row/path/hash/rule/位置・countを再構成しrawJSON/exit/log hashesと照合。sourceCount2/Main2/Test0、全input/runtime/toolchain不変、processing0/同byteを確認。source/scope/count/bool/quality/raw削除/Product昇格等のmetadata反例を拒否。処理エラーや未実行は合格にしない。

群event3129予定 .5/2/4pp cap10、primaryF03・componentP00307/08追加0、実0確認後14664→14666。rawの実仕様違反が確認されたら修正前BUG/必要YKT等を起票、単なるrule警告を自動的に障害/非該当へ確定しない。保持rawに行単位の具体code/独立PT/設計根拠を付ける場合も抑制/設定緩和/手動0化をしない。

全操作は公開Source・normal class/Jar/tool metadataの読取と自己tool証跡出力だけ。Product PT/JVM/Root/VM/DB/HTTP/鍵/native/私有raw実行0（analyzer JVMは工具）。Source/Test/POM/rule/installedtool変更0・旧解析の確認再演0。結果2738に各command/時刻/環境/source/input/hash/実際/未分類・BUGを保存、正式/工数null/QA051final/全F03-451/HOLD維持。全体品質判定や新leaf受入へ当二fileだけで昇格しない。
