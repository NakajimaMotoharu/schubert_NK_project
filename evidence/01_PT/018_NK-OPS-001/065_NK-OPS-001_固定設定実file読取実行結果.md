# NK-OPS-001 固定設定実file読取実行結果

PG275/PT-OPS-CFGFILE-001～007。2026-09-25、Java25.0.4/Maven wrapper、branch `dev-foundation`。選択7PTはfailure/error/skipped0。Storage `clean verify`は92PT全件成功、Production instruction/line/method/class/branch coverage100%、SpotBugs0、exit0。探索段階の欠落file Reason不一致はBUG-254、coverage不足はBUG-255として修正前起票済み。探索結果を正式合格へ算入しない。

正式試行`PT-WEB-20260925-12`/source`2caa43a43`は全reactor `clean verify`でexit0だが、018の厳密なinstruction missed=0で新classの本番入口に2命令未到達を検出し収集exit1。部分008証跡は`stash@{0}`へ保全し、run12を正式認定しない。BUG-255範囲内で本番固定instance factory＋不変instance読取へ変え、Storage全92PT・instruction/line/method/class/branch missed0・SpotBugs0の探索再試験が成功。正式な別run、対象commit、日時・command、全module結果、manifest/hashは未実施・未確定。全reactor/収集器/負canaryが完了するまで本Programの正式PT合格を宣言しない。入力は公開非秘密fixtureだけで、credential/token/raw sessionは保存しない。外部process・実Linux account/ACL/filesystem・DB/JMS・実NK CHRとIT/STは未認定。
