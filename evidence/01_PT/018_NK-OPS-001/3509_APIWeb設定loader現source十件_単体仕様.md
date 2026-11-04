# API/Web設定loader現source全十件・単体試験仕様

Program NK-OPS-001。対象ApiConfigurationLoader/WebConfigurationLoaderの全method/physical class、既存Test各五件を一括選択する。Test IDはPT-OPS-API-LOAD-001～005 / PT-OPS-WEB-LOAD-001～005。関連RD SYS002/004、UI253、SS311/342/343§4–5、元2478の個別入力・独立固定期待を継承する。656のMain/Test hash、全十method名、事前条件、入力、期待、権限/副作用、費用を着手前凍結した。

Production Main6b53、Test入力も同commitと全byte一致。旧a90のwhole10と現sourceのstartup一部は期待値レビューだけ再利用し、実行/coverageを移さない。今回の必要性は現sourceのwhole二Source資格が欠けるため。Test/codeの変更予定0。実行命令は `env PYTHONPATH=tools/quality python3 -B /home/mini/codex/project1/work/pgpt-runs/PG379/pg18590-config-loaders-current-whole10-v1/driver.py`。driver SHA256 a2b27daf92b034fda893d86900e4682728afac47ce1b6458d997036df147bb6d、元全文は公開成果へ保存する。

PT_DEFAULTの範囲は固定memory YAML・public nonsecret SHA256・自己所有thread/Futureだけ。production factoryはFFMの固定libc symbol/downcall handle束縛を行うが、native function/FD操作を呼ばず、戻りのproduction.loadも呼ばない。実設定・DB・MQ・HTTP・Root・VM・鍵・credential・native資格の操作/証明は含まない。子環境は既存runnerの固定ENV、nativeアクセスflag追加0、実環境値/アドレスは公開しない。暗号なし/pure-onlyとは記録しない。null/空/未知/例外identity/先行validation/32並行readの独立期待は元assert固定値・回数である。

四counterは両Source全物理二classに原exec一回で照合し、手動除外0、CRC/session一致、全十unique/F/E/S/aborted0を要求する。parser/storage/native依存全体は未資格のまま。既存PMD/Checkstyleも実行し、指摘を隠さず適用性未確定はOPEN。原18474終端未回収、QA054、外部HOLD、正式1964/53、3008/451/650集計は維持し、小群の結果だけで親受入/全451を閉じない。結果・原失敗・証跡hashは3510へ記録する。
