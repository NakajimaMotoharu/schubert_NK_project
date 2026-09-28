# NK-OPS-001 root現行permit事前照合 PT仕様（PG371）

対象予定class `RootCurrentPermitPreflight.verify/verifyNative`と`RootServiceLauncher.preflight`のread-only接続。RD SYS-002/004/OPS-009、UI212/251/253、SS341/342§4.2/343§6.15、SSC086～089、471 R1/D04/D05。既存`StartupPermitFiles.readIssued`の固定root-owned tmpfs現在原本/permit同一性を、Web/API root入口から読み直す。親A下・全root/Ops/schema/実prestart/FD/exec前の最終権限確認は別必須であり、この事前照合の成功でもexit30を維持。

| Test ID | fixture/input | 独立期待値 |
|---|---|---|
| PT-OPS-RPERMIT001 | WEB root snapshot、同boot UUID・release固定64hexのISSUED Permit | 比較成功。ただし許可型やreadyを返さない |
| PT-OPS-RPERMIT002 | API root snapshot、同値Permit | APIも同じ固定検査、成功をWebへ変換しない |
| PT-OPS-RPERMIT003 | 別boot、別release hash | それぞれ固定IOExceptionで拒否、原本を更新しない |
| PT-OPS-RPERMIT004 | MORNING/CLEANUP root actor、null snapshot/hash/Permit | service境界とnull契約を拒否 |
| PT-OPS-RPERMIT005 | `readIssued`欠落/INVALID/不一致、root再確認失敗 | 既存Store仕様の拒否を起動成功へ変換しない。native外部受入は別 |
| PT-OPS-RPERMIT006 | root Launcherの固定preflight順と不変exit30 | root→NSS→release→現行permit→argv→再確認。permit単体による同PID execなし |

期待値はSS343のboot/current/release fieldと独立UUID/hex literalで作る。Productionのpermit encoder/hash生成をexpectedの計算に用いない。JDK25.0.4/Maven3.9.12でBatch選択`RootCurrentPermitPreflightTest`及び`RootServiceLauncherTest`を実行し、静的/coverage、source固定後のsecurity6module回帰を記録。実A/Unit/main・成功permit発行、既存Current baselineは変更しない。結果/hashは次番号253へ。
