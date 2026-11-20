# 設計書の公開・branch運用

- 設計書の閲覧用正本は`origin/main`の`documents/100_RD`、`documents/200_UI`、`documents/300_SS`。詳細は[README](README.md#設計書の正本branch修正完了時の反映)を参照する。
- 設計修正の記述確定、必要な上位承認、関連設計への横断反映、文書整合確認が終わったら、その作業の中で設計書と必要な設計変更台帳をmainへ反映し、remoteを確認する。PG/PT全体や実装branch全体の完了まで待たない。この反映は利用者が継続的に指示しており、毎回の再承認は不要。
- 未承認案・調査中draftは確定設計と分ける。設計反映を実装・PT・工程完了として扱わず、台帳の実装/PT未完了状態を維持する。
- 実装が未受入ならmain起点の隔離worktree/branchで設計関連ファイルだけを反映する。未受入のコード・配備設定・工具・証跡をまとめてmainへmergeしない。実施worktreeの既存変更・stash・processは保全する。
- source commit、main反映commit、対象文書、残る未確定事項を記録する。mainの並行更新はfetchして照合し、force push・保護規則迂回はしない。push/merge/remote確認が未完なら反映済みと報告しない。
- 485または486を変更する手動commitでは、485の全バイトのSHA-256を486の `inventorySha256` に反映し、必要なファイルをstageしてから `python3 -B tools/quality/wbs_index_binding.py` を実行する。stage済みの二文書が一致したことを確認してからcommitする。
