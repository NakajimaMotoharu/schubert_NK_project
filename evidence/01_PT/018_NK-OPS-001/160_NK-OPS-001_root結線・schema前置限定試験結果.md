# 160 root結線・schema前置 限定試験結果

2026-09-28。仕様018156、NK-OPS-001/NK-BAT-001、SS331/341/343・SSC095096・PG-D314、BUG296297/YKT229230。base source `a275496a135dfe2ac295afecb4df11d6981bed5d`＋各manifest記載のdirty source hash。正式認定・R2/R3・IT/ST合格ではない。

| 保存run | 終了日時JST/終了code | 実行・結果 |
|---|---|---|
| PG314-rootSchema-limited-1 | 05:03:14/0 | Storage8/Bootstrap16/Batch24＝48件、F/E/S0、static0。固定入口の公開API反射、全close後生成、current再読、OS/JDK拒否、六列schema不一致、未admission beginの実DB後条件0行を確認。 |
| PG314-rootSchema-static-RED | 05:15:17/1 | 上記48件成功、OS祖先/ACL/保持vs現在inode・全取得close注入成功。ただし固定path再生成lambdaの個別portability check1で全合格ではない。BUG297修正前に全XML/counter/static/source hashを別退避。 |
| PG314-rootSchema-GREEN-3 | 05:18:32/0 | 上記48件F/E/S0、NullAway/SpotBugs0。固定Path1回生成による再open共有、wrong typed値・null・割込前後・未知identity・OS公開実file IO・旧held/current祖先反例・両begin前Schema故障SQL/IO/Runtime/Errorを確認。 |

実行command/toolchainはprovisional各manifest。GREENは6JUnit/3coverage/3static、全source hashと元log hashを次試験前に固定。OS Ubuntu26.04/Linux7.0.0-34、UbuntuJDK25.0.4+7-1-26.04、Maven3.9.12、Spotless3.10.2、JaCoCo0.8.15、SpotBugs4.10.4.0。48件以外の残留target XMLを合格算入しない。

独立oracle: RootBOM001～008はliteral六列・vendor/OS/JDK Map・固定query/closeイベント、synthetic root kernel/NSS portを使用（実rootの代用ではない）。OS inode fixtureは古い保持handleを不変に保ち、親から再openした現在の/usrまたはlibだけ別inodeへ移し拒否する。実OS streamの正例は一時公開fileの27byteを独立比較し、実host OS承認とは区別する。MDB007は旧constructorでbegin拒否後、独立admin SQLがrun31400000の行0を確認。両begin正常／commit ambiguityの実PG後条件は明示synthetic schema port付きで従来どおり確認し、native opaque authorityの合格へ読み替えない。MDB006追補はschema故障実到達1回・HISTORY SQL/commit未実行・全owner解放をassertする。期待値をProduction methodから作らない。

GREEN限定counter: RootReleaseAdmissionはbranch78/78・line126 covered/14 missed・method22 covered/3 missed（固定native入口）；NativeOsIoは全counter0 missed。MorningDatabaseSessionはbranch52/52・line116 covered/4 missed・method18 covered/3 missed（実Root release constructor/closure）。Sessionは全counter0 missed。FullBOM helperはline234/method30/class1全covered、branch139 covered/39 missed。残native/分岐は除外せず同source補完を要求する。

BUG296/YKT229: 新OS readerを修正、既存RootApproval/StartupRelease/BackupTerminationは親再open＋前後照合を持ち直接修正非該当。新synthetic namespace回帰は成功、既存全依存回帰とnative同class補完待ち。BUG297/YKT230: 新readOs2literalだけを1固定Pathへ統合、candidate/callerからpathを受けない。抑制のclass化・security/null/coverage除外なし。直接限定再試験済で、全bundle認定までは完了扱いしない。

collector: Bootstrap ownerにnew helper/test、022と独立019にFullBOM8/RootBOM8の正確method署名・PT prefix・runtime subjectを登録。Batch予定516（従来508＋8）、OPS内Batch229（従来221＋8）、旧508拒否。105 canary全成功（/tmp/PG314-collector-canary.log）。次security横断回帰予定2217件、正式countは実結果から確認する。

次の受入: host releaseを真のRO mountへ配置、候補外の固定Ed25519/pinned署名配備側で全BOM検証後だけ原本発行、V023を専用migration actorで配備、pending Native027を同identity resume。全M/A・全対象終端/INVALID・実worker/3archives/DB成功/7世代/全30分・permit/business main/実NK CHRは未達。公開claimsのparse/照合や限定48件から承認済全起動を報告しない。
