"""Join corrected630 reasons to genuine6014 XML;never reinstate six withdrawn claims."""
import pg5950_private_lock_static3973_join as previous
from pg6014_constants_whole import SOURCE


def qualification_source():
    raw=previous.qualification_source()
    for old,new in(('PG5944-current3973-cases','PG6014-current3973-cases'),('pg5946-private-lock-qualified-v1','pg6016-constants-qualified-v1'),('pg5944-private-lock-six-v1','pg6014-constants-six-v1'),('pg5942-private-lock-static-v1','pg6008-api-bounds-static-v1')):
        if raw.count(old)!=1:raise ValueError('one genuine original6014 source/XML/physical receipt binding')
        raw=raw.replace(old,new,1)
    compile(raw,'<original6014 qualified whole correspondence>','exec')
    return raw


def reader_source():
    raw=previous.reader_source()
    for old,new in(('(joined, static_only, len(result)) != (573, 239, 1451)','(joined, static_only, len(result)) != (630, 239, 1348)'),
                   ('all573 reasons/all1451 warnings preserved,239 static-context-only premises','all630 corrected reasons/all1348 warnings preserved,239 static-context-only premises;six withdrawn claims stay unreviewed'),
                   ('PG5950-current-static3973-v1','PG6024-current-static3973-v1'),('currentRawFindings=1451','currentRawFindings=1348')):
        if raw.count(old)!=1:raise ValueError('one exact current630 reason/XML binding: '+old)
        raw=raw.replace(old,new,1)
    compile(raw,'<corrected current630 actual XML join>','exec')
    return raw


def main():
    scope={**vars(previous.previous.previous),'SOURCE':SOURCE,
           'PENDING':previous.previous.previous.BASE/'PG6020-rethrow-review-withdrawal-v1/manifest.json',
           'PENDING_SHA':'fa2b2e407ab6fc6a303e34f5a323a2810a6f2b0125b23577d26c92205b4e6bd4'}
    exec(compile(qualification_source(),'<current6014 original3973 correspondence>','exec'),scope)
    exec(compile(reader_source(),'<current630 only,no reinstated claims>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
