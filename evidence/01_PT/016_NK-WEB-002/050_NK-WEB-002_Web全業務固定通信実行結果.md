# Web全業務固定通信 実行結果（限定・未正式）

2026-10-03 04:39:49 JST、dev-foundationのHEAD d90a1f34f9ffc53b17a4b0d1a576840012f92c3d＋WIP。個々source/testのSHAは[manifest](evidence/provisional/PG433-wire-selected-v4/manifest.json)へ記録。未commit変更をHEADで試験済と偽装しない。source固定後の全回帰は次のPG433 fullで別に採取する。

JDK25.0.4/Maven3.9.12/Node24.19.0/Linux、JaCoCo0.8.15/SpotBugs4.10.4.0。選択72PT/10suite/F/E/S=0、全6 compile/format/null解析・SpotBugs0、command exit0/70秒。新PT-WEB-S3WIRE001～008（8JUnit内に18全byte/72誤capability/複数code/180並行を含む）、既存Scenario/Music/Animation/Log各8、Protocol8/Storage8/Bootstrap7/API5/Batch4を実行。新facade5はline/method/class missed0、branch0/0（条件分岐は既存shared transportへ委譲、全体100%の主張ではない）。既存cumulative execは新正式runへ流用しない。

独立期待値はUI232 Header、UI234 Logout、UI235 descriptor、UI236 Question/Notification/Userのbyte開始/幅・fillerと固定UTC→JST値から手作成。QSBはA、他S、request/response別UUID・context/correlation、正常0000/0200の型値、全byte消去/保留0、同token新Message、未知Error同一性を確認。NTD誤B0は明示拒否canaryを追加し、正本のBspaceを守る。

途中不合格は保全: v1 Storage no-tests（既存BUG524再発）、v2 新assert accessor compile2件（BUG545/YKT389）、v3 NTD error B/容量16 fixture3error（BUG546/YKT390）。Production拒否契約を緩めず実signature/正本filler/容量12へ是正、v4 fresh選択で全対象を再試験。まだ全6 fresh/full/source固定/正式gate前なので台帳の完了日は未設定。

生log WorkPG379/pg433-wire-selected-v4.log SHA256 `27c7dcc1c82d8a042abfee7715cbed8615f92b6ccf03de94e9cc8160c6a3b0c5`。sanitized JUnit10/XMLとmanifestの各hashを保存、manifest SHA256 `0e8dacaeb79c14478b9db3c97a4223b60b01cca993cb999aa040782f4e29b51b`。実credential/session/token/password/key/DB dumpは含まない。HTTP controller/template/full Web assembly、同Root ordinary native coverage、Caddy/DONE/CHR/53scope/100%は未受入、正式run24/1964PTを更新しない。
