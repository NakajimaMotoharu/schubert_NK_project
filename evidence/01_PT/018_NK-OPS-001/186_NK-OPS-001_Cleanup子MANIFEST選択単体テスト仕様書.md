# 186 NK-OPS-001 Cleanup子MANIFEST選択単体テスト仕様書

Program ID: NK-OPS-001/NK-BAT-001。Class/method: `BackupManifestReader.findCleanupClaims`/`names`/`digest`/`readAt`、`NioIo.openNames`。RD OPS-009/BAK-001、UI251、SS341 §6/7・343 §6/SSC104-PG331。Test ID: PT-OPS-BMR017～024、既存BMR001～016とbackup artifact/DB後続試験を区別する。

前提: `BackupArtifactFixture`の保持backup root、root-owned MANIFESTと公開のみの4file fixture。期待SHA256 `bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370`はProduction readerを呼ばず独立固定byteから計算済み。root/UID/GID属性はfixtureで注入し、真正VM backup root・親M/A・子Unitはこの限定PTの対象外。MANIFESTの元byteやcredential実体はGitへ保存しない。

| Test ID | 入力・操作 | 独立期待値 |
|---|---|---|
| BMR017 | 固定同run/cutoff/manifest SHAと単一正規directory | 2回root列挙一致＋claim再読後に固定manifest全値一致、borrowed root不変・owned close完了 |
| BMR018 | `.part`、別run、未知名を追加 | 選択・削除しない。正規同runだけ選ぶ。既存全file不変 |
| BMR019 | digest/cutoff/runを各1値だけ変える | 全件固定UNAVAILABLE、0件採用。期待値は固定literal SHA/UTCµs/UUID比較 |
| BMR020 | 同run suffixの短い名、同52byteでも不正区切り | 正規日時＋UUID名以外は固定拒否、fallbackなし |
| BMR021 | 2回列挙間の名前集合/親metadata変化、選択後のMANIFEST同size別digest/同名別cutoff | いずれも固定拒否。再読後のbyteを最初の結果と誤認しない |
| BMR022 | 重複名、4097 entry、null/別parent path | 4096上限・一意/保持parent契約で固定拒否 |
| BMR023 | list/read/close故障、null stream、非root UID、SHA provider失敗 | すべて固定UNAVAILABLE・結果0。raw path/cause/suppressedなし、所有者解放 |
| BMR024 | null request、割込、同Reader二並行再読、NioIo実directory listing | nullは境界NPEとして正常化せず、割込拒否、並行二件はそれぞれ同一claim/close、native listは固定dir名を返す |

これは「未信頼MANIFEST claimを選ぶ」試験であって、4file hash/owner・両backup SUCCESS row・親M/A/子advisory/DELETE許可ではない。実行command・環境/JDK/tool・対象commit、coverage、F/E/S/static、BUG/SSC、sanitized evidence path/hashは187に記録。Coverage除外なし。正常/境界/異常/例外/null/並行/再送は上記と既存BMR/Artifact PTを合わせて確認する。
