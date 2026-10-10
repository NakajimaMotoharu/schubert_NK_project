# 共通StopHold実shutdown独立PT・採取仕様結果

Program NK-OPS-001/FixedNativeCoverageStopHold、WBS-P018-08。SYS004/OPS009/TST004、UI212/251、SS342/343/451、SSC194/BUG753。Production main-byte=D5不変更、testsource=ac497af0a9aa5df0343f0b0fb2048829f6913713。当限定host PTであり当普通VM/native/全source正式の代用ではない。

独立fixtureは所有newhost JVMだけにTERM一回を送る。PT-OPS-NHOLD194001～005はowner/foreign/null/unknown/add-remove exception/normal/NOT_OWNED/interrupt/idempotent、194006は旧application hook完了後もoutercaptureまで終了しない実TERM143、194007は別newhost JVMの実shutdown開始witness→普通hook解除を試みliteral SHUTTING_DOWNを確認→late JaCoCo dump→witness返却→actual143。194007のwitnessを194006のearlyexit判断に流用せず、193以前のapp/nativeを混ぜない。Production内部reflection・人工状態改変なし、reflectionはJaCoCo公開RT dumpのみ。

通常JVMの自動JaCoCo hookはshutdown開始時に先行し得るため、初回1272は6PT/FES0/static0であっても後2行未採取、1273は四100gateactual1を正当に保全。既存expectedを変更して成功にしない。新1274 selected7/FES0/static0/13.649414秒、selectedexec99e194f5e3823e73ed4880e04e80cea5ac7af864f99b7ca178325eba51f192c4。1275は既D5/1018のfrozen production classjarとそのselectedexec一本だけを解析し、classByteMismatch0、3独立JVM/4session records（自動＋late dump）全開始・終了が当実run時刻内、旧native/host0。

| Counter | Covered | Missed |
|---|---:|---:|
| line | 46 | 0 |
| method | 7 | 0 |
| class | 1 | 0 |
| branch | 28 | 0 |

実commandは `python3 -B tools/quality/vm/050_s1/pg1274_stop_hold_selected_v2.py` → `python3 -B tools/quality/vm/050_s1/pg1275_stop_hold_selected_counter_v2.py`。環境Ubuntu26.04/JDK25.0.4/Maven3.9.12/JaCoCo0.8.15、branchdev-foundation、operator a38292aa4で資格照合。私有manifest: `/home/mini/codex/project1/work/pgpt-runs/PG379/pg1274-stop-hold-selected-v2/manifest.safe.json` SHA51a2084d16ed258cd5d4f236f715b2eb03ac10c7663c49a2995736726f5d9aac、1275 SHA629b72c872e891ed2eb17a997c6ec7d53d73720316d33e01bbcfb946bacecb4c、XML65980f0bc3cdba1c0ab89cee6cfaddd3535d0ebddd19005e562e7675908d4d97。全旧target試験/coverage/static証跡はnewrunへコピー保持、rawexec/session情報はGit外。公開数値のみ、秘密情報なし。個別実token/費用unknown、shared19→20を個別費へ配賦しない。

四100はこのclass/selectedrunだけ。NativeCoveragePrivateFileの10branch、他bootstrap/batch/API・実VMfault/QA051/CHR・同一source全回帰/正式451・trace終了は別残件。正式PT-WEB-20260925-24/1964PT/53scope据置、全P018-08/PGPT/ITST完了ではない。
