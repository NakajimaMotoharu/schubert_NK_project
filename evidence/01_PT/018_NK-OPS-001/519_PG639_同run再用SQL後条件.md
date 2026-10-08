# PG639 同run再用の独立SQL・Backup後条件

## BUG903/YKT672訂正（2026-10-09、v2実受領前）

v1actual1/保存前/秘密logSHA6d27263a…を保護。SS341 SSC200・SS331/V022の今回SKIPはaudit三列NULL、元3a53SUCCESS auditは元cutoff-7days（2026-10-01T15:32:46.368375Z）/before-after0を独立に再読する。旧本文C001の「今回Expiry元cutoff-7days/selected0」は両者混同の誤りで、今回rowへ監査を生成しない。現在fresh MQ selected0/Expiry Unit終端は別実経路証拠であり本snapshotの成功から推定しない。修正前誤audit要求拒否・現在三列各破損拒否・元audit各破損拒否を手書きfixtureへ追加、独立4/Pyflakes0。新slot pg639-post-v2、guest pg639-resume-post-v2、旧v1に追記/再発行0。全旧24/494列・Backup metadata/hash不変と今回十SKIP/504の検査は維持、PG640前提もv2だけ。

SS331/341 SSC200・343 SSC228229、QA047、WBS-N15.04既.83/2/4.17pp内（追加/二重費0）。Production36fe/PG631/57a・parent1522744/293d218b/104329/start103062293730/元1800sに固定。PG637v2実一回start後、同経路のread-only受領だけ。所定新10attempt/494→504、全旧494列不変、23他table全列不変、REUSED_SUCCESSによるBackup全metadata/hash不変・削除0をSSの独立SQL後条件とする。DBdump/秘密はRootprivate、公開はhash/判定だけ。

| Test ID | 独立期待・検査 |
|---|---|
| PG639-C001 | 手書き494旧＋10新literal fixture、順序だけ変更可。新十固定step、同e492/JST2026-10-09、全SKIPPED/ALREADY_SUCCESSFUL、ended=start/all件数byte0、attempt旧最大+1、Backup元e492SUCCESS・他八元3a53唯一SUCCESS、Expiry元cutoff-7days/selected0 |
| PG639-C002 | 十七column各null/破損、型/step/run/日付/status/error/count/time/attempt/Expiry不一致を拒否。Production呼出で期待値生成0 |
| PG639-C003 | 旧row変異・Backuphash変異・他table列変異・余剰/欠落/重複拒否。成功の再分類ではない |
| PG639-R001 | 固定sealedafter c946…/新issued/boot/sourceから元budget内でfresh24readonly snapshot。全504終端後全table二読/Backuptree二読/同親前後保持、Rootnew-only pg639-resume-post-v1/full-rows.private.jsonへ保存。親DONE/ready/native/global/正式は別受入 |

command `python3 -B tools/quality/vm/050_s1/pg639_resume_oracle_test.py` 独立3成功/Pyflakes0、未実行R001を成功へ算入しない。実行 `python3 -B tools/quality/vm/050_s1/pg639_capture_resume.py`、通常証跡pg639-post-v1.safe.json/exit、private stderr/rawはGit外。Java PT/coverageへの加点0。formalPT24/1964/53維持。現在API/Webへ業務HTTP操作未発行なのでその変更をSQL期待へ取り込まない。
