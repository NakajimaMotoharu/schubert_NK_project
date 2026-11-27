# schubert NK project

schubert現行システムを、利用者向けの主要挙動を維持しながら再構築するプロジェクトである。

## PGPTの作業資料を読むとき

製品コードと単体テストは `src/`、要件と設計は `documents/100_RD/`・`200_UI/`・`300_SS/` にあります。12月6日に向けた作業順と判定条件は [11月26日の回復計画](documents/400_PGPT/470_PMO/更新判断-20261207/11月26日回復計画/) から確認できます。試験実績を調べるときは、対象のWBS行に記載された実行IDとマニフェストから必要な証跡を選んでください。

整理前のファイルはコミット `dd4cffb505be7189e37adba5d7b034068b16f282` に残っています。以前の作業を検証するときは、`git show dd4cffb505be7189e37adba5d7b034068b16f282:"対象パス"` で単独のファイルを読めます。当時のディレクトリ一式が必要な場合は `git archive dd4cffb505be7189e37adba5d7b034068b16f282 -- "対象ディレクトリ" | tar -x -C "復元先"` で空のディレクトリに展開できます。

## 文書区分

- `documents/100_RD`: 要件定義（最正本）
- `documents/200_UI`: 基本設計
- `documents/300_SS`: 詳細設計
- `documents/900_OTHER/910_台帳`: QAおよび後工程フィードバック・修正管理台帳

要件定義中の調査メモや未整理資料は、プロジェクト外の`/home/mini/codex/project1/work`で管理する。
合意済み要件および明示的に未決とした事項だけを`100_RD`へ記録する。

## 版管理

本プロジェクトのプログラム、設定雛形、スクリプト、Markdown文書をGit管理対象とする。
実行時ログ、秘密情報、ビルド成果物および大容量マスタ素材はGit管理対象外とする。

## 設計書の正本branch・修正完了時の反映

**利用者が閲覧する最新の確定設計は、常に`origin/main`のRD・UI・SSとする。** 作業branchは修正中のdraftを持つ場所であり、利用者が複数のbranchから正本を探す運用にしない。

- [mainの要件定義（RD）](https://github.com/NakajimaMotoharu/schubert_NK_project/tree/main/documents/100_RD)
- [mainの基本設計（UI）](https://github.com/NakajimaMotoharu/schubert_NK_project/tree/main/documents/200_UI)
- [mainの詳細設計（SS）](https://github.com/NakajimaMotoharu/schubert_NK_project/tree/main/documents/300_SS)

設計修正は、必要なQA/RDF/UIC/SSC起票・承認、関連する設計への横断反映、記述・参照・traceの整合確認が終わった時点で、関連する設計書と設計変更台帳を**同じ作業の中でmainへ反映し、remoteの反映を確認する。** 設計反映をPG/PT全体の完了や実装branch全体のmergeまで先送りしない。利用者への確認を毎回取り直さず、このルールに従って反映する。

対象は`documents/100_RD`、`documents/200_UI`、`documents/300_SS`と、設計変更に必要な911～914等の管理記録である。未承認・調査中の案を確定仕様として公開しない。台帳に未解決事項を残すことはできるが、確定した設計、検討中の案、実装/PT未完了を区別する。設計のmain反映は、実装・試験・工程の完了認定を意味しない。

実装が未受入の場合は、main起点の隔離worktree/branchで設計関連の差分だけをcommit・反映する。実装コード、配備設定、工具、未認定試験証跡をまとめてmainへmergeしない。作業branchのdirty差分や既存stashを破棄・適用せず保全する。mainの並行更新はfetchして照合し、force pushやbranch protectionの迂回は行わない。保護規則がある場合は所定PRを使う。

反映報告にはsource commit、mainの反映commit、対象文書、残る未確定事項を示す。push/mergeやremote照合が失敗した場合は、main反映済みと報告しない。
