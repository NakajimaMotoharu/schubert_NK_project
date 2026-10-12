# API新Source全回帰・現行保守前照合

Program NK-OPS-001/API/bootstrap/batch、関連RD SYS002004/OPS009/MQ008010、UI212243251253、SS311312321342343353355、PG-D412。正式1964PT/53scopeは未更新、IT/ST未実施。

| Test ID | 目的・独立oracle・操作・結果 |
|---|---|
| PT-OPS-PGD412-FULL-001 | 全6の全旧suite保持＋新API5/既batch8＝3596、532suite、1643classをsource/diffから先に算定。PG1633 snapshot0044、Production2741/test1683、JDK25.0.4/Maven3.9.12/Ubuntu26.04.1 LAN、worker1/768MiB、filter/NoTests緩和なし。Maven actual0/1536.802347秒、3596全成功/FESflaky-notrun0/static6zero。 |
| PT-OPS-PGD412-FULL-002 | 別PG1636で全XML testcase unique/fresh time window/全source/archive/CRCではなくclass実bytehash/JAR/static/coverage/session一致を独立確認。三API変更・六追加、他Main同byte、LinuxFilesystemClassifier四counter100。actual0、ただし全体host残3772/626/37/1085、同source native未実施・global100 false。 |
| PT-OPS-CURRENT-SEAL-001 | 元1613の実after schemaは10key、pid1だけlist・残dict、nativeは別観測であることを独立確認。missing/foreign/null/架空native拒否、actual生成static0。旧1639 KeyError actual1をBUG1143/YKT911へ修正前記録。 |
| PT-OPS-CURRENT-SEAL-002 | 新1641で同boot3d69/現current4d6/PG1544・真正ordinaryDONE/全24DB・32config・187署名・原本Backup/runtime/十kernel/旧全actor不在/client-advisory-flock0を二読。独立native catalog current8/歴史6のmetadata/hash/windowと旧private保全及び全tree二読一致。Ref正常終了/actual0、元after9f18不変更、業務/配備/start/stop/reload/SQL書込0。 |

command：固定PYTHONPATH `tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime`で `pg1633_api_boundary_full_six.py`（開始済同jobへ再付着、再実行0）、`pg1636_api_boundary_full_qualification.py`、`pg1641_completed_current_preflight_v2.py`各新slot一回。工具testは `-m unittest pg1636_api_boundary_full_qualification_test pg1637_api_candidate_contract_test pg1641_completed_current_preflight_v2_test`、全生成static0。独立期待値はSS固定境界・元私有manifest/schema/全byte比較、Productionからexpectedを生成しない。

公開safe manifest（実時刻/source/command/count/coverage/hash/exitを格納）：

- host `/home/mini/codex/project1/work/pgpt-runs/PG379/pg1636-api-boundary-full-qualified-v1/manifest.safe.json` SHA256 `f42efdee4c3c740792a90aabf1ff55502f99f6643955843d4788f8a536b73bce`。
- LAN `/home/mini/schubert-nk-pgpt/runs/PG1633-six-v1/manifest.safe.json` SHA256 `dfcf5c3eb977d7057b5b8904fbd3283cfead7c59e6e5282a4f0e444547b679bb`、archive `e1c3f195efb3938c4e78dd4f5515df4f1e11de952962d591cde47808624d2cd8`、qualifier `5e1e137cdee31b03a86d23132a3aefce36ed2dec5439ed038ed69e8e211f9b9c`。
- host `/home/mini/codex/project1/work/pgpt-runs/PG379/pg1641-completed-current-before-v2/manifest.safe.json` SHA256 `63449cd4bec8f1b2a068b5a838a674610ccbe709221def7b7d60410b14d73075`、payload `e6ee223c128871912e8edfb93ada5d49fe22fcb4838d8589801970b6bac9c119`。

秘密/raw DB/Backup/token/key/private原本はGitへ格納0。旧1639 actual1、旧143/UNKNOWN、別sourceの旧nativeは不変更保全し合格へ算入0。次は新署名候補/当source実経路/native/CHR/四100/451/trace/引継ぎ、wholeleaf受入増分0。
