# 1285 JMS同lock完了flag：当source925の独立結果

source59960d19c226fd524bb608a34299d7616433ae50、branch dev-foundation、仕様1284/PG-D460/BUG1544/YKT1304。変更はArtemisReplyConsumers.closedのprivate volatile→private一箇所、Test/expected/build/static/Current/SSは不変更。

元exec12010/pg6106-locked-flag-web925-v1は2026-10-20 15:47:39.601467Z→15:52:07.445166Z、267.843699秒、真正exit0/phase[0,0]、925件/150suite/FES/flaky/notrun0、六format/型null/SpotBugs0、全入力固定。当class実L76/M12/C1/B22すべてmiss0。旧870全3985/coverage/nativeを当sourceの全体合格へ輸入しない。

| 証跡 | SHA256 |
|---|---|
| WorkPG379/pg6106-locked-flag-web925-v1/begin.safe.json | 00fc9b430ccc63846fcc7e0352caddcd0f021532652e4d63c7ec6c3598d54cb9 |
| 同/source.tar | c66d76e41e846be4d244f1fea95ceafcf556f606095c08e8a6c3be8a7d58e3e8 |
| 同/manifest.safe.json | 943e783d44dfc78c78c2222d47de9c6ad84018dfcccd6a66f281c3e9eb86c3f7 |
| PG6108-locked-flag-qualification-v1/manifest.json | 8adb610d4bcbcdf3a345cff889e09f988c79607734d524c46f0cb344dfaab218 |
| 同private manifest.safe.json | 45142110edcfc83bceffcc02d0219dba3a2f7fbba891ca67154c7d07c2d06b92 |
| 同cases.safe.json | 781fb9498d0430340c96bc6b7acaf469ee816ecbdc14601bcc1a247709880a63 |
| 同findings.safe.json | 11ce7af04a4baeed77fe274b35361fc53d9ea8a51067e0020aad35ce1ea592a2 |
| PG6110-locked-flag-byte-v1/manifest.json | f1412018fb6aff74b77d92359b4f13137979d2019720b5f7204618d4b6ad09b1 |

56823/6108 actual0は全原925 XML・全851source/1667Main/六Jarを照合、当outer一件だけ差・他1666同byte、raw PMD1315→1314は当volatile一警告だけ減、processing/Checkstyle0。静的0と言い換えず、旧870の721理由は新sourceのwholejoin成功にしない。

45568/6110 actual0はClassFile構造を独立parseし、closed field flags offset6122の0x0042(PRIVATE|VOLATILE)→0x0002(PRIVATE)だけを確認。**他の全ClassFile byteは完全一致**、全method descriptor/命令/例外edge/publicABIも同じ。closedの二GETPUTはclose内同private final stateLockのlock/try-finallyに限定、stopping/startedのvolatileは保持。Sync/WebLog.closedはreadyがlock外で読むためvolatile保持、既Question/WebBroker.closedは非volatile＋同private final lockで同条件に準拠し変更不要。これらは実Jarで個別確認、他22volatileは同closed/同lock全アクセス保護の変更条件を満たす証拠が無いため削除もstatic受入もせず残レビューへ保持する。

独立ClassFile fixture2unit/選択定義1unit/pyflakes0、binary比較はPG静的根拠で新PT件数/coverageへ加算0。BUG1544/YKT1304当限定scopeCLOSED/完了2026-10-21、修正59960d19c・本証跡commit参照。機能誤動作を観測したとせず、重複modifierによる静的品質項目を閉じた。

当sourceの限定925/対象四100は確認済み、全体/native/CHR/451/trace現候補再認証は変更群をまとめた必要確認待ち。943trace/全3985/721理由は870sourceの歴史測定として1281/1283へ保持し、現候補sourceとの不一致を隠さない。正式1964/53・17/190・工数null・QA051final/PTALT未特定/実VM等HOLD/原v3v4は不変更。次は同sourceで可能なWebの残volatile/例外/資源の個別PGレビューを、当925の独立case/counterへ接続して進める。
