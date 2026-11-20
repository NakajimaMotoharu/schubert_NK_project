# 期限切れ監査更新で更新と資源解放が同一例外を返す場合

NK-BAT-001、OPS-009、DAT-009、UI251、SS332 SSC310、SS341、WBS-P017-11、BUG-3408／YKT-2732。

**EXPPORT-J011**。`ExpiryAuditRepository.stage` と `finish` の各経路で、借用Connectionの事前参照を成功させ、確保した文の更新とcloseが同じ例外インスタンスを返す。合成のLinkageError、SQLExceptionを各経路で別々に用意する。期待値はJava 25のtry-with-resourcesの一次・二次例外規則、既設計のError保持およびSQL固定変換から定める。Errorは元と同一で抑制なし。SQLは原因・抑制を持たないBatchRepositoryExceptionとなり、入力のSQLExceptionも抑制なし。事前参照と更新の順で各文を一回取得・解放し、事後参照を実施しない。借用Connectionの解放呼び出しはfixtureが拒否する。

Java 25、既使用の借用proxy、PG40712で固定された補助classの個別抽出だけで試験する。実DB、実削除、並行・再送、および既30試験は今回の実行対象外。新規試験の実行環境、command、終了コード、入力hash、結果はPG40858のmanifestを参照する。全体coverage・451・正式受入には別途同一sourceの証拠が必要。
