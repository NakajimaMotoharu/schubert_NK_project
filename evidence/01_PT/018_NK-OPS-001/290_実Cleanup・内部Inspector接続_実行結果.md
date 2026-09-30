# 290 実Cleanup・内部Inspector接続 実行結果（暫定・未受入）

仕様289/SS341§7.3・343§6.17/SSC119。PG389のSource `24ed4e271e6e10d47302103969050f3d3f57e05e`（実装bab5bad44＋全回帰command固定）で、選択203PT/4module static0、2026-09-30 17:16:34 JSTを確認。共通CLOCK_MONOTONIC frame/golden、Root deadline IO/null、2Root親、普通Inspector自己＋別shell MainPIDのkernel/manager二回一致、DB DELETE/commit境界、型付き0/10・Inspector明示stop→全終端→reacquire→DB→env/owner→intentの順序をhost独立fixtureで試験。全6回帰/同byte nativeは実行中又は後続、未網羅100%を認定しない。Source六回帰manifestで結果を確定する。

## 隔離VMの接続前環境

実行command: `sudo -n python3 /home/ubuntu/pg389_provision_inspector.py`。作業領域script SHA256 `7d5e16c83a8070758eaf04d14cdfaf1cc157d4c5959f7d42add0ee5bfa729b83`、終了code0。Ubuntu26.04/PG18.6、instance固定 `pgpt-r2-20260927-01`。既存M/A inode/Root0600をNOFOLLOW保持・非blocking flock、current INVALID、固定9Unit inactive/failed・MainPID/ControlPID0、既存OS accountなし／DB専用roleのpassword未設定を先行確認し、new-only構築。既存file/account/passwordがあれば上書きせず停止するscript。今回再実行は行わない。

- `schubert-inbox-inspector`: UID991/GID976、group976/982/986（専用primary、schubert-read、schubert）を独立`id`で確認。nologin/nonexistent home、API/Web group継承なし。
- `/etc/schubert-nk/inbox-inspector.env`: Root:schubert0640、DB5432/schubert_nk・fixture version v1。既存envなしから新規作成。
- `db-inbox-inspector`: Root:Root0600、新規ランダム値をVM内生成し専用DB roleへ設定。値・hash・DB dumpはGitへ出さない。DB role login=true/superuser・createdb・createrole=falseを独立SQLで確認。鍵2種の既存Root0600は変更しない。
- Source Unit/ownerはまだ配布・起動していない。実VM releaseはPG387、Inspector inactive/dead/PID0、permit0。これらの環境事実をCINSPECT実受入へ読み替えない。

provision固定receipt SHA256 `b5d47c480ca49062030b582d9413943f226bd0d0ec82c603517af54c158281f5`、独立metadata/role/Unit/current観測log SHA256 `e2baea369c6c0d0d75e1089b1bcf9ee1106c4c495740dc28524ee06f58dfeeed`（作業領域PG379配下）。原本run/cutoff・旧DB12行・4file・復旧点・秘密鍵は保持。installerは通常Unit起動・release切替・permit/approval発行を行わない。

## 残る実受入

CEXEC001～003/CINSPECT001～004の真正外部経路はNOT-RUN。Root request publisherの閉鎖owner型→同Cleanup DB/advisory内の6step→実Inspector→Transfer→親再取得/独立全DB再読→request/owner/intent退役を結線する。Backup真FAILED時の6SKIP・Inspector/DELETE0とTransfer実行、Artemis Requires下Cleanup再実行0、Expiry/prior監査・正規issuerは別残件。S1実30分UNKNOWN、native100%・API/Web業務起動/CHR・正式全scopeは未完のまま、工程完了を宣言しない。
