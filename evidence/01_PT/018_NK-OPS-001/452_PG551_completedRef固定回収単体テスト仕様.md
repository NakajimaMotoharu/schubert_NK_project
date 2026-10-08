# PG551 completedRef pre-SAVE固定pair回収

NK-OPS-001、RD OPS/BAK/MIG、UI251、SS343353/SSC222/QA047、BUG843/YKT612、PG549-C007。旧source868c2d4e6/v4補助NameErrorでbefore/SAVE原値未取得、oldRoot576780/Ref576809・DB576807・M-A保持とidle60s後peer0を分ける。

|Test ID|対象・入力/操作|独立期待値・根拠|
|---|---|---|
|PT-OPS-PG551-H001|identity literal/root-ref/null/type/UID/argv/ticks/親・子、wrapper正規新name/reservation/sourceSHA|固定root576780/ticks4161990/sudo576778、Ref576809/ticks4162106/親576780、独立全field変異拒否、全task唯一子Ref・Ref子0・先行private一回予約/Ref→RootだけpidfdTERM。未知/別世代操作0|
|PT-OPS-PG551-H002|新metadata十Ref・全元値/unused候補187/旧current署名187/immutable7payload/solepeer or role60s後完全0・M-A FD-FLOCK/元error二読|preflightactual0/source868c dirty四helperSHA明示/2.555215050s/logf3a41cca…、before原値/全24-462/原本Backup/全18/config/currentISSUED/native9/候補未RO不変。動的owner失敗を新before成功へ変換0|
|PT-OPS-PG551-H003|same4helper/source固定→execute一回/予約→Ref→RootだけTERM143/全原値二読/全oldowner-peer-advisory-FLOCK0/新Refbus正常|旧actual143/UNKNOWN保持、旧source/nativesafe合格捏造0、new回収actual0と区別。before=after/privatecomplete正常後だけ、業務start/namespace/DBwrite/reload/配備0。現在未実行|

Commands: `python3 -B tools/quality/vm/050_s1/pg551_completed_ref_test.py`→`.../pg551_completed_ref_native_v1.py preflight`成功済→source固定push→同`execute`一回。管理testはProductioncoverage/PT加点0。exact旧namespace/proofsと当privateRawを保全、公開manifestはsource/run/実時刻/exit/command/環境/helper/RootproofSHAだけ。次新v5owner globals/閉schema/oldEpoch join・phase negative/真正typedBOM/allnewscope正常verifyへ。
