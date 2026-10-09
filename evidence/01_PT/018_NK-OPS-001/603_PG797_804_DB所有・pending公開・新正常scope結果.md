# 603 同owner DB生存・phase別公開照合・当source新正常scope

NK-OPS-001、OPS009/UI251/SS343354/SSC238・BUG936/942～947/YKT705/711～716。工具PT加点0、Production source102cdf1d365ab321f74b523237590eee764ae858、正式PT-WEB-20260925-24/1964PT/53scopeは不変更。PG794同source3517PT/520suite/静的六0は602、host全四100とnative全体は未受入。

## Test ID・独立oracle・実結果

| Test ID | 入力・目的・独立期待 | 実際結果・証跡 |
|---|---|---|
| DBLIVENESS798001～004 | 元batch/backend/role/app/db/RW/advisoryとmigration/session/effective nk_owner/RO/no-advisoryを別列で照合。同Connection・sameThread・変更/再取得0。null/欠落/未知role/喪失・SQL/Runtime/Error・正常close・既失活→retain入口で両SQL停止を独立JDBC fixtureで検査 | 307 lease条件＋scope fault/実生成retain入口6反例、Werror/whole生成AST/CLI0。Actual798 stage0/verify0、86.990672s。800独立0・最大確認gap5,002,387,853ns/41確認、全24/544/39/原本/Backup/署名/設定/10kernel・DB/advisory/M-A0。旧scope799/779の正常closeへしない |
| NAMESPACE797001～003 | 全生成compile/Python/class/argv/TOOLS/frozen/source/hashを独立照合、未使用停止surfaceをprobe helperから削除 | 797v1 compile1/FQN、v2 verify1/authentication-effective混同、v3 assemblySyntax失敗保持。v4 actual0/87s後にレビュー945を新798へ是正。旧失敗を成功へ補完0 |
| FREEZE799001 | 同原本9de2/021111b4/cutoff2026-10-09T05:42:22.532331Z/bootcc9/INVALID e9/全24/39/544、全十Ref下の同27宣言・kernel0・resource0で新candidateだけfreeze | place796=0/187file、799v1 guardはRefなしで非ロードUnit・implicit After不足を拒否/UNKNOWN、801固定pidfd TERM/原値0確認、旧host143保持。v2 guarded全十Refで進行した |
| APPROVAL799002 | 許可deltaはapproval/currentのみ。beforeは旧750、after/回復/readbackは新796をそれぞれ固定し、未知/逆転source拒否。旧epochのbyte不変・全24不変 | v2は実公開後、helper parent()がbeforeの750をafterにも要求し拒否/UNKNOWN。946と947は別原因。803v1 stale guard拒否/SAVE・TERM前、803v2は新currentに固定し既Java/Ref二actorをTERM、全原値/DB/advisory/M-A0。旧799v2 normalClose=false/exit143維持、二重公開/起動/Unitstop0 |
| READBACK804001 | 新M/A・元2Connection・十Ref・current796の187署名BOM/source102、当pending original/全24/39/544を全scopeで確認し、新scopeだけ正常帰還 | compileは旧750 ABI/Werrorで行い、actual VMは新796全JARでstage0/verify0/86.814116s、log65e16c24b55ccd89cc559d76eea19ef32bc1d14f4c1cc5b484fa7fa41d41746a。802独立0・最大gap5,001,963,143ns/41確認・Unitfile18/private coverage-before・10kernel/DB/advisory/M-A0。正式/真正親DONEではない |

固定75秒超の正常観測は、role設定60秒/親1800秒の変更無しで同server接続を保つ限定実証。wholepairのloss後再SQL0と固定DB_NOT_CONFIRMEDは独立faultで検査したが、実DBの故意失活/再発防止全範囲は未閉鎖。BUG936を全解決にしない。新scopeの正常帰還は、旧799v2/779 UNKNOWN・143や旧758の親timeoutを正常化しない。

## 実行・環境・hash

branch dev-foundation、Linux VM bootcc9ed874-7f4f-450e-a188-8de1e42c8441、Java25.0.4/PostgreSQL18.6/JDBC42.7.13/schema028。親予算1800s/idle60s/DDL/grant/業務DB変更0。Current baseline/stash7/原本/Backup/元Scenario3保全。

Commands: `pg798_probe_compile.py`→`pg798_probe_native.py stage/verify`→`pg800_probe_post.py`。`pg799_candidate_place.py`→`pg799_pending_native.py` v1→`pg801_guard_handoff.py`→`pg799_pending_v2.py compile/stage/activate`→`pg803_handoff_v2.py`→`pg804_current_compile.py`→`pg804_current_native.py stage/verify`→`pg802_current_post.py`。いずれも`python3 -B tools/quality/vm/050_s1/<name>`。旧slot再発行不可。

source798=4984e77617d886f13f60e1134445a0128d1bdc91、799v2=ce285c21113c2a8cf052bbe96608ab14da5de3ad、803v2=4b4bdb8a2fb46edee3b3371b955b9a87d619e7b4、804=3cdafcaa800eb80cb2f2cf01e739a98e32345da9/802=ed1b697498134d77d48b801e4cf5e0819d53cad5。全full/Production source102と工具sourceを区別する。

Git外private `/home/mini/codex/project1/work/pgpt-runs/PG379`のactual exit/safe/log/frozenとRoot `/var/lib/pgpt-s1-preservation`の原値を保持。800snapshot SHA07b39c1faf43629f79d36e58055817aedb1a30ac36d0c3e34707df5e7e3cb5b2、803v2snapshot d82a4626f8b9a0cb00130087413d1dd227dd04ced4f9add680668f99b27c6a92/complete60486256b6941b73e5a0546e11b860d958ed1970275e82f1799f83f667348a43、802snapshot fc1fb69cbc9e6db2d5c246547a0181f1a1b41c7b89c1ac7198edb69f638e07c5。署名BOM c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d。秘密/DB原値/credential/native rawをGitへ入れない。

## 未完・次

BUG947のbefore/after固定source guardとRefs内例外保持/固定frame診断をrecipeへ反映し独立全surface試験する。正常804/802は公開の新所有readbackだけで、旧799v2の正常返却の再認定ではない。次は802全原値/18Unitfile/coverage-beforeから新only同9de2 runtime resume→observer-first/durable一回予約→新親1800s真正DONE→owned停止/当source native/CHR/四100/正式/引継ぎ。QA051はL01最終比較だけ保留。IT/ST合格は宣言しない。
