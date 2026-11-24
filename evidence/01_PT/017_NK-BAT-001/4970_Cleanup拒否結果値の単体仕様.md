# Cleanup拒否結果値の単体仕様

NK-BAT-001／OPS-009、UI251、SS332と341。WBS-P004-05/2。CleanupTerminalRepositoryの公開値RejectedEntryとRejectedSnapshotのコンストラクタを合成フィクスチャで検証する。

| Test ID | 入力と独立期待値 |
|---|---|
| PT-BAT-REJVAL001 | 固定7位置。位置0の終了成功にID21・135 bytes・固定終了時刻。位置2の走行中はID22・結果なし・終了なし。位置5は固定のバックアップ未成立によるskip。1・3・4・6はレコードなし。snapshotは入力変更の影響を受けず、診断は固定マスキング。 |
| PT-BAT-REJVAL002 | 通知行を質問位置へ置く、別runの行を置く、通知／質問が同一IDを使う。各不整合は独立に拒否し、診断を固定。 |
| PT-BAT-REJVAL003 | 非CleanupのBackup行、終了と結果の有無不一致、開始前終了、非skip行にskip結果を与える。各入力を独立に拒否。 |
| PT-BAT-REJVAL004 | 7未満幅、runなし、slot内null、終了Optional欠落は境界で拒否。 |

期待値はSSの7ステップ順、型・終端時刻と保存実体の区別から固定する。接続・Repository生成・readRejected・DB・削除・再開は行わず、実runtimeと原本保全の終了条件は別に扱う。
