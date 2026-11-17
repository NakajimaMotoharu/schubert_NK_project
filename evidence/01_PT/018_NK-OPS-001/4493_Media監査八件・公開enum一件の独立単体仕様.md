# NK-WEB-002 Media監査 whole9仕様

BUG3176/YKT2645、RD FUN005～007/MON004・UI252・SS333351352354。追加発見.30/.80/1.80 cap3、主担当P00905。元MediaAuditContractTest8 source/独立JSON catalogを保持。新PT-MED-AUDIT-RAW001は独立固定names NONE/IO/CLIENT_ABORT/BUSY、ordinals0/1/2/3、valueOf同一identity、values配列を変更しても次のvalues不変、未知/小文字/空はIllegalArgumentException、nullはNPEを確認。expectedをproduction enumから作らない。

元8の全closed status×failure×media、byte境界、Unicode/canary、省略field、clock/logger例外、繰返し・並行の期待値を維持し、現Protocol/SessionPrincipalと一つの必要whole9にまとめる。固定memoryLogger/Clock/公開未発行synthetic値のみ、実配信・ファイル・認証・DB・JMS・Root/native/VM/鍵/permit操作なし。

Java25/原POMNullAwayの限定安全MainとSDKを固定し、PMD/Checkstyle/format/全physicalSB、source同一性・全Code単一exec/raw・CRC/init・XML/FES/notrunを独立postで確認。現WebSecurityAudit enum2の同じcompiledbyte/既存rawは比較して再利用可だが、旧whole依存資格へ拡大しない。Web29enum横展開は別scopeの未確認/保留を保持する。旧8実測が未回収なら「未確認」と明記し、新9へ算術加算しない。新規元190受入0/全451未完/正式1964-53不変。
