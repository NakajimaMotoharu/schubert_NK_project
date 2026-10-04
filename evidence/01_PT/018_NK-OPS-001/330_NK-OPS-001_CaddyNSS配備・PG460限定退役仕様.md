# NK-OPS-001：SSC181 Caddy NSS配備・PG460限定退役仕様

関連RDの既存Security/運用要件、UI226/242、SS342343/SSC168179180181/QA047、BUG685686687/YKT490491492。上位業務仕様/Current baseline/厳密identity gateを変えない。Production sourceは8e97eb9138828010926cd47fd10868d8a2d54f11、工具dirty SHA/classをmanifestで別管理する。工具assertはProduction PTへ加算しない。

| Test ID | 対象・事前条件/操作 | 独立期待値/正常・境界・異常の根拠 |
|---|---|---|
| PAIR460-PEERS | Pg460CapturedPeers.watch、実PG459の両Root/ordinary/同親/info/socket観測を入力、source/pid/ticks/generation/readinessを改変 | 固定実Unit世代と明示info5/UID/GID/groups/caps/NNP。欠落・未知・他世代を拒否、旧PIDを生存と推定0、14assert |
| PAIR460-POST | Pg460Known30PairRecovery.retirementStage/fullyRetired、固定初期16→typed3退役後13・旧保持8をliteralで列挙 | 旧8＋当4＋currentの13を独立構築、全13各欠落/未知追加/飛越/巻戻し/WEB→API→publication順/未実行・IO/Runtime/Error/同primary・secondary/A-closeを278assert。旧9のpostを流用0 |
| PAIR460-NATIVE | 正規同schema027/INVALID/e8cce…/281全14列/原本pending、真正M/A/限定DB/advisory・全9終端、14私有capture/hashと実終端を照合 | capture前/変異前/typed各gate/後条件で原本/Backup/Transfer/23business/281全列・旧記録byte/inode不変、3intentだけ型付き退役、current INVALID・newpermit/start/DDL0、全owned正常帰還。誤recover引数は入口拒否で変異0 |
| NSS460-LITERAL | Pg460CaddyNssPreparation.removeMember/groupIds | 固定ASCII4field/newline/groupwww-data gid33、caddy一件だけ除去・other member/primary/他row不変。CRLF/終端欠落/空/未知/重複/不正gid/duplicate ID/未知member字句を拒否。gshadow password/admin列は不変更。25独立assert、expectedはliteral文字列でProduction算出0 |
| NSS460-FIXTURE | Test native-fixture、root私有chrootのliteral passwd/group/gshadow/NSS、実`gpasswd --root <fixture> -d caddy www-data` | group/gshadowは独立after literal、group-/gshadow-は独立before literal、実CaddyNSSは前後不変、他member保持。32assert（host25を含む、別Production試験と重複算入0）。fixture保全/実対象変更0 |
| NSS460-NATIVE | 管理main無引数、当boot/source8e97/既存署名PG459・退役済13/全9kernel空・DB281/原本pending、実NSS993/978と余剰33を認証 | root私有before-image同期、真正M/A/DB下で`gpasswd -d caddy www-data`だけ。group/gshadowの当member以外・passwd/NSS/primary・全13startup/全原本Backup/281/23business/Transfer不変、自動group-/gshadow-旧内容も保存、id groups978のみ・全scope正常帰還。未知は隔離/保有、無差別usermod/復元/permit/start/DDL0 |
| NSS460-RESTART | 上の管理終端証拠を確認後、既存signedPG459を再配備せず外部Morning一度・同owner/API保持Web/Caddy | actual専用kernelgroups=[978]、same-peer/generation/identity/socket/info5/TLS200、保持原本DONE/3intent退役・親全outer0or10。同source native coverageとCHRは別、受付0/単体readyを全体合格0 |
| CHR460-A01 | common Current captureLoginDisplay/desktopOptions、NativeNkA01Capture→allowlistedHTTPSの外部NK、同 pinned Chromium/1366×768/ja-JP/AsiaTokyo | Current artifact全JSON一致＋承認DIF001/QA045 titleだけschubert NK - ログイン。csrfをTOKENへ正規化、公開CA/hostnameは別同source nativeTLS witness、他case/full24 gateは未実行と明記。DB初期化/既存Application起動停止/基準改変0 |

Command：`javac -Xlint:all -Werror`（固定guest16base＋当同署名Jar/lib）→独立Test→new-only root0500/0400/hash配置→guest Java `--enable-native-access=ALL-UNNAMED`、詳しい世代/source/run/終了コードは331/manifest。OS Ubuntu26.04/PostgreSQL18.6/JDK25.0.4、gpasswdは実passwd package/tool helpで--rootを確認。v1短flag-R誤り（実target変更0）は不合格保全、正常期待値を変更しない。

全Production coverage100/正式認定は未達。工具の純判定・私有fixtureは実親/全資源/CHRの代用でない。raw NSS/gshadow/原本/startup/dump/spy、credential/token/sessionはGit外root私有に保存し、通常証跡にはTest ID・安全flag・公開hash・退出結果だけ採用する。
