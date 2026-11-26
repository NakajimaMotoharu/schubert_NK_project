# APIFULL012 注入された標準描画と終了所有

NK-OPS-001、SS351・354、UI252、BUG-3981、YKT-2997、WBS-F03/2-2-b。

APIFULL012。標準sourceは固定FullProbeとno-op registrationで組み立てる。二つのlatchで描画中の操作順を固定する。標準sourceをcloseした後、元FutureはIllegalStateException、標準scrape 0、borrowed custom registryはopen。元固定独立期待と30秒の各期限を維持。

後続組立が失敗した場合、既取得のownerを解放する。開始後の終了処理はlatch解放、shutdown、30秒の順で、真終了時だけcustomとstandardを逆順に解放する。一次失敗は抑制例外より先に保持する。終了失敗は単独でも合格にしない。別APIFULL011の実JVM採取、実サービス・DB・JMS受入は対象外。
