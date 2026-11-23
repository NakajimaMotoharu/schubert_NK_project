# Reactor新規証明のcheckout結合

WBS-G09、SS354、PGPT451、BUG-3711、YKT-2911。対象は `tools/quality/pgpt_reactor_junit.py` の新規証明作成と、別入口での保存済み証明の確認。

| Test ID | 入力・操作 | 独立した期待値 |
| --- | --- | --- |
| PT-OPS-G09-JUNIT018 | 専用一時Gitリポジトリの初期commitで原runの記録を作成し、同じbranchに別commitを作る。新規の証明作成を呼ぶ。 | 初期commitと実HEADが異なるため拒否。新規証明ファイルは存在しない。 |
| PT-OPS-G09-JUNIT019 | 同じ初期commitで原レポートのhash取得を完了してから、一時リポジトリのHEADを同じbranch上の別commitへ進める。 | 書込直前に実HEADの変更を検出し拒否。新規証明ファイルは存在しない。 |
| PT-OPS-G09-JUNIT020 | 元のcommitで証明を確定し、同じbranch上で入力の内容を変えずに管理用commitを追加する。既存証明を確認する。 | 元の証明バイトと一致。実行済み結果を新規認定として再計上しない。 |

期待commitはGitが一時リポジトリで作った実オブジェクト。期待ファイルの有無・既存bytesはテストが直接確認する。既存のJUnit報告、Git branch、時刻、異常・重複・元artifact変更の試験も維持する。一時リポジトリと合成レポートを使い、実reactorや稼働環境の証拠は使用しない。対象source、環境、実コマンド、結果と証拠hashはPG43492の実行manifestに記録する。
