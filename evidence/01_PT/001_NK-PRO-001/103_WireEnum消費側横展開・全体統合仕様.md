# WireEnum消費側横展開と同source全六統合

実結果（2026-10-14）：PG2640/session56826 actual0/Maven0、04:33:53.360644Z→05:00:03.030207Z/1569.669563秒。PG2641/session54760独立actual0/3664PT-540suite-1643Main/static六0/FES-flaky-rerun-notrun0、全20対象suite当XML/hash成功。PG2642/session56737 actual0/現十point/latest九/all1643Main/resourcebyte/CRC-session0/再採取0。source911b16e0e/Productiona79不変。BUG1244/YKT1010対象完了、実残788line/156method/9class/542branch・全100未達、正式1964/53不変更。以下の「実行中」「未完」は着手時履歴で、当対象終端は本段と公開wire-oracle-full-native-manifestを優先する。

BUG1244/YKT1010、NK-PRO-001/PT-PRO-001-H01・T04。共通code許容集合・name/wire/profileの独立oracleはHeaderModelTestのUI232§7固定12行、18semantic型はProtocolSemanticTypeTestのUI234～236/SS333/351固定表。共通契約を消費側Production methodからexpectedへ逆算しない。共通表の反例は2632三件、2636全36件、通常Protocol2634v2の82件で再試験済み。

消費側の`values()`は入力の網羅列挙としてのみ扱う。wireValue/usesSuccessProfileを使用するconsumer test単独で承認許容集合の保証を主張しない。共通独立表が同一sourceの全六runへ含まれることを必須とし、固有業務期待値は以下で別判定する。全体閉鎖は全対象のfresh XML/source資格が揃ってから。

| 対象Test class | 個別判定・独立根拠 | 判定の残条件 |
|---|---|---|
| HeaderModelTest | 是正対象。UI232固定12件/name/wire/profileと未知0199/9900/9999。三mutationを拒否 | PG2640へ同whole Test file統合 |
| ProtocolSemanticTypeTest | 是正対象。18固定表/件数/name/wire/required/optional/未知。元round-tripは補助変換契約のみ | PG2640へ同whole Test file統合 |
| AuthenticationErrorProfileTest | DATA expectedはUI233/234～236の独立TSV offset/length、space/zero filler、LOCKED Retry900/0107 PROCESSING literal。values/profileは入力選択のみ | 新共通表＋当fresh XML |
| LayoutMetadataTest/LayoutFieldCatalogTest/typed mapper | UI233/234～236転記TSVがレイアウト数/field属性/offset/lengthの独立根拠。Production catalogをoracle原本にしない。semantic意味は18固定表へ結合 | TSV hashと当fresh suite/source |
| ApiSessionInvalidTest | web158はliteral12wire/12HTTP status表。既に許容集合とHTTP固有結果が独立。非該当 | 当fresh XML |
| SessionOperationTokenLifecycleTest | SUCCESS/IDEMPOTENT_SUCCESSの実固定token/時刻/保持、他codeのcomplete拒否。profileは共通固定表へ依存、operation結果とDB後条件は個別fixture | 共通12行＋当fresh XML |
| AuthenticationServiceTest | Failure許可AUTHENTICATION_FAILED/LOCKED二literal型、retry1..900、独立DB/credential消去。valuesはその他拒否入力 | 当fresh XML |
| LogoutInboxServiceTest | failure許可SESSION_INVALID/TEMPORARY_FAILURE二literal型、他全拒否。保存scope/metadata/SQLを個別検証 | 当fresh XML |
| UserCommandServiceTest | 成功DATAはUI236 offset0/12/21・length12/9/3のliteral byte。結果許可VALIDATION_ERROR/NOT_FOUND/CONFLICT/RESOURCE_LIMIT固定集合と成功profile条件 | 共通12行＋当fresh XML |
| UserMutationReplayServiceTest | adm029 definite許可はlayoutごとの固定code集合、transient SESSION_INVALID/FORBIDDEN/TEMPORARY_FAILURE、保存状態ERROR/no reference/再送有無とUI236 wire helper。code byteのみ共通12行へ依存 | 当fresh XML＋共通12行 |
| UserQueryReplayServiceTest | detail NOT_FOUND/list RESOURCE_LIMITと三transientのliteral許可、ERROR/none・独立wire record/fillerと再送結果。code byteのみ共通12行へ依存 | 当fresh XML＋共通12行 |
| LogReplayServiceTest | UI235 wire fixtureの0000/0200/9001固定byteと件数/範囲/ERROR保存。四failure許可はliteral型集合、code byteのみ共通12行へ依存 | 当fresh XML＋共通12行 |
| MediaReplayServiceTest | med051 persistent許可9001/0104の独立literal byte、layout限定/descriptor無し/ERROR保存。その他許否も固定型集合 | 当fresh XML |
| ScenarioReplayServiceTest | codeごとの許否は固定型集合、UI234 field/record/FILE/INLINE goldenを使用。code byteのみ共通12行へ依存 | 当fresh XML＋共通12行 |
| QuestionQueryReplayServiceTest | qry014 detail NOT_FOUND/list RESOURCE_LIMITと固定transient、scope/ERROR/独立filler/wire、code byteのみ共通12行へ依存 | 当fresh XML＋共通12行 |
| QuestionMutationApplicationServiceTest | 固定kind→結果code/time、二回処理のmetadata不変、ERROR/no-reference等SQL literal後条件。profile選択のみ共通12行依存 | 当fresh XML＋共通12行 |
| QuestionMutationReplayServiceTest | 固定cancel/delete code/state/time・再送0200規則、cipher不変/reference/statusと独立wire helper。profile/code byteのみ共通12行依存 | 当fresh XML＋共通12行 |
| QuestionCommandServiceTest | qry034 fixed switchの成功CANCELLED/time・0107 PROCESSING/COMPLETED/ERROR/no time・0104/9001 reference無しを独立列挙 | 当fresh XML |

