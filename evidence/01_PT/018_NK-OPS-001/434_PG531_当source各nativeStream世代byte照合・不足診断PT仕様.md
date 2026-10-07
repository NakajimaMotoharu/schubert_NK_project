# PG531 当source各nativeStream世代・byte照合と不足診断

対象Productiona2/PG495/schema028。SS342343/SSC193196215、451の4counter100%・全scope/source/run/独立oracleを変更しない。PG522当親真正DONEと普通API/Web、PG526同世代ownedTERM/native witness、PG530全新scope正常/原値二読とpeer-lock0を前提にする。旧PG481 sourcebab/旧native/旧counterを当sourceへ混ぜない。

| Test ID | 期待値と独立根拠 | command |
|---|---|---|
| PG531-H01 | 当親開始UTC2026-10-07 19:46:29.837227～DONE20:08:51.344734、API capture1791407716520095us/Web1791407714709599us、固定Root/ordinary roleIDに対するliteral境界/null/unknown/foreign58assert。raw coverage session IDは出力0 | NativeStreamInspect531Test |
| PG531-V01 | sealed PG530afterSHA d08b56b1…の8file/hash/metadata9（atime除外）と所定owner/mode0600/no-symlink/nlink1を検証、heldNOFOLLOW FD原値を私有exportして再hash。file presence自体をPASSにしない | pg531_collect_native_diagnostic_v1.py |
| PG531-V02 | **各streamごと**single session/当時刻/同role/当source6jarのproduction class IDを独立検証。混合unionで旧streamの不一致を覆い隠さず、非当run/byte不一致/未起動を未受入・残件として記録 | NativeStreamInspect531 |
| PG531-V03 | 同a2 hostPG495 frozen6jarSHA＋該当eligible current nativeだけで診断counterを計測、class mismatch0を要求。未達line/method/class/branch/全roleは残件、全native/正式PASSへ読み替え0 | NativeCoverage、後続private gap XML |

入力native実8: parent/backup/cleanup/expiry/RootAPI/RootWeb/ordinaryAPI/ordinaryWeb。Backupは当親SKIP/旧run参照の可能性があり個別判定し、Inspector/Bootstrap未起動はnot-run。入力を減らして対象class母集団を除外する操作は禁止、却下stream/欠落role/全counterを明示する。旧raw/native filesはそのまま保全。

着手群は487 event0028、N15.03=1.25/3/6.25＋N15.06=.84/2/4.16＝2.09/5/10.41pp。既N15.01/.02/.04/.05開始群2.91/7/14.59を再加算0、親N15総5/12/25不変更、個別実tokenと専有消費は不明。静的undefined0、JDK25.0.4/JaCoCo0.8.15/ASM9.10.1、Source/試験工具固定後一回new-only。VM start/stop/reload/agentattach/DBwrite0、binary exec/raw sessionsはprivate、Gitはsafe aggregate/hashのみ。正式run24/1964/53scope更新0、IT/ST判定0。実結果は後記。

実結果: source150530872、collector4990 actual0、8stream全single/time-role/classByte0/unknownClass0、Host frozen6jarと実8nativeの診断counter。protocol/storage/webは全4指標miss0、bootstrap=LINE91/METHOD14/CLASS0/BRANCH89、api=85/3/0/16、batch=1297/235/11/894。全体未網羅1473/252/11/999、全counter100%未達・Inspector/Bootstrap未起動/全negative-PID-INV物理対応は未認定。Parent/Backup/Cleanup/Expiryの最低single/time/source一致を実経路全条件の代用にしない。safe manifest=evidence/provisional/PG531-native-current-diagnostic-v1/manifest.json、元私有summary SHA8c273962…、exec/rawはGit無し。

PG532一回XML診断（source150530872に未commit helperを加えた時点、operatorScriptSHAはsafe manifestへ固定、正式受入0）: 同source/同8stream、gap class数bootstrap10/api4/batch120、別Module0。privateXML/実class-method-line/branchを機械抽出・counter一致を確認、safeGapSHAd0e10124…・evidence/provisional/PG532-native-gap-v1/manifest.json。未commit helperの実行を正式frozen-source検証へ読み替えず、実解析のinput6Jar/8execのSource/bytehash整合だけを当不足選択へ使う。
