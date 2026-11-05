# Receipt初回8件と未通過登録close

{
  "source": "e8ccb3918a84412bb1731eea48e07cbfc697ee77",
  "run": "PG18874",
  "exit": 0,
  "tests": 8,
  "FES": [
    0,
    0,
    0
  ],
  "manifestSha256": "83f3b91e76b22e661aecc80d45c49dd9ca91dbaea4ce51d22b8cae2bf63503e8",
  "coverage": [
    {
      "type": "INSTRUCTION",
      "missed": "7",
      "covered": "302"
    },
    {
      "type": "BRANCH",
      "missed": "2",
      "covered": "34"
    },
    {
      "type": "LINE",
      "missed": "2",
      "covered": "90"
    },
    {
      "type": "COMPLEXITY",
      "missed": "1",
      "covered": "26"
    },
    {
      "type": "METHOD",
      "missed": "0",
      "covered": "9"
    },
    {
      "type": "CLASS",
      "missed": "0",
      "covered": "1"
    }
  ],
  "uncovered": "register finally statement.close secondary lines55/56; both replace outcomes",
  "qualification": "NOT_WHOLE_SOURCE_100; no independent success post attempted",
  "next": "Add independent register close precedence Test009 SQL/Runtime/Error x absent/SQL/Runtime/Error body primary; exact SQL count/rollback/close/commit/identity assertions. Main and expected policy unchanged. Fresh all9 source/run, no old exec union.",
  "budget": "same765 ordinary group, not V; no new group budget",
  "fixture": "same pure JDBC interfaces; no real DB/driver/files/VM/Root",
  "producerPreservedSha256": "0dbc9cb409f963ac72ab40e6773e2865854021ca3f95587e4473cf07376aa9f0"
}
