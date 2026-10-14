# 新boot有限公開・七phase独立post

2026-10-15 JST、SS343/353/SSC249250264、PT-DEP-2852001/PT-OPS-2854/2856/2858/2860。834～836のnewboot認証・unused・ROを前提にした限定技術証跡。formal1964PT/53scope・受入leaf差0・工数率null・QA051final保留。

## 入力と独立oracle

旧current042/PG2654/BOM552→新current `a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25`／PG2802／BOM `37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863`。新BOOT `79a3260a-e16d-42bf-942a-b914ed144c28`、old run77601cf8/activation26250063/6:56 cutoffは元DONEの保持dataだけ。旧boot/Root/PID/permit権限は移植0。

独立finite oracleは承認済SSC249250の固定expected（新INVALID byte構造、version/BOM approval0400、current symlink target）を新boot/current/candidate literalへ束縛し、全metadata九項・ACL・変更時刻・完全parent tree・保持inodeを各phaseで検査。独立golden/正常全phase/null・未知・境界・metadata各項・ACL・無関係変更・旧FD原本・wrongaliasの反例を、Production呼出なしで確認。新epoch UUIDはfreshv4、boot/run/activationとの同値拒否。期待値を実ポインタやProduction生成methodから作らない。

## 実行・結果

| 段階 | command | 実結果 |
|---|---|---|
| finite/whole Ref oracle | `python3 -B tools/quality/pg2852_network_cold_publication_test.py -v` | 二試験PASS（独立finite子suite全PASSを含む） |
| 全graph | `python3 -B tools/quality/pg2858_network_cold_publication_test.py -v` | 一試験PASS・独立post namespace/static0 |
| current JAR ABI | `python3 -B tools/quality/pg2854_network_cold_publication_compile.py` | actual0/session5916、Java25.0.4/Xlint-Werror・引数/null/mountinfo literal vector |
| immutable工具stage | `python3 -B tools/quality/pg2856_network_cold_publication_stage.py` | actual0/session23790、117file、起動/permission0 |
| 一回正規有限公開 | `python3 -B tools/quality/pg2858_network_cold_publication_activate.py` | actual0/session31238、freshM-A/readonlybatch/advisory/十Ref/保持原本FD、全scope正常 |
| 別fullpost | `python3 -B tools/quality/pg2860_network_cold_publication_post.py` | actual0/session83323、全七phase・24/32/187・oldDONE/原本Backup・RO/12roles・全資源解放 |

PYTHONPATHは835と同じ。operator `e0d45fc290a757f0d34409c096b6deee9ec492ae`、current/candidateは上記別source。専用Ubuntu隔離VM/JDK25.0.4、各phase command/終了/hashは私有frozen/actual manifestへ固定。最初の新source graphはunused traceback importをTDD静的検出→actual前是正。false/未実行/失敗を合格加算0。

実経路は空startup→canonicalINVALID→新approval0400 atomic replace（旧保持FDで原本と既知unlinkのみ認証）→新current symlink stage→renameat2交換一回→旧symlinkをlinked私有保全（inode/nlink1/target/ACL全検査）→fullimmutable/data/資源正常close。公開前/epoch/approval/link-staged/after/database-closed/releaseの全七読取証跡を保持。古stage alias、失敗UNKNOWN交換、旧epoch、Root/Backup/ADMIN/start/stop/reloadは再演0。

## 証跡hash

private基点 `/home/mini/codex/project1/work/pgpt-runs/PG379/`、guest `/var/lib/pgpt-s1-preservation/`。raw原本・旧approval bytes・DB行・key/credential/session/tokenはGitに保存0。

- frozen `pg2854-network-cold-publication-frozen-v1.safe.json`、immutable工具 `pg2852-network-cold-publication-tools-v1`。
- stage `pg2856-network-cold-publication-stage-v1/manifest.safe.json`、archive SHA `98a54ec7cfdd9862eb8e54ed45446f64633d5363b189b16bde3df63720c32fcb`。
- actual `pg2858-network-cold-publication-owned-activate-v1/manifest.safe.json`、payload `1e0e5d2085602e56f8091575a037ce35fe66e58d15a437467e19143f48ec4bae`、log `39e6e12a93b1dc3037e4c6b139f9dafb379e653c6d986bd305bb01be6d59fa5c`、after `51bfda383bbb7a57e8cadc2e213d253fcaba31bef07a1451a1b0b9cf018cf916`。
- post `pg2860-network-cold-publication-independent-post-v1/manifest.safe.json`、payload `0fa1283a421ec5630c577a692ed7586d611288d5f30daf34eea9d7733b7000e1`、after `ecee7f3e149ee12afa74c43d1e8c47f3246acf67e25c542b4ab10c10fb11fe5a`。

postの`source=042`は完全保全した旧release/read-only原値資格、`newCurrentSource=a9`が公開後の実current。両者を混同しない。新INVALIDはpermission未発行。新source3680全体/署名は維持、当native資格なし・旧042成功を合算0。

## 次の未完

新source immutable observer/一回freshordinaryの正規外部起動→捕捉Root/同owner API-Web-Caddy/真正terminal/全24/全体seal/owned停止/当source native/実Browser/CHR/四counter100/451/trace/引継ぎ。BUG1251/YKT1017複合closeとQA051 final保留。通常公開・小受入・commitで停止せず続行、IT/ST合格宣言0。
