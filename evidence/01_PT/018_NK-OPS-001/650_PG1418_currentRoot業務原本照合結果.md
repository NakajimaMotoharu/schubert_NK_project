# PG1418 currentRoot業務原本照合結果

仕様649/SS314/324/331/341/343/351/352、主担当WBS-N15.06の当source原本採取・照合subset。業務消費側N01/N02/P006-04/P006-05へ参照し費用を再計上しない。Main769/VM1292、dev-foundation工具source22c99529dc6f2e8ff1886effcbad2eeb82f223a6、実command `python3 -B tools/quality/vm/050_s1/pg1418_current_business_readonly.py`、2026-10-11T02:27:22.106412Z～02:27:29.869235Z/7.762823秒/actual0。host actualpayload結合1testと既独立Backup/config/Log/journal11testも全0、新Production試験件数への加算0。

|Test ID|独立期待値と実結果|結果|
|---|---|---|
|PT-OPS-BUS1418001|before1319 SHA3cb4…/当Main署名187/全24・32property・十Unit/原本/Backup/native・全client/advisory/FLOCKを正常Ref寿命内で二読。freshafter SHA d0dc7150…は既current snapshotと同値|PASS、新metadata正常終了、起動/停止/reload/SQLwrite0|
|PT-OPS-BUS1418002|保持FD/NOFOLLOW/全9field・ACL/mode・canonicalMANIFEST・三archivehash/size・二DB handle/count/byte。config8memberとeffective/profile/template/host env責任分離、pg_restore --list actual0|PASS、dump16666903byte/config20480byte/暗号credential41160byte、total16728543byte。BACKUP_DB/CONFIG attempt2とmanifestの一致。成功した当Root結果であり別sourceからの借用0|
|PT-OPS-BUS1418003|同Web Invocationのcausal222/固定2336byte電文/独立AES-GCM/AAD/nonce/HTTP/DB/Outbox/local/session。旧row全保全、retained446/期限delete0、journal全field/order二読安定|PASS、Log222/Outbox SENT222/匿名暗号session222、重複message/nonce/session0。鍵guest内finally wipe、raw/plaintext/key外出0|

実Rootは1320/DONE1477.543157秒、四owned stop1336、currentADMIN1396を再発行せず原本を検証。nativePhysicalFiles20はdisk上全保持数でありcoverage選択9を増やさない。L895/M176/C12/B717/正式1964PT53scope/全WBS受入0据置。QA051最終比較はfalse、外部request fixture完全性は不明。Log再送故障・競合、Backup失敗/skip/timeout・restore/prune、合法Inspector/四100/残CHR/451は別未受入。IT/ST完了ではない。

私有run `/home/mini/codex/project1/work/pgpt-runs/PG379/pg1418-current-business-readonly-v1.safe.json` SHA ed0680daae0f1b5ce977e201946a21d6050b9cde6f14037742fbbf96e8058761。全raw原本/private key/journal/DBはVM私有内保全。公開manifest `evidence/provisional/PG1418-current-business-readonly/manifest.json`。新BUGなし。host0.82GB余裕のため重いnew disk/全回帰コピーは未発行、品質緩和0。
