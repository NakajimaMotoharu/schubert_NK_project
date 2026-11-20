# CLNPORT010 CleanupStepの単独SQL例外

NK-BAT-001、P017-07.01。DAT009、OPS009、UI251、SS331 §3.14・SS332 SSC063・SS341、YKT-2359。既借用JDBC fixtureに、準備、query、列取得、row.close、statement.closeのいずれか一つで合成SQLExceptionを返す。cause、suppressed、nextの先から到達する元Errorを独立した同一インスタンスとして固定する。5箇所×3形を1 Test IDとする。

期待は元Errorの同一性と追加suppressed 0、最初の参照確認1回、失敗後の再照合なし。削除側のcloseは準備失敗でなし、query失敗でstatementのみ、他ではrow→statementを各1回。各回で全取得資源の解放を確認する。実DB、実削除、管理権限、Rootは対象外。Java25の隔離実行とscopeをmanifestに記録する。
