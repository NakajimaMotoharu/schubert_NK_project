# WD-BUG-004 (副担当ローカル、正式915採番待ち)

Log画面でもSS313§10 validation summary anchorがなく、liの固定messageから対象入力へ移れない。P016-14のlogs.htmlのみ。固定control idとsummary anchorを追加し、FORM/PAGEはLog formを指す。DIF010のFrom/To・enum・入力順・ADMIN display contract・escapeは維持。LogController/実HTTP/DB/JMS/再送/正式受入は副担当対象外。独立期待と失敗を修正前に保存。
