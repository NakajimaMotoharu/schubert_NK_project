# SSC461 Backup監査ペアのJDBC所有と単体仕様

WBS-F02-a、P017-06、NK-BAT-001、SS311/332/341、SSC061/063/134/461、BUG3233、YKT2680/2683。BackupStepRepository.inspectのSQL例外1境界を上位adapterに接続し、所有行と文は当Repository内の型付きprivate処理で各一度解放。借用Connection、SQLと値、監査readback、先後と例外優先は維持。実ファイル・権限・実Backupは起動しない。

原仕様699のBKPPORT001～010を全件、現Test sourceそのままで選択する。手書き固定SQL・bind・状態値、再送時刻／2回目UPDATEなし、欠落／不整合、null・各JDBC faultの本人性、行→文と借用後条件が独立の期待値。元ISSCOMP001～003の外側MorningDatabaseSession依存はclosed profileを超えるため保留し、元全13を現在の合格に使わない。

同一固定Java25 sourceの厳格NullAway・SpotBugs・Checkstyle・PMD、独立JVM terminal/全XML・物理CRC・未フィルタcoverage、公開ABIと実対象methodの確認。原Web/Root/DB/署名・native仮説には入らない。coverage不足や実経路を別条件として保持する。
