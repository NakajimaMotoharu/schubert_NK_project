# 193 NK-OPS-001 Cleanup子外部入口限定実行結果

2026-09-28 JST、PG334/SSC-104、`dev-foundation`、source `3d0371698`。対象/根拠/Test IDは192。Linux host UID1000、JDK25.0.4/Maven3.9.12/PostgreSQL18 fixture/JaCoCo0.8.15/SpotBugs4.10.4.0。実行command、日時、source/入力/期待/実際、hashは`evidence/provisional/PG334-selected/manifest.json`に記録。

| 観点 | 結果 |
|---|---|
| CMAIN001～004/NCLEAN001/CUNIT001～003、依存CPR/CBA/CDB | Batch選択5 suite/31 PT、F/E/S0。空argvの公開manifest観測でも0/10でなく30、argv有70、null契約/未知identity保持。固定候補Unitのprivate2 credential・root/依存/停止policyを独立literalで照合 |
| Production外部Javaのhost smoke | `CleanupProcessMain`をcompiled Production classpathで別processとして起動。UID1000、引数0、終了30、stdout/stderr 0 byte。真正root CLEANUP Unit/credential/DBへ到達したという証拠ではない |
| BUG-312/YKT-245 | 初回Batch SpotBugs1でstatic不合格→915/916起票→固定backup openを明示methodへ移動。再試験Batch SpotBugs0、Production6 moduleそれぞれBugInstance0。未修正testを合格に加算しない |
| 新class Java coverage | `CleanupNativePreflight` line 1/38、branch 0/2、method 1/10、class 1/1。`CleanupProcessMain` line 7/12、branch 2/2、method 1/3、class1/1。全4指標100%未達。JaCoCoはno-clean累積の限定計測で正式全体値ではない |
| 付帯Batch suite | PG334 Unit候補追加前の依存reactorは618 Batch PT F/E/S0でexit0。その後sourceのBUG-312修正とtest候補追加を行ったので、同一sourceの正式全回帰へ加算しない |
| 実VMの非起動Unit構文照合 | 候補templateと隔離Ubuntu VMの`/tmp/pgpt-cleanup-334.service`はSHA-256 `ced5a9ec47100eaff74edf5db1585d3c51991f60fd119b5462517d2b3c11962a`で一致。`systemd-analyze verify /tmp/pgpt-cleanup-334.service` exit0。出力は配布元xfs_scrubの`CPUAccounting`非対応警告2件のみ。Unitは正式pathへinstall/enable/startしておらず、`schubert-nk-cleanup.service`はnot-found。構文成功を実効policy/実子成功へ読み替えない |

証跡: `evidence/provisional/PG334-selected/manifest.json` SHA256 `6f2b0c031a725fe54098851bbf970b3b2a7e6f7ded82e4e95b2ee601ce05a8fa`。Sanitized JUnit5/coverage1/static1/BUG結果1/smoke1の9fileを全hash再照合し、properties/output/failure/skippedと秘密値を保存しない。原始logはGit外でSHAだけ記録。

未認定: native root成功経路、Unitの非起動配備とsystemd実効設定、親M/A・同run handoff・API/Web全終端・実DELETE/transfer、Artemis `Requires`起動、Production全体coverage100%、実NK CHR。正式認定は従前`858713c0bf310ae8bf62078b0a1cedbce4e968db`/`PT-WEB-20260925-24`/1964PT/53scopeのまま。PG/PT工程完了ではない。