検索条件はResultCode.values/usesSuccessProfile/wireValue、semantic18型及びLayout/typed mapperのTSV入力。Production Main不変更。上表の非該当は共通型の未承認追加を許すという意味ではなく、共通独立oracleがその不適合を拒否し、個別testは消費契約に限定するという責務分割。

PG2640実入力TSV hash: layouts-ui233=`c4f290595f5cabf19c11877e2dea95627b4d42490116431bac3bfde58950d711`（comment込み65行）、fields-ui234-236=`b07bd90705a4761ebcc97b859bd495dadaf26501fcee3b60c4edd72474a4811b`（394行）、named-types-ss323=`9529fce86672b27a435665331648110521be6f59c5fe3fe5ca516df5234c7a76`（65行）。三つとも001/evidence/inputの独立転記原本と全byte同値。payload-golden-ui234-236=`49bb76ec610216042f8e53ed548f4d5e52707a8bbf930a9fc6c93300dfa24839`（68行）はtest/resourcesの独立golden、別のevidence/input同名原本は無いので同値と主張しない。各TSVが同凍結sourceに含まれることを2641で照合する。

必要統合PG2640: snapshot911b16e0e7fabb2a3f7b2c11f6b25ca666ef60c6、Productiona79b45b5858a186fa82bec1ff36882271ab996a4。期待3664PT/540suite/1643Main/static六0、FES/flaky/rerun/not-run0。追加はsemantic一Testのみ、Header既methodのoracle変更は件数加点0。各module count=protocol82/storage163/bootstrap298/api969/web886/batch1266。旧3663と82を合算せず、当実全XMLを資格付けする。

command=pg2640_wire_oracle_group_full_six.py一回→pg2641_wire_oracle_full_qualified.py→pg2642_wire_oracle_native_qualified.py。当sourceの全Main/resource/Jar member byte同値・現current十point/latest九CRC/session資格を再照合、旧0fd nativeの輸入0。Production/起動/停止/Backup/ADMIN/reload/公開再演0。API/batch coverage全100未達を維持し、本統合でPGPT/IT/ST完了を宣言しない。

群開始event0694、WBS-K01.01着手前0.75/2/5pp、元原/v3見積り不変更。個別実費/実tokenN/T不明null、共有使用30/rem70をtokenへ換算しない。実結果・hash/coverage・全対象XML・関連commit・再試験証跡は終端後追補する。現状態=実行中、横展開全完了未認定。
