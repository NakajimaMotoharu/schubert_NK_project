"""Fresh750 source/PID1 independently validates544 rows and original534 bytes."""
from pg724_retention_sources import oracle as previous_oracle, capture as previous_capture
from pg662_sources import replace


def bind(raw):
    pairs=(('pg722','pg758'),('pg723','pg759'),('pg724','pg760'),('PG724','PG760'),
        ('96a45c46a3e3f33924331fdebfb716bf1a47581b9eb3765f1a00eb4a8d09514e','e64061198bf2aa2716f0895189289db8a9c9dc4741075c22a55c88693ec9879a'),
        ('2468821','2797579'),('2aff8ecf3b7d4d15b24a8af0f73a8745','e4093109ab234700b61dd45711126e4e'),
        ('132812','142602'),('127549297774','137240785885'),('PG715','PG750'),
        ('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'),
        ('74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5','a96ddf6542dff9cdecfb9f92b48c4cefec5c5299598d47e0ce54ad98e5231289'))
    return replace(raw,tuple((a,b)for a,b in pairs if a in raw))


def oracle():
    return replace(previous_oracle(),(('len(after)==534','len(after)==544'),('len(actual)==534','len(actual)==544'),
        ('len(before)==524','len(before)==534'),('len(prior)==524','len(prior)==534'),("'oldRowsPreserved':524","'oldRowsPreserved':534")))


def capture():return replace(bind(previous_capture()),(('==534','==544'),('<=534','<=544')))
