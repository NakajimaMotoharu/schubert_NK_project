# 478 再開プロンプト：GPT-6.1 Sol

2026-10-17現行補足：利用者が券あり臨時overrideの失効を明示訂正したため、477冒頭の**通常残10%以下で新規停止**をA/Bとも優先する。今回残5%は保全停止、枠回復だけで自動再開しない。明示再開後もfresh枠>10%、最新456/460/保存job/source/所有を確認し、既成功4972/4968/4970/4976/4980/4982/4988を再演しない。過去の残3/1%・券許可を持ち越さず、PMO毎時監査PAUSED/品質・モデル・scopeは維持する。

2026-10-08更新。実施チャット「PGPT製造・単体テスト開始」でGPT-6.1 Sol / high（高）を選び、Aを全文貼付する。旧9/30ブロックは置換しGit履歴へ保存。reset券を前提にせず開始時fresh枠を確認する。PMOはultraを維持。プロンプト作成だけでは実施チャットを起動しない。

## A. 今回の実行（全文貼付）

```text
Schubert_NKの残PG/PTを、修正版実行計画とWBSに従って再開してください。計画説明・試走・一区切りの報告で終了せず、実装、独立試験、実接続、品質受入を停止条件まで自走してください。PMOの返信待ちは作らないでください。

主実行はGPT-6.1 Sol／high（高）の既承認設定です。指定と実確認を区別し、文面だけで設定変更済みとしないこと。大幅な仕様・工程・モデル・品質変更はPMOへ論点を残し、独立承認済み作業を継続します。

作業tree=/home/mini/codex/project1/work/pgpt-foundation、branch=dev-foundation。documents/400_PGPT/470_PMO/477_GPT61Sol実行計画・再開判定.mdと487_WBS実行計測規約.jsonを読み、479/481/484～486を現行WBS正本、456先頭と460を最新現況/再開順として使ってください。旧482は比較履歴固定です。元依頼・承認済RD/UI/SS/DIF・451品質条件・AGENTS.mdを維持してください。資料は必要箇所だけ読み、全履歴/成功ログを反復調査しないこと。

最初にfresh利用枠を照会し、Git status/最新HEAD/既存変更を確認してください。古いHEADへresetせず、stash/Scenario/Current baseline/原本DB・Backup・旧失敗証跡を保全します。10/7のVM状態は履歴なので、実施側が現在VM/Unit/kernel/process/所有/署名/source/epoch/原値を再認証し、二重起動を防いでください。

保存点はProduction a2e98ce9e96c42425921e3686e8ae7a94bff9e6c／PG495／schema028。PG495 host3411PT/510suite/静的6module0は限定成功、PG498は当sourceのreadonly/pending code-only限定2段階です。PG499はBUG808/YKT577工具pin不一致の是正後、host28assertだけ済み、実VM再試験未実行です。最新成果があればそれへ追随し、a2へ巻き戻さないこと。

最初の実経路は、現在所有とPG498after参照の再認証→python3 -B tools/quality/vm/050_s1/pg499_runtime_retirement_test.py→是正refsを別new-only TOOLS v2/compile-v3/native-v2へ固定→新M/A・専用DB・十RefでPG499正規runtime退役/dirsync/reload/全新scope正常→別fresh一回用通常resume→durable一回予約/observer/外部Morning→元30分で同Root/API所有を保つWeb/Caddyと真正DONE→逆順ownedTERM/native同source、です。旧PG492 wrappers/pg499 v1を直接再実行せず、旧143/UNKNOWNを正常化しないこと。続いて依存順で残製造・CHR・全coverage・正式gate・引継ぎまで進めてください。

G13.07初期要求/担当/TestID/独立oracle joinを先行し、領域別照合を各対象着手前、最終release差分を最後に行います。初期WBS190ID/83子/実作業leaf251＋予備1、残見積り低90.90/標準269.80/高642.60週次枠ppは未較正です。36共有classの共通製造/PT費は主担当のみ、P019-02参照は0費用、親子/共通費の二重計上は禁止。scope不足は版と根拠を保存して追加します。depsは受入終了条件で、必要な早期調査/captureまで禁じません。

counter閉鎖92/未網羅23/非Java7/参照1は技術測定です。個別criteria・独立oracle・同source証跡・終了依存まで揃わずACCEPTEDにしないこと。旧89→92は分類変更で新成果0。正式PT-WEB-20260925-24/1964PT/53scopeと限定成果を分け、工数率不明を旧48.3%や試験件数で埋めません。QA051比較範囲は保留し、独立Log/replayは継続可能、L01最終PASSへ読み替えません。

同時に進める新規経路は一つ。変更群ごとに独立正常/境界/null/異常/競合/再送/修正前再現と必要YKTを閉じます。変更module/影響suiteを選び、必要全回帰はtriggerを記録して実施。同source成功全回帰の無根拠反復は避けます。451のJava四counter各100%・適用JS100%・静的0・CHR/DIF・秘密/trace・同source正式条件は維持し、除外/人工到達/Production生成期待値で合格を作らないこと。Backup失敗時の所定SKIPPED/起動継続など承認済分岐も維持します。確定RD/UI/SSは設計だけmainへ当作業中に反映します。

今回から487のeventTemplateに従い、/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonlへ開始・作業群開始・意味ある区切り・失敗/再試行・受入・停止/全完了を追記してください。長時間job中も約1時間に一度、既知の状態を保存します。着手前leaf見積りを固定し、WBS群/source/run/達成criteria/未達/再開/scope差/実経路/coverage/正式差/失敗原因/実時間と待ち時間/残見積り/次command、利用枠前後と取得時刻/resetを残してください。開始予算と現行残予算を分け、親子/共有費を二重加算しないこと。

実tokenは数値usage増分だけを採取します。487記載のpmo_usage_increment.pyを初回init（過去本文は読まず末尾から）し、作業群区切りでpollしてmeasurementIdをeventに紐付けます。N=input−cached_input+output、T=input+output、reasoningは出力内数。親/許可レビュー/PMOを分離し、response重複・圧縮分・欠測/flush遅延を記録します。数値usageが取得不能ならN/T=null＋理由。token_count差やquota割合からtokenを換算しません。reset跨ぎは別窓、他chat/PMO並走が不明なら共有消費のまま、個別actualSpentPp=nullとし均等配賦しません。標準超過又は追加5ppで自己点検/残見積り、同原因反復や約20pp実経路証拠なしなら既方針内の限定是正を行い継続してください。

PMOの約毎時診断は別に動きます。実施側は監査専用hourly-monitorを編集せず、返信依頼/PMO待ちを作りません。WBS更新前後にpython3 -B tools/quality/wbs_progress_audit.pyを実施し、旧比較確認は必要時/最終時に--baseline-v1。管理検査はProduction PTへ加点0。最新456/460、WBS証跡、eventを意味ある単位で永続保存しGit pushまで確認してください。

週次又は該当短期残10%以下で新規実装を止め、必要検証・差分・証跡・計測cursor・source/所有/job・次commandを保全し、5%付近までに停止します。枠不明はfresh UIでも確認し、両方不明なら新規実装なし。自動reset券消費/追加課金/枠回復だけで無指示再開はしません。その他の停止はPG/PT全完了、利用者停止、実環境継続不能、不可欠な外部入力待ちで独立作業も尽きた場合です。通常報告/commit/レビュー/小受入で実行を終了しないでください。中断時は最後のeventと456/460に具体的な次commandを残してください。
```

## B. アプリ中断・枠停止後の復帰（全文貼付）

```text
Schubert_NKのPG/PTを保存点から継続してください。/home/mini/codex/project1/work/pgpt-foundation/documents/400_PGPT/470_PMO/478_再開プロンプト_GPT61Sol.md のAを今回の指示として適用し、477/487、最新456先頭・460・最後の計測event/cursorを確認してください。fresh枠>10%と現在HEAD/dirty・source・所有/job/署名・保全原値を再認証してから、最後に保存された未実行の次commandへ進んでください。新しい成果を巻き戻さず、配備/退役/起動/試験を二重発行しないこと。tokenの既集計record/窓を再加算せず、reset跨ぎや中断中の欠測は分けます。モデル/品質/10・5保全は維持し、一区切りやPMO待ちで止めず残PG/PTへ自走してください。利用者の停止/承認待ちが別途残る場合は解除せず、承認済み独立作業を継続します。
```

## C. PMOの軽微是正

毎時診断は具体的証拠がある時だけ「観測根拠／承認済み計画内で修正する点／次に得る受入証拠／現job・source・所有の保全」を一度伝える。対象モデルを上書きせず、既対応・単なる照会・返信依頼を送らない。大幅な変更は利用者判断へ提示する。
