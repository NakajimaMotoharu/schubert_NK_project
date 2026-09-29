# 478 再開プロンプト：GPT-6.1 Sol

2026-09-30版。実施チャット「PGPT製造・単体テスト開始」の親を**GPT-6.1 Sol / high（高）**に選択し、利用者がFull reset券を使用した後、Aのブロックを貼付する。券使用の事実から残量を推定せず、開始時の実照会を行う。PMOの本チャットはGPT-6.1 Sol / ultraを維持する。471/472の旧プロンプトを併せて投入しない。

## A. 次回の実行（全文貼付可）

```text
Schubert_NKの残PG/PTを再開してください。計画説明・能力試走で終了せず、実装、独立試験、実PG/PT VMでの接続、正式品質の閉鎖を進め、停止条件まで継続自走してください。

今回の実行指示として、次の現行計画477を読み適用してください。471/472の旧モデル・旧開始基準・旧停滞判定は置き換えます。元PGPT依頼、RD/UI/SS、承認済DIF、451の品質条件は維持します。
/home/mini/codex/project1/work/pgpt-foundation/documents/400_PGPT/470_PMO/477_GPT61Sol実行計画・再開判定.md

【モデル・分担】
親はGPT-6.1 Sol / high（高）を指定します。指定値と実設定を別記し、文面だけで変更済みとせず、確認可能なmetadataで照合してください。機械確認不能だけで停止せず、信頼できる実値が指定と異なる場合は新規実装前に設定差を報告してください。
初回のSSC108・接続図・coverage計画、又は停滞した難契約にはGPT-6.1 Sol / ultraの読み取り補助1名を対象限定で使ってよいです。ultra委任が未対応なら同モデルxhigh、補助tool自体がなければ親が独立資料で点検して進めます。これは補助のモデル・推論指定の明示許可です。
補助には対象資料と失敗事実だけ渡し、接続差分案、所有関係、独立試験、未確定判断を返させてください。共有source、採番、正式runは親が担当し、通常は親＋補助1名まで。補助の再委任・全履歴fork・定型集計へのagent追加はしません。6.1レビュー後も具体的反例が未解決なら、レビュー役をGPT-6 Astra / highへ交代してよいです。xhigh/ultra/Astraを順番に自動投入しません。

【現在地・reset後確認】
作業treeは /home/mini/codex/project1/work/pgpt-foundation、branchはdev-foundation。本計画改訂前HEADは614d8c139で、その後にPMO管理文書commitが続きます。実装停止はb05f96c3e、最新限定sourceは1acade420339eb81f79b717036a69f030ee1949e（PG378）。正式認定はPT-WEB-20260925-24/source858713c0bf310ae8bf62078b0a1cedbce4e968db、1964PT/53scopeのままです。暫定中心48.3%、実API/Web業務起動・実NK CHR-A01/L01未受入です。新しいHEAD/成果があれば巻き戻しません。
Git status/branch/HEAD/remote、必要なfetch/差分、実行中process/job/log、未認定stash、元treeのScenario未追跡3fileとcheckpoint107/219の保全hashを照合してください。既存変更は破棄・混入せず、stash適用/削除/合格算入をしません。新規採番は実台帳末尾から行います。VM/PID/Unitは再確認し、9/29時点の生存記録を現在値としません。
9/30 PMO確認時は共有週次残5%、利用可能Full reset券1枚でした。利用者が券を使ってから再開する予定です。現在の利用枠を実照会し、reset後開始値を新しい計測期間に記録してください。券があること、予定日、文面だけでreset済み/残100%と推定しません。自動券消費・追加課金はしません。
toolで残量を得られなければ利用者の現在UI確認値を使用できます。両方不明、又は残10%以下なら新規実装を始めず読み取り/保全確認を行い、不足事実を報告してください。古いused90/95を新しい期間の開始値として引き継ぎません。

【最初に閉じる経路】
S0: SSC108のroots_sha256/prestart_steps_sha256について、実観測集合、canonical byte/順序、boot/run/activation/Epoch、owner/freshness、SUCCESS/FAILED/SKIPPEDの意味をSS341/342/343と独立goldenへ確定してください。既存methodの接続図、不足値、差分案、host/VM別のcoverage採取方法を短く揃え、一度の限定レビュー後に実装へ進みます。内部技術補足は自走し、真に必要な外部仕様承認だけを所定QAで扱います。
S1: 最初の完成単位は「外部Morning入口→同ownerの実Backup一往復」です。MorningProcessMain→MorningControlScope.executeOwnedEpoch→MorningBackupStageのEpoch付きOwnedWork→MorningBackupUnitCycle→真正Unit/worker→実artifact・step結果/全終端→marker/request後条件を結線してください。現在のMainはread-only exit30、Stageは旧Epochなし経路、CycleはProduction未接続なので、既存部品を使い同じ機能を作り直しません。
同じ親30分budget、M/A、原本DB、INVALID Epochを維持し、隔離PG/PT VMの外部Production入口でfresh Invocation、worker/Unit全終端、実archive/receipt/step結果と後条件を実証してください。UNKNOWN/hard-timeoutのM/A保全、残留marker、次回隔離、再開条件をBUG322/SSC107/YKT254等に沿って独立試験します。--no-block client exit0をworker成功としません。
SS341のBackup失敗時はBUSINESS/TECHNICAL削除SKIPPED・起動継続を維持し、成功を全起動の新しい絶対条件にしません。実際の試行/結果が必要で、未実装・未実行をFAILED/SKIPPEDで代用しません。
S1の後はS2必要Cleanup/Transfer/Artemis/Expiry実結果→SSC108根拠の正規StartupPermitFiles.issue、S3全root gate/proof・FD/held ELF・同PID権限移行exec→API/Web業務ready、S4同じProduction経路の実NK CHR-A01/L01・必要Log再送と正式品質へ進みます。gate迂回、no-op RetirementGate、別PID forkを同PID execとする代用はしません。
新規WIPは同時に一つの接続経路に絞ります。追加依存には接続箇所、根拠SS、必要性、既存部品で不足する理由、終了試験を先に付け、D01～D07の下位条件として管理してください。無関係な一般化・read-only helper・拒否probeだけの反復で経路の完成を先送りしません。

【検証と認定】
451を維持します。Java line/method/class/branch各100%、適用JS coverage100%、独立oracle、境界/null/異常/並行/再送、静的0、修正前BUG・必要YKT、Current baseline、CHR/DIF、秘密/trace、全scope同一source/runが必要です。採取方法不明の未網羅面を増やさず、native外部mainは実プロセスで同一source照合可能なcoverageを採取します。除外追加・人工的呼出し・Productionでexpected生成により数値を合わせません。
開始未網羅B/L/M/CはBootstrap37/11/4/0、API3/32/4/0、Web1/25/4/0、Batch31/365/137/17、Protocol/Storage0です。既存不足、今回追加、今回解消を別表示します。
開発中は変更module/依存・影響suiteを検証し暫定保存します。同じ所有・起動契約の変更群で検証をまとめ、変更契約の独立試験/網羅を閉じてから無関係な機能へ進みます。必要な同じ起動経路のnative接続/採取はS2/S3へ継続できますが、S1の実経路検証だけで正式受入としません。
機能受入、変更後停止、PR/工程gate、POM/共通codec/DDL/security等の横断変更では451所定の全回帰を実施し、横断変更群は他機能へ進む前に全回帰します。全run前にtriggerと受入IDを1行で記録します。個々のhelper/class/commitだけを理由に全正式scopeを毎回再生成せず、必要な試験回数に上限も設けません。
正式run前にNode/toolchain/PATH/format、collector owner/JUnit署名/XML、対象coverage、既存負canary、VM採取を照合し、source/試験/設定/toolsを固定してください。Maven exit0・jacoco:report・限定manifestを正式合格と混同せず、未実行/failed/skipped/flaky/disabled、別source結果、未認定stashを加算しません。
意味ある単位でcommit/pushし、未認定状態を明記します。既存変更破棄・force push・branch protection迂回はせず、PR/mergeは元依頼の権限と完了条件に従います。source等未変更の再開や管理文書だけの今回改訂を理由に全試験を二重実行しません。

【消費・停滞の自己点検】
476のN=未キャッシュ入力＋出力、T=全入力＋出力を親子込みで計測し、推論/cachedを二重加算しません。N/Tは共有枠/料金の公式換算ではなく、不明値は推定で埋めません。既存script/usage増分で集計し、長大rawログを毎command再読・再集計しません。
S1仮予算425～850万N、約170万N又は共有観測約10ppで自己点検してください。これは是正契機であり自動停止上限ではありません。S/R/D closed/reopened/new、未接続箇所、次区間の外部観測1件、実経路source/command/result、coverage残数、全run理由、N/T/used/reset、次commandを短く残します。
約20ppで外部経路の実証が増えなければ、helperやPT増加があっても限定統合レビューと具体的設計修正を必須にします。同じ拒否probeや「次は結線」の再記載では次区間へ進みません。S1上端までに閉じなければ残工数を再算定し、実行可能な差分案・同経路の必須依存へ自走します。PMO介入要はcheckpointへ記録し、返答待ちだけで止まりません。
6.1 Solへの変更だけを理由に476の残工数を割り引きません。最初の受入が閉じた時点で実N/T、再試行原因、初回合格率、接続/coverage達成を保存し、A残りと最終Gの見積り更新材料にしてください。

【継続・停止・中断復帰】
S1/S4/review/通常報告の完了は停止条件ではありません。S4後も460/SS362の残Resource、Logout/User、質問受付/replay/worker/回答/通知、本文/media、残運用/移行/切戻し、最終gateへ継続してください。旧15pp試走・約12pp保全・試走後PMO待ちは適用しません。
残10%以下で新規実装を止め、必要検証・証跡・差分・再開手順を保全し、5%付近までに停止します。正式gateを完遂できなければ未認定として保存します。その他はPG/PT全完了、利用者停止指示、実環境上の継続不能、不可欠な外部入力がなく独立承認済み作業も尽きた場合だけ停止します。
QA045/046は回答済みです。内部判断/SS補足/採番/作業切替で許可を取り直さず、新しい外部仕様承認が不可欠な範囲だけ保留し、独立作業を続けます。VM作業は隔離PG/PT環境で行い、既存test-only Unitの状態/退避/復旧方法を確保してProduction構成を検証します。
短い最新現況は456先頭、変更依存は460、正式証跡はProgram manifestに集約し、全履歴・成功ログ全文の反復読取や最新要約の多文書転記を避けます。中断前にはbranch/HEAD/dirty、S/R/D、正式/暫定source/run、実行中process/job/log、保全hash、未確定事項、次command、枠/計測期間/モデル確認を永続保存します。メモリ内draftや/tmpだけに依存しません。
アプリ中断・context圧縮後は保存した現在地を確認し、適用済み変更・試験・外部操作を二重実行せず再開してください。途中報告は進捗メッセージで行い、停止条件に該当しない限り実行を続けてください。
```

