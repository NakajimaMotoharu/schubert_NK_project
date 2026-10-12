# NK-OPS-001 保持inode分類：影響全回帰と署名候補の資格

対象SS311/343/353、SSC269、QA047承認済原因対策。RD/UI/DIF/通常期限・全graph・ACL/readonly/epoch/rootの既契約を不変更。WBS-P018-03.01/.02の内部分類、P018-02/N12の署名候補、全回帰共通K01は責務と費用を分離する。本文は実行仕様であり、未実行・途中結果を合格にしない。

## PT-OPS-FSTYPE-REG-001：是正sourceの必要全6

Production source `4d6bcbddb417b76d27e52d5d9640752c300edccf`、実行snapshot `308d144b6e51ee91f502795fb5730e004643c304`、branch dev-foundation。PG1532は専用LANの固定JDK25.0.4/Maven3.9.12/PostgreSQL18.6/Node24.19.0/ShellCheck0.11.0/ACL2.3.2・Ubuntu26.04.1/x86-64、worker1/heap768MiB/offline、専用source/target/tmp/fixture。環境導入・復元対象は425の記録へ接続する。VM/業務DBには変更を発行しない。

実行：`python3 -B tools/quality/pg1532_filesystem_closing_full_six.py` 一回、当jobへ再付着。triggerはSSC269とBUG1124是正のProduction storage/batch変更。NoTests literal true、静的/format gateは不変更。旧Main769の3578、旧f877の3582、是正後storage限定22はいずれも全6の代替ではない。

独立期待値：旧3578PT/523suite/1635Mainの全対象を保持、新分類器5test/1suite/2Mainを追加して3583/524/1637。内訳はprotocol81/17/174、storage163/23/74、bootstrap298/40/105、API963/157/401、Web886/129/315、Batch1192/158/568（PT/suite/Main）。正常・境界・null・異常・例外・tamper/ACL/readonly・並行/再送を既全suiteへ回帰する。F/E/S/flaky/not-run0、静的6module0、全source input不変、Mavenとcollectorの両exit0を要求する。

全回帰後1533一回はBUG1125として固定debug差分不足を拒否・actual1保全、新only `python3 -B tools/quality/pg1541_filesystem_full_qualification_v2.py` で資格する。別の資格者処理がXML時刻/hash/case一意/結果、archiveのhost→server同値とGit Production差分0、全package1637Main byte、静的XML、coverage/exec/sessionを再照合する。旧同Main769全6から変更byte4class：EnvironmentInodePolicy/InspectorEnvironmentReader$NioIoの2semanticと同policy Metadata/Snapshotの2debug-only。追加はStorage分類器/StatfsCallの2classだけ。2recordは定数pool・method Code・stack map・全属性・行offsetを含む非行番号全byteが同一で、LineNumberTableの固定+1だけ（13/19entry）を独立class parserで実証する。coverage/CRCの対象から除外せず実byte4として保持し、未知差分/別offset/Code変造は拒否する。分類器line/method/class/branch各missed0を別資格するが、全体四100は別native/global gateであり、この全回帰だけから宣言しない。

工具の独立fabricated graph6試験は全3583case/524XML/1637byteの合成資格fixture、別source/skip/flaky/static/byte変造/case重複/分類器branch欠落を拒否する。これは工具検証で、Production PT3583へ加算しない。

## PT-OPS-FSTYPE-CAND-001：hostだけの正規署名候補

前提は当PG1532/1533全資格0。`python3 -B tools/quality/pg1535_filesystem_signed_candidate.py` はその六JAR固定hashだけをpinned mini SSHで専用新namespaceへ受信し、hostの既PG1292/BOM `ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99` 全187payloadと独立class差分を照合する。資格済byte以外をbuildし直したり旧sourceへ置換しない。

独立期待値は同187path、schema028、SQL28/history29、DDL/config/依存/secret配置/署名pinの不変更、VERSIONと当module JARの有限差分だけ。候補PG1535のmanifest/source/全hash/canonical sumsを固定し、Ed25519署名をhost private keyで作成・public pinで検証する。秘密鍵はLAN/VMへ移さず、ログ/argv/env/Gitへkey実体を出さない。新candidate/tree/signatureをforce/dirsyncして候補receiptを保存する。候補作成は未配備・正式未受入のまま。

独立工具試験はclass差分2、資格/受信admission4。unknown moduleは鍵照合/credential読取前に拒否、source/count/quality/null/type/不足・余分hash拒否。未実行の実候補署名をこれらの成功で補完しない。

## PT-OPS-FSTYPE-CAND-002：失敗途中原本の未使用配置

SS343 SSC247の署名closed archive/unused-only・追加前全current verifier/追加後held FD取得境界を、SSC266/268のcurrent failed-partial/strictGC観測と組み合わせる。新SS/業務authorityや一般DONE条件の緩和ではない内部工具組立である。根拠は同SSの有限復旧正常帰還後だけ必要code-only又は別fresh resumeへ進む順序。旧1293の完成済原本を当partialへ偽装しない。

新工具1536/1537は既同Main769 helperの全byteから凍結し、元run/cutoff/activation/active・DONE無し、真正Root timeout143/現在10Unit・完全原本DBBackup/INVALIDと元permit二entry、三停止の真正receipt＋currentGCを固定照合する。新M→A/readonly batch/advisory/実heartbeat/十Ref/原本Sessionを連続所有する。署名currentのfull verifierと元全値二読→固定unused sibling/私有signatureだけnew-only配置→各親dirの同dev/ino/owner/mode/ACL・追加entry/link/size/timeの有限差分→old/new全signed inventory FDの新取得→全元値二読→DB閉鎖/実peer0/Ref/FD/bus/A/M正常帰還を要求する。全graph検査をcache/anchor-onlyに置換しない。

親dir oracleは事前値＋固定一entry、release parent nlink+1/private signature parent nlink不変、同dev/ino/uid/gid/mode/xattrs、size非減少・追加最大4096byte、mtime/ctimeは当operation開始終了内。外entry/別inode/ACL/未知時間/余分delta/再placeは拒否する。旧epoch/current/approval/全24DB/元原本/Backup/credential/native/Unit/start/stop/reloadは変更0。配置だけをcurrent切替/新Root/DONE/native/正式へ算入しない。途中又はclose不明は元ownerを隔離保持し、同slot再実行しない。

独立工具試験は親deltaとpartial binding5・once receipt2。最初の合成entry順fixtureはsorted listing契約に合わせた手書literalへ修正し、未完成工具試験の初回失敗として保全、既Production障害の成功化はない。正常/全9metadata field/ACL/foreign/null/重複/欠落/無効hash/不正framingを検証する。実行順は1537凍結→1538immutable tools/inputだけstage→1539一回unused配置→別独立全post。実source/command/実終了値/日時/hashは後続実行結果へ追記する。

秘密scan/trace/全同source native/CHR/四counter100/451正式/工程完了は別未完条件として保持する。私有raw XML/log/電文/DB/credentialはこの文書又はGitへ複製しない。公開エビデンスは非秘密数値・hash・安全な参照だけとする。
