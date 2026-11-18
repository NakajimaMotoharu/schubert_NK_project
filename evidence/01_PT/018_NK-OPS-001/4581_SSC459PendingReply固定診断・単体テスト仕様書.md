# SSC-459 PendingReply一般診断の単体テスト仕様書

NK-MSG-001、UI231/232、SS321の相関・期限・一回終端とSS351 §12、WBS-P005-02／P018-10.03、BUG-3229／YKT-2678。PendingReplyとReplyCorrelationRegistryの元PT-JMS-008全7件（登録上限・重複、不正値、期限・遅延、取消、有限並行・一回勝者、borrowed viewとbody所有を元の期待値で確認）。旧wholeの試験コード・期待値は維持。

PT-JMS-008-DIAG001／PT-P01810-CATALOG-038は二つの合成IDと締切で各getterの独立値を確認し、未完了の両方に固定診断を要求する。双方を独立に成功と失敗へ終端させて、成功bodyの固定byteと失敗状態、終端後の固定同一診断を確認する。既Registerとの閉じたJDK25 fixtureのみ。実JMS／非所有process／実ユーザーや時刻／実ログの条件は別の未実証。全試験および四counter/独立証拠は同sourceのmanifestへ記録する。
