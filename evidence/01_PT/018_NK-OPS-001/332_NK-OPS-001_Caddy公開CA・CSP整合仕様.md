# NK-OPS-001/NK-WEB-001：SSC182183公開CA・CSP整合

Program/class/method：NK-OPS-001 `CaddyPublicConfiguration.file/requireFileMetadata/tls`、NK-WEB-001 `WebSecurityHeaderWriter.writeHeaders`。RD SYS-006/FUN-001/AUT-004/現行互換、UI222226/264、SS342352355/SSC182183、BUG688689/YKT493494。Web既存最正仕様は015001のWEB091～094。Current baseline/oracleは変更しない。

| Test ID | fixture・入力/操作 | 独立期待値・観点 |
|---|---|---|
| CA461001 | literal POSIX metadata、UID993/GID978/single-link/size1,631,65536、mode0600/0640/0644を公開CAへ、設定はUID0/978 | 公開CAのみ3mode合格、設定0640だけ合格。0600はより厳しいowner-only。期待はSS342 literal、Production算出0 |
| CA461002 | owner0/gid0/link0,2/size-1,0,65537,Long.MAX_VALUE、未知/dir/symlink/write/setgid/setuid mode | IOException拒否。所有者/容量/型/権限をrepairしない、unknown値を正常化しない |
| CA461003 | null metadata | dereference前に契約拒否、NPE catch正常化0 |
| WEB091..094 | GET/HEAD/POST・全route/status・既存競合/重複header、response異常/null、100並行response | 独立固定Current CSP `default-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'` と他header完全一致、同origin/default-src継承・inline/eval/external不許可を維持 |
| CA461-NATIVE/CHR-A01 | fresh固定同source full→署名候補/正規code-only配備→外部Morning/同Root普通API所有保持Web/Caddy | 実固定root.crt0600/single-link/UID993/GID978・祖先/noACL/inode前後/CA期限属性/hostnameを維持、実同peerTLS200→原本DONE/intent/outer0or10。共通Current A01 driverでDIF001/QA045 titleのみ、それ以外完全一致 |

既存正常/境界/異常・guard/再送/所有者退役は選択MorningCaddyReadinessTestと全6回帰で維持。fixture private key/credential取得0、公開CA権限の書換え0。コマンドは333/manifest、環境host Linux/JDK25.0.4/Maven3.9.12/Node24.19.0、guest Ubuntu26.04/PostgreSQL18.6/JDK25.0.4、対象commitはsource固定後全回帰へ別記。選択結果を全coverage100/native合格へ換算しない。

QA047限定復旧の追加Test ID PAIR461-POST/PEERS/BINDINGS：actualPG460/source8e97・INVALID20/3intent/DB291を固定、独立literal旧12＋当4＋current=17post、全各欠落/未知/逆順/巻戻し/全phase・同primary/Error/null/owned close302、実watch改変14、全固定binding preflight。Nativeは真正M/A/DBで全291全14/23business/原本pending/Backup/Transferを保全し、3typedintentのみ退役・旧16record保持/全9kernel空/全owned正常帰還。CODE461-NAMES：同source code-only配備の引数/17literal各欠落/未知/OLD source/digest/OLD/NEXT/SAVEを60独立assert。新authority/DDL/直接子startを工具assertで許可しない。BUG690691/YKT495、旧failed工具/旧BUG544は成功化0。
