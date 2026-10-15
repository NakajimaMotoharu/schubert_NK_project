# 設定読取・credential位置/IDの個別受入

2026-10-15、WBS-P003-07、Production a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25/PG2802。固定Test snapshot25e571bd1、実全3702/542suite/1643Main・静的六module0・F/E/S/flaky/not-run0・同Main/resource/debug byte/CRCとnative28を001/112・公開PG3302から参照する。原全体のStorage23suite163caseはPG3316 actual0の原XML/hash/source照合で同一性確認済み。今回の監査は新実行・新PT・配備・秘密読取を伴わない。

## 全scopeと正本

485専有四path＝NonSecretConfigSource（非実行interface）、ServiceConfigFiles（Service/Contents/Snapshot/Io/NioIo含むouter family）、ServiceCredentialId（Kind含む）、ServiceCredentialLocation。三実行familyのLINE/METHOD/CLASS/BRANCH miss各0。共有classは485の所属を変更せず、OwnedTransferDirectory/DirectoryCalls/ResourceScopeはこの境界からの利用を確認するが他ownerの製造費を加算しない。専有requirementIds空、終了依存P002-02は同a9 ACCEPTED。

origin/main 756a891d9のSS343 §4/6/6.1/6.2/6.4・SS342 §4.2、既018/064・070・076のPT仕様を照合した。SS343の現local byteはorigin/mainと完全一致。SSC080の非秘密envと固定設定source、SSC081の通常service別必須5 IDと位置入力≠保持inode認証を適用する。WBSの見出し「private directory/file生成」はこの専有四型が作成権限を持つことを意味しない。**ServiceConfigFilesは読取専用、位置型/ID型も生成・修復・秘密配布をしない**。実directory生成、ACL/readonly、systemd配布、secret readerの受入は各ownerに残し、当leaf成功で代用しない。見出しを根拠に無指定の作成処理を追加しない。

## 独立期待値と原実行Test ID

各IDは下記classと番号に対応する実method名でPG3316の元XML case（class＋元ordinal＋case名SHA）へ一意に接続する。原XMLに含む引数値・properties/stdoutは公開しない。

| class / Test ID | 入力・操作・独立期待値と後条件 |
|---|---|
| ServiceConfigFilesTest / PT-OPS-CFGFILE-001 | temp root0750/三file0640、手書き公開UTF-8 common/API/Web各literal。API/Webがcommonとそれぞれの固定名だけを返す。expectedをread/Production codecで生成しない |
| CFGFILE-002 | api.yml欠落→symlink→directoryを独立に配置、各UNAVAILABLE、内容/pathを診断へ返さない |
| CFGFILE-003 | 0/16384/16385 byte、UTF-8 C3 28、file0600。内部bounded readerの1～16384だけ受理・strict decoder、16KiBの独立整数境界。YAML文法/secret key/重複key検査は上位設定parserでありここで認定しない |
| CFGFILE-004 | hardlink2、root0700、owner/group不一致を拒否し、正常属性に戻した公開literalだけ返す。readerが権限修復をしない |
| CFGFILE-005 | owner/group/mode/nlink/dev/ino/size/ctime各欠落、型・独立属性変造、nlink0/2、device負値/別device、inode0、size負/0/16385、wrong owner/group。固定UNAVAILABLE、genuineの返値deviceは実fixtureの独立unix属性と一致 |
| CFGFILE-006 | root/identity/calls/io/serviceとContents各nullは内部NPE precondition。32並行readは手書きWeb literal、owned close故障は成功返却せず保持handle全close。NPEを正常結果へ変換しない |
| CFGFILE-007 | 実held inode＋package内Io故障portでroot/file ctime変化、最初/最後channel.size変化、zero/short/overflow read。正常fixture literalと全故障UNAVAILABLEを確認、read中の同一inode・size再照合とbounded IOを維持 |
| ServiceCredentialIdTest / PT-OPS-CREDID-001 | API固定順 db-api,mq-api,api-context-aes-current,api-inbox-response-aes-current,operation-hmac-current、前2PASSWORD/後3KEY。SS343/Unitからの手書きliteral |
| CREDID-002 | Web固定順 db-web,mq-web,web-session-aes-current,web-revoke-aes-current,web-log-aes-current、同じ2/3種別。APIへWeb secretを追加しない |
| CREDID-003 | 全10 enum重複なし/各service所属、返却List変更不可。callerによる任意filename、未知IDやpreviousの暗黙探索なし |
| CREDID-004 | null serviceを内部NPEで即時拒否、空catalog等へ変換しない |
| ServiceCredentialLocationTest / PT-OPS-CREDLOC-001 | 公開合成Mapの絶対正規化Pathを保持、無関係PATH値は保持せず、toStringは固定REDACTED |
| CREDLOC-002 | 必須欠落/空/相対/rootを固定IllegalArgumentException診断で拒否 |
| CREDLOC-003 | lowercaseと大小文字重複alias、..、NUL/CR/LFを拒否、secret/pathを失敗診断へ含めない |
| CREDLOC-004 | 手書き4096文字受理/4097拒否、null key/value不正、null Map自体は内部NPE。未知のsystemd prefixを推測しない |
| CREDLOC-005 | 8thread×32個のfresh Mapが固定公開Pathへ一致、不変snapshotを他readから変更しない |

ServiceConfigFiles全read/checked/control flowを確認：root保持→前属性→common→service各entry/READ channel→前後size/metadata→root後属性→全close完了後Contents、全既知Storage失敗を固定UNAVAILABLEへ縮退する。NioIoはREADのみ、checkedは属性型/正確mode/link/device/inode/size/ctime、Snapshot/Contentsはimmutable。未知Runtime/Errorの正規成功への捕捉なし。production()は固定/etc/schubert-nk/root:schubert/defaultcalls、任意外部path入力の公開factoryなし。NonSecretConfigSourceのthrows/null契約は同実装を通じて検証する。

16実methodは同3702の内数、新16加点ではない。全型/内部型/全methodのmiss0と静的六0は当source原全体に接続する。再送/DB transaction/MQ/業務mutationは当純catalog/位置・read-only config処理に非該当。IO channel/保持directoryの全所有closeは当正常/故障/並行Test、共通優先順位は受入済P003-08と全3702で照合。ローカルfixtureのmode/属性検査は本番systemd ACL配布成功の代用ではない。

## 三criteriaと適用

contract＝上の全16 ID・承認SS/既PT仕様・独立期待値・結果/資源境界。scope＝485の四path/三実行＋一interface/全含有型・共有参照。quality＝同source全実3702/静的六0/全FES0・当family四miss0・native28/全1643Main79resource/debug同byte、独立正常/境界/異常/null/並行/故障/close。原whole command/OS/JDK/commit・coverage/hashは公開PG3302 manifest、個別原Test/XML hashはPG3316 manifestへ接続。strict前/候補/後auditを通った場合だけ当一leafをACCEPTEDにする。全体残603L115M0C470B/正式1964PT53scope/工数null/QA051final保留・ITST未完・原/v3費用は変更しない。
