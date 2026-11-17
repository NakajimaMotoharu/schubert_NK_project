# BUG3189/YKT2657 WBS公開JSON参照修正
ToolFix low .1/base .3/high .8 cap1。485/486の公開JSONと所定tool sourceだけを読み、beforeの真正参照不一致、currenthash再結合、他486field不変/元190row/原価格/元snapshot意味の不変を検証。Main/Test/DB/VM/private/四held/Root/cohortの追加source/binary調査はしない。
全auditは--current-source-structure-onlyの入力（publicJSONとGit名簿だけ）を確認後に一回扱う。stale descriptor等で失敗/HOLDする場合は理由を保存し、hash修正を全WBS/451合格にしない。旧履歴/旧view/元受入は書換えない。将来保存のcheck既定/rebind明示を小工具へ実装しguard対象を限定する。
元negative準備.35成果と今回ToolFix価格を混ぜず、history原9.888/原残1089.498/追加12.350/ToolFix別1.4/再資格別1.4を保持。source MainCorea013不変、parent正式17/190・1964/53は変更しない。