## B. 今回以降の中断から再開

```text
Schubert_NK PGPTを保存した中断地点から再開してください。親はGPT-6.1 Sol / highを指定します。次の477と478 Aを今回の実行指示として継承し、旧471/472・15pp試走・PMO返答待ちへ戻しません。
/home/mini/codex/project1/work/pgpt-foundation/documents/400_PGPT/470_PMO/477_GPT61Sol実行計画・再開判定.md
/home/mini/codex/project1/work/pgpt-foundation/documents/400_PGPT/470_PMO/478_再開プロンプト_GPT61Sol.md
456先頭の短い現況と460の変更依存、Git/dirty、実行中process/job/log、正式/暫定source/run、既存stash・元tree保全、現在の利用枠を照合してください。reset後なら実値を新しい期間として記録し、券の存在だけで枠回復を推定しません。残10%以下では新規実装を始めません。
現在のS/R/Dと未接続箇所から再開し、完了済みS0/S1等を最初から再調査・再実行しません。保全されたtool jobの状態を確認し、同じ外部操作を二重に発行しません。意味ある既存成果を巻き戻さず、モデル・品質・WIP一経路・実証停滞の是正条件を維持して、停止条件まで自走してください。
```

## C. 統合停滞時のPMO介入（必要時のみ貼付）

```text
Schubert_NK PGPTの自走を継続しつつ、477 §6の統合停滞是正を実行してください。現在のS/R/D、最後の実経路source/command/result、残接続、coverage残数、前回点検以降のN/Tと共有枠消費を短く照合してください。
同じ経路の実証が増えない原因を、GPT-6.1 Sol / ultraの対象限定レビュー1名へ渡してください。求める成果は既存methodの具体的接続差分案、所有/budget/Epoch/失敗時継続の整合、独立試験とhost/VM coverage閉鎖、次に実測する外部観測1件です。単なる反例一覧・追加helper一覧・「親へ戻る」の説明では終えません。補助の制約とfallbackは478 Aを継承します。
結果を主実装へ反映し、同じ経路の実測を進めてください。計画修正・通常review・仮予算到達だけを理由に停止せず、PMO返答待ちにしません。未承認外部仕様だけを保留し、独立承認済み作業を進めます。451の品質、残10%/5%保全、現在HEAD/既存変更保全は維持してください。
```
