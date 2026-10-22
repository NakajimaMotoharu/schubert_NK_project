# C01 Caddy静的変換・個別criteria仕様結果

## 是正後の実結果（2026-10-22）

修正2b7659218をpushclean後、6948を一回実施。元IPv4は再実行せず固定JSONのsemanticだけを読取検証、未実施IPv6のplain adaptは11:10:18.078910～11:10:18.102458 UTC・actual exit0、before/exit/input/outputを保存してから全独立semantic成功。tool SHAは修正commit blobと一致。公開 `evidence/provisional/PG6948-c01-static-adapt-v1/manifest.json` SHA256=7df814760d8a297d08c55f3623d5c6db8de56e31ef37004668dc1087c8323c4b、元v6終了receipt=8f261bc086ad652a9a027665c255eb8f87d6eb06dcc05809e2509f5675e7ea2a、begin/exit原byteも同folderへ保存した。

別のread-only postは元receiptのsource/command/input-output/tool commit hash、public/private JSON同値、両出力semanticを照合してexit0。管理四/pyflakes0に加えて実vendor schemaと未実施v6の真正終了まで確認できたためBUG1635/YKT1388を当tool scope CLOSED。初回driver1・旧v4 child exit/time未保存はそのままで、未知をPASSへ変換していない。

数量は当元Java3件の参照（再実行0/加点0）、静的artifact内容検証2件、direct exit記録付き新static実行1件、local contract/scope二criteria根拠である。2件の新規実行PASSと表現しない。XDG state生成無し、CA/keyのprovisionやdaemon/socket起動の命令は発行していない。WBS-C01 qualityは全fmt/validate/実効/TLS等が残るので未完、canonical受入加算0/正式1964/53/工数null/PTALT0を維持する。

両stderrの警告は各4件：explicit Forwarded header冗長のvendor注意3件＋format差1件、未分類0。原stderrは自己slot private保持/publicはhash/有無だけ。SSがpeerからの明示再構成を指定しているため、注意を消す目的でheader設定を削らない。format/配備validateの未達を黙って合格扱いせず、rendered配布物の後続品質として記録する。plain adaptの成功をvalidate/provision・実公開入口の成功にしない。

是正準備追記：元失敗を82f5d81c5へ保存push。公式tag certificate_authoritiesへ限定是正し、管理fixtureの自己整合だけでなく固定hashの実保存IPv4 JSONも管理で読取り、全独立semantic条件が成功した。管理四/pyflakes0、新CLI実行0。旧IPv4は静的artifact内容の資格だけで、実行exit/time未保存は依然UNKNOWN/実行PASS加点0。

新IPv6はbegin/source/command/input/binary/tool hashを先に保存し、返却直後のactual exit/完了時刻/output hashをsemantic検査前に保存する。未完begin/inputがあれば新起動しない。既exitがあれば同原結果の読取だけで再起動0。raw child exit0だけをPT PASSと書かず、semantic条件を満たした後に初めて当caseの確認結果とする。現時点ではIPv6未実施、BUG1635/YKT1388 OPEN。

## 初回tool失敗（是正前保存）

pg6948/session5124はIPv4 JSON保存後、verifierのPKI field cas誤認でKeyError/driver1。管理三は誤schema自己整合で成功していたためBUG1635/YKT1388を修正前登録。元driver e24ab242/私有original-driver.py、input f33eb2f491b7cb1de8cb68c5460382870ceaef82622fe1e79330838960026237、JSON28f9a4df19349dc877a1a9765bdd3a4d6615fdb50633d68287b84531416395cfを保全。child zero check通過は制御流上分かるが独立exit/time receipt未保存なのでactual child exit/startはUNKNOWNのまま実行PASSへ加点しない。新static二件PASSは未成立、IPv6はinput作成前で未実行。

