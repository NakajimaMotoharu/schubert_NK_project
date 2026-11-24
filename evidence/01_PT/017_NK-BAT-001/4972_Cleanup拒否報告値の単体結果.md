# Cleanup拒否報告値の単体結果

2026-11-24 22:58 JST、PG44034。JDK 25.0.4。製品Core `4d3a0f69c8241f6dd3dbe67e5fdf7b067cd98349`、試験commit `847f6c23d0c361a7521d0d0ed095edc113a1f423`。正規Batch JARから明示10物理を抽出し、対象二型を一回のexecで計測した。

PT-BAT-REJVAL001～005は全件成功。失敗、エラー、skip、未実行各0。7区分の保持と形状拒否、完了・未完・skip・不存在の区別、runとstepの一致、等値・hash参照、診断の固定非公開表示を確認。行32/32、メソッド14/14、クラス2/2、分岐24/24。書式・Checkstyle・PMD各0。合成初回4件の元証拠は保全し、四指標を足し合わせていない。DB接続、実SQL、親の回収・削除、同一source全451は別。

- [当manifest](evidence/PG44034-cleanup-rejected-pure-report-final/manifest.json) SHA-256 `84cdfdf9356c0da2df7557708d22253e23791bee6cb5d4a1ff977b564d4080f6`
- [基本四条件](4970_Cleanup拒否結果値の単体仕様.md)
- [等値と診断](4971_Cleanup拒否結果の等値と診断単体仕様.md)
