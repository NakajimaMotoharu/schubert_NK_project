# 163 実候補BOM・boot配布・版統一限定結果

Program NK-OPS-001。RD SYS002/004/OPS009/DAT009、UI212/251/253、SS311/343、SSC086097098、PT-OPS-NATIVE-028/FULLBOM006008/ModuleDependencyBoundary/LOCK008。2026-09-28。正式runへ加算しない。

## 実artifact/署名/VM

source2905d7cdaa9490b0ccc048f602c0fa011f097aa1で実thin-JARを生成。test-only assemblerはMaven runtime dependency一覧のGAVとclassifier filenameを独立に使用し、169artifact/63GAV/23SQL、38,123byte manifest SHA a83dcee059ed6d66f74d3801ffafc30c16cc5f924b46a907fa1b66c2a45eb050。SQL期待は固定Flyway13.4一次ChecksumCalculatorでrelease SQLから算出、DBから採用しない。API runtimeにFlywayを入れずbuild-sideにのみ使用（BUG301是正）。pinはGit外private fixture Ed25519鍵から生成、公開DER44byte SHA3664698f42d75d702ef98a869241e3ff6cb312bd6d87ee90db0271c3d7a505a1、detached signature64byte SHAa0320135cb736d883034f89bf6f2020575053d320d5c2809defc76e664f9db08。OpenSSL3.5.5の元bytes検証成功。Production pin custody/approval publisherではない。

候補外固定toolとpinを専用VMへ新規配置。初回shell quote失敗はBUG304として修正前登録、Hostuid1000/uptime/target不存在/VMtarget不存在/stage保存を直後確認し、Host system/VM本体変更無し。literal quoted heredoc＋sudo bash -se/marker先行で再実行成功。raw shell envをGitへ残さない。BUG302はprobeの公開A API/checked例外契約のcompile是正、期待値は不変更。

BUG303はSSC086既定Aのboot配布漏れ。独立4行oracleのRED（32PT/F1/E0/S0）→固定boot-only/no-truncate f!追加→06:05:10 GREEN32PT/static0。old RED/new GREEN別provisional/hashへ退避。VMに初回tmpfiles install→実rebootでM/A空/root0600/link1、共有親root0755を実測、実行中修復無し。新bootでもNative027三原本hash不変。snapshot pre-PG315-20260928-0539/private diskはGit外であり業務backupではない。

NATIVE028は真正RootStartupContext/MORNING＋実M/A＋固定fixture pin署名のmilestoneまで成功したが、候補全BOMはRWと実host RO（bind/remount ro）の両方で非成功。MainPID0/ExecMainStatus1、明示stop後固定cgroup leaf不存在、currentは旧pgpt-native-301のまま。RW試行にも後述GA不適合があるため、RW拒否原因をRO条件だけへ断定しない。新版のvalid BOMでRW→ROを同bytes比較する再試験が必要。

## BUG305の原因・修正

独立JSON/ZIP検査で136jarに未知/duplicate/nested jar/Class-Path列挙外/foreign SQL無し、共有3GAVのroleと全複製size/SHA一致を確認。一次strict parserの各fields/dependencies/artifacts/migrations単体読取は成功したが最終inventoryは拒否。GA matrixにCommons Logging1.3.5/1.4.0、JSpecify1.0.0/1.0.1が存在。Verifier拒否が正しい。SS/期待を実物へ合わせて弱めず、SSC098先行後に既存Web採用1.4.0/1.0.1を親へ統一。全子property/Web局所上書きを除き、親3pin＋子上書き0の独立literalを既存境界試験へ追加。assemblerもmanifest/署名前にGA重複拒否を追加する。

06:20:45限定49PT（Storage8/Bootstrap24/Batch17）F-E-S0/NullAway/SpotBugs0、collector105全成功。provisional/BUG305-pins-limitedにselected4XML/3coverage/3static/全POM・test/log hash、clean無し累積execは正式coverage認定に使わない。POM/annotation/logger/security横断のため次に全6 clean2217PT/report/staticをsource固定で実行し全採取する。

## 保全・未達

provisional/NATIVE028-refused/inputに公開manifestを保全。旧RW exec SHA58dfa5ffbe7e160bede47c14c54dd15e06a71361b9a774818ccd74faf9bff28f、旧RO-refused exec SHA5648d4ea0721e954d29288aeb697fb6234c54756995f3aeff92eb0e26d4a443d（private work/pgpt-native/PG315、正式へ合成しない）。旧probe class SHA43daf49da1b253af972ed31b0a4a83286238272f568c65a3a13089da7232bbc4。新tool sourceを0.1.0-PG316/新signature固定入力へ進める。旧RO候補/署名/原本を上書き・削除しない。

RootReleaseAdmission actual factory/schema、trusted Production署名原本発行・activation/M/A全Unit・INVALID、initial V023、全親backup/cleanup/transfer/expiry、permit/業務main/実NKCHR/R2R3は未達。FullBOM37branch等を除外しない。native/fixture/countを全体完了率へ換算しない。各修正commitは本PG316保存のsource/manifest hashとgit historyから追跡し、直接限定済の台帳を全完了扱いしない。