[公式2.6.2 PKI型](https://raw.githubusercontent.com/caddyserver/caddy/v2.6.2/modules/caddypki/pki.go)のjson tagはcertificate_authoritiesでありcasではない。SS/template/期待するtrust無効化を変更せず、このvendor field名だけを正す。旧IPv4は保存outputの独立内容検証だけに使い、回収目的の再実行0。未実施IPv6は新begin/終了receiptをsemantic検査前に保存して一回実施する。旧driver1/子exit未保存は後の成功へ変換しない。実VM/Unit/TLS/鍵等への操作0。

WBS-C01既枠.25/.6/1.5pp、群1754で先行固定。SS342§3/SSC178、UI251、ownedArtifactはCaddyfile.template一つ。全実環境HOLD/QA051final/Current baseline/全Main/Test不変更。PGは論理template全体・許可directive・固定IP/TLS/proxy/header/timeoutを正本へ照合、現時点で不具合の発見無し。actualCaddy起動のPG/codeや真正readinessの完了とは別。

## PT着手前判定

RUN_NORMAL、command=既full PYTHONPATH下 `python3 -B tools/quality/pg6948_c01_static_adapt.py`。新only W/pg6948-c01-static-adapt-v1、原e7d64/4222資格728682a9を固定。既CaddyPublicConfigurationTest三methodの当元case/hashへ一意joinし、再実行しない。現artifact/SS正本origin/main8b919/当original source archive/485全owned scopeを読取照合する。

追加の静的caseはPT-C01-ADAPT-001/002。自己生成slot内にlocalhost IPv4と文書用IPv6（2001:db8::1）のrendered inputだけを作り、既binary Caddy2.6.2（SHA256=678c1849799e6d81c7cfbe63cebb8f92400cb70a67fc9f601697cb8ce7cdfa4a）で `adapt --config <own file> --adapter caddyfile` を一回ずつ行う。15秒上限、argvにrun/start/reload/validate/--validate無し。子envは固定最小値・自己slotのXDGだけで、environ表示/実CA・鍵/Unit/port/VM/原本DBへの操作を含まない。

[Caddy公式CLI](https://caddyserver.com/docs/command-line#caddy-adapt)は通常adaptをJSONへの変換・終了、--validateを別のload/provisionと区別する。後者と実TLS動作は今回行わない。2.6.2自身のhelp/versionも事前read-only確認済み。新inputへ固定IPだけを置き、実公開IP/署名/秘密情報を取り込まない。

## 独立期待値

SS342の唯一caddyfile論理blockをcomment/余白以外で完全一致させ、JSONのadmin off・IP55160のみ・redirect off・host trust書込off・internal issuerのみ・唯一loopback8080上流・2/30/60/60秒transport・四固定header/Server削除・Forwarded値のpeer再構成/trusted_proxies無し・直接file/media handler無しを個別検査する。

body 2MBは2,000,000 byte。導入2.6.2の[requestbody parser](https://raw.githubusercontent.com/caddyserver/caddy/v2.6.2/modules/caddyhttp/requestbody/caddyfile.go)はgo-humanize ParseBytesを使用し、その[SI/IEC単位定義](https://raw.githubusercontent.com/dustin/go-humanize/v1.0.0/bytes.go)ではMBは1000の二乗、MiBは1024の二乗である。変換結果を見て期待値を生成せず、上記原則から定数を先に固定した。実HTTPの境界受付結果を測ったとはしない。

管理Testは手書きJSON fixtureの両IP正常、広域bind/admin/trust/redirect/2MiB置換/file_server、上流/timeout/Forwarded/Server/issuer改変を拒否する。これらは管理検査であり新Java PT/coverageには加点0。実adaptのcommand/時刻/終了/元input-output hash/警告有無と当元三caseをmanifestへ記録する。

## 判定の境界

当静的変換はまだ未実行。実行成功後もqualityの全fmt/adapt--validate/validate・実daemon/TLS/active config/所有/停止後条件は未受入。正規Root/実public入口の代替ではなく、PTALT例外完了/実測四100/正式1964/53/canonical17/工数nullを更新しない。未知/失敗は保全し、成功化・再実行を自動で行わない。
