# 1279 JMS所有五sourceの個別静的点検

source870/SS312321342343354/SSC311・PG-D457458/BUG1537/YKT1297、1273/1276～1278。1462群の品質確認内（費用二重加算0）。五MainのPMD99診断をsource/座標/span/個別役割で確認し、旧631のうちowner変更により自動移植できない8を新点検する。未確認を受入にしない。ArtemisReplyConsumers.closedのvolatileは全参照lock保護で必要性未確認のため保留し、他三volatileのready読取可視性とは区別する。

対象=三consumerの取得alias/consumerのcontext所有、callback committed fatal/未確定rollback停止/確認済rollback再送、startup通知失敗・close複合/同一Throwable、API group容量3/逆順全close/fatal保持、Web factory設定保護/返却所有移譲・既open credential消去/固定例外・live close再試行。各class/method/rule/具体的line単位で理由・正常境界null例外並行再送の適用性、独立TestID/当元XMLをjoinし、JVM順序/資源後条件と一緒に記録する。注入TestのError tableやsame object期待をProductionで計算しない。

追加静的commandは `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg6094_jms_current_catch_facts.py` と同6096。既SourceCatchContextInventory/SourceReferenceIdentityInventoryはJava25のparse/analyze、`-proc:none/-implicit:none`、Main851だけの固定mirror/当元1667byte・BOM固定third-party classpathで型を解決する。工具独立fixture/工具compileだけでProductionをinvokeせず、通常PT PASS/実測coverage追加0、実VM/current/Root/原本/failed-cohort/intent/permit操作0。拒否代替の完成数にも加点しない。

source/catch type/identity lhs/rhs symbolの事実だけで分類を確定せず、各catchの通知/rollback/cleanup/再throw/固定wrapやhandlerの境界を個別に反証点検する。古いpure Error rethrow理由は流用しない。必要3985真正0後、未変更ownerは源/全byte/診断列/独立Test全文不変で再認証、変更ownerは明示fresh理由と元XMLへ接続する。残F03/coverage/native/CHR/451/trace/正式は別未完、静的理由を実RootDONE・DB不変・実解放へ置き換えない。
