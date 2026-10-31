# BatchRun 現48診断・所有八scopeレビュー 仕様

2026-10-31 / PG-D980 / WBS-F03（関連P017-02は追加費0）/ event3395。
着手見積り低0.5/標準2/高5共有pp、cap10、開始used51/reset1793774153。専有費・実tokenはnull。原見積り/受入数は変更しない。

現Production6b53efeec87f3ec36a840dd8e7759656cb4aee5cのBatchRunRepository全502行とJdbcResourceFailures全26行を読む。保存15938の未接続929件のうち当Source48件を対象とし、SS332/SSC063の借用transaction、所有Statement/ResultSetの直接close、SQL/unknown優先順位を個別八scopeへ追跡する。関連RD DAT009/OPS009、UI251、SS331§8.3/332/341、BAT138～153。先行957/1266の目的は参考にするが、別sourceの実PT/coverage/型解析を新sourceへ移植しない。先行索引BatchRunRepositoryを実行し11件の保存結果を確認済み。

対象scopeはfinish(statement)、history(statement/rows)、abandon(statement)、insert(statement/rows)、replayed(statement/rows)。各scopeのalias一、primary catchのRuntimeException/Error二、finally一、cleanup catchのRuntimeException/Error二、計六診断を座標・spanと結ぶ（計48=CloseResource8/汎用catch32/finally8）。null取得はpresentで固定SQL拒否、nonnull資源は同変数を一度直接close、未知failureは同一instanceを再throw、cleanupの置換だけを既helperへ委譲する。借用Connectionのclose/config/commit/rollbackはない。

レビュー判断はMANUAL_PURPOSE_REVIEW_COMPLETE_DYNAMIC_UNQUALIFIEDとし、raw抑制/適用違反数確定/全F03合格には変換しない。八scopeに同じ理由を盲目的に転記せず、個別method/資源/line/primary変数を検証する。型解決・実close回数・SQL後条件・DB所有・nativeは本作業では未検証のまま。既helperの独立68fault試験は保存証跡参照に限り、再実行も新Sourceの八scope合格認定も行わない。

PG16004は公開Main二つ、承認済SS332、固定15938公開queue/manifest、明示site表のみを読み、review/残queue/manifestをnew-only保存する。独立PG16006は別のline/token走査・全ID/multiplicity/hash/八site/理由・境界を照合し、欠落/重複/違うmethod/資源/primary/座標/byte/成功昇格などの変異を拒否する。既Product試験・scanner/compiler・JDBC接続/SQL・DB・Root/cohort・Graph9・VM/外部・私有raw・鍵・intent/permit操作は0。対象不明の拒否を探索せずHOLDも解除しない。

実行commandはchecked entryで各新工具を一度起動。管理検査の成功をPT PASS/coverageへ加算しない。既registry2094/278・473Source/654physical・四252/366・正式1964/53・歴史17/190・工数null・QA051final・全451/HOLDを保持し、WBS正本には本群で変更しない。
