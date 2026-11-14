# 六master table絶対ownerを既column照合へ追加・独立仕様

NK-MIG-001、RD MIG003005006/MIG-DAT005/DAT004/TST、UI242254、SS311331343。BUG2961/YKT2490: SS331 3.2 nk_ownerはSchema/object ownerであり、既九属性/NN/sequence検査が相対owner一致だけでは別role所有tableを拒否できない。内部catalog前条件補足でRD/UI/DDL/role/grant/承認済DIF/QA変更なし。実DB資格は未実行のまま。

既六固定SELECTの第十projectionにpg_catalog.pg_get_userbyid(c.relowner)を追加し、全66物理columnでgetString(10)を一度読みnk_ownerとの完全一致を検査する。NULL/空/大小文字/空白/別roleを拒否し補完・trim・権限変更・SET ROLEをしない。WHEREだけで判定したとみなさず取得値をJavaで検査する。元九projection/六table順/66行/既descriptor/NN8/sequence9と全resource/primary/cleanup契約を保持。実DBのrole実体/権限/grant/孤立sequence/index-triggerは別未受入。

Column独立matrixの全66行に手書きnk_owner第十値を付加、generic全field異値/null/三型fault/cleanup/有限並行試験の対象へ含める。PT-MIG-COLUMN025は六table各行のNULL・空・別role・大小文字・前後空白を固定入力で拒否し、query prefix/Result-close/table終端/Statement-closeを照合する。親Targetの既column rowsも第十fieldへ更新しCOLUMN_CATALOG_FIELDS10、catalog getters66x10+75x7=1185を独立算出。SQL94/Result76/ownerclose17/auto12/fetch4/scalar56/Game10gettersと業務内容の意味は不変更。PT-MIG-TARGET035は全66行誤owner/NULLでstagingCTAS0、各phase三型faultは既generic matrixが第十fieldまで行う。既Column24/Target34の期待値を削除せず新2追加、既940＋2=全942/45Main47Test65physicalを一source/一execでRootNullAway-lint-CS-SB-PMD個別適用/CRC-init/既定と無filter全Code四100により再認証する。旧Main44/他Test45同byte、実DB原本/Backup/key/VM/server/native/HOLDには触れない。

追加不足1.8/5.4/9.9pp cap10、元費用/SV/各群開始と未較正残397.324/837.386/1643.415は保持して当不足分だけ一度追加・完了時減額する。専有実費token null、旧940は再認証で新成果へ加算0。正本625/元190正式受入と正式1964/53/工数nullは本限定製造で増やさない。BUG2961は通常host限定再試験の根拠と実DB未受入を分離して閉じる。
