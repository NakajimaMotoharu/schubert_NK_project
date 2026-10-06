# PG498：pending code-only配備とhost readonly境界

NK-OPS-001 / SS343353 / SSC198202204205 / QA047 / BUG807 / YKT576。Production source=a2e98ce9e96c42425921e3686e8ae7a94bff9e6c、全回帰PG495 actual0・3411PT/510suite/FES0/static6zeroと同source。工具のみ変更しProduction PTやcoverage件数に加算しない。

## 独立期待値と結果

PT-OPS-PG498-001：固定PG495/BOM f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44、全187artifact/28SQL/履歴29/schema028、Root group986/files640/dirs750、host readonly必須。rw候補をtyped verifierが拒否したnative-v1はSIGNED_ORIGINALでUNKNOWN、current切替/DB/Ref/SAVE/start前。findmnt/statvfs旧PG489 ro対PG495 rwが独立原因。検査や署名oracleを緩和しない。

PT-OPS-PG498-002：固定Root Java22255/ticks26384604/boot e07aa706/argvSHA1127333b3f3d2fbaac2d884b93411c6292c893d4b269b5bc2b8a2d0f64b2216f、全task子0/実M-A lock inode、全24DB/10Unit/config/原本Backup/startup二読不変・peer/advisory0を認証。handoff v1は初期工具検査のcommand引数契約でTERM前actual1、v2 actual0でpidfd TERM一回、旧native-v1 actual143、close UNKNOWNを保持。私有予約・完全後条件保存、業務資源stop/start0。

PT-OPS-PG498-003：新M/A内で固定署名とBOM digestを確認→全10終端/24全列/原値二読/peer0→既承認freezeCandidate→typed全candidate→別専用batch DB/advisory/十Ref→approval/currentのみpublish→原値不変→全新scope正常帰還。native-v2/session41975 actual0、host compile-v3 Werror0/Java10・独立Python16、guestJava10。compile-v2は初期frozen lib path誤置換で未成功、証跡保持・合格に算入0。現current=PG495/sourcea2、epoch同INVALID/73file/run91/cutoff/activation不変、24table/442batch/schema028・全10終端不変、start/migration/permit0。固定候補のbind roだけ実施、既存payload byte上書き0。

実command=`bash tools/quality/vm/050_s1/pg498_pending_compile_v3.sh`、`python3 -B tools/quality/vm/050_s1/pg498_stage_pending_tools_v2.py`、`python3 -B tools/quality/vm/050_s1/pg498_pending_native_v2.py`。Ubuntu26.04/JDK25.0.4、branch dev-foundation、工具親保存HEAD d7cab5652ca79803cd0cbbddf60db0acd80518ee＋対応未commit工具（次保存commitで固定）。実日時/OS/source/command/exitはWorkPG379私有logとstarted/completedに保持。

公開manifest=`evidence/provisional/PG498-pending-readonly-v2/manifest.json`。Root private `/var/lib/pgpt-s1-preservation/pg498-before`、`pg498-preflight-owned-handoff-v1`、`pg498-pending-codeonly`、immutable tools-v1/v2を保持。raw epoch/auth/password/token/原本/DB/native実体をGitへ保存しない。

## 未受入

YKT576の他旧pending工具全前提確認、YKT574依存8行列、新runtime正規退役/一回外部親30分/DONE/native、global100/正式R4/CHR全件/QA051比較・残PG/PTは未完。当配備actual0を親成功やformalへ流用0。正式PT-WEB-20260925-24/1964/53scope/48.3%維持、IT/ST未認定。
