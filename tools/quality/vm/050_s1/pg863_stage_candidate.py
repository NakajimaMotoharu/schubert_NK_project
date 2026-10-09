"""Unused signed862 stage only; current832/private ADMIN originals unchanged."""
from pathlib import Path
from pg754_stage_candidate import source as previous
R=Path(__file__).resolve().parent
def source():
    raw=previous()
    pairs=(('pg754','pg863'),('PG754','PG863'),('pg750','NEXT_pg862'),('PG750','NEXT_PG862'),('pg715','pg832'),('PG715','PG832'),('NEXT_pg862','pg862'),('NEXT_PG862','PG862'),
      ('8d4b68b4f1449932ebe506aaf08e584bbfea8dd2','e01612fcd7f2752df5ae0836b78538fd5e87f120'),
      ('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','2a0d5aa392c85a1dc12a1cdb423978e8500895b8'),
      ('a96ddf6542dff9cdecfb9f92b48c4cefec5c5299598d47e0ce54ad98e5231289','20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'),
      ('74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5','8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977'))
    for a,b in pairs:raw=raw.replace(a,b)
    raw=raw.replace('Place signed unused PG832 only','Place signed unused PG862 only')
    return raw
if __name__=='__main__':
    namespace={'__file__':str(R/'pg863_stage_candidate.py'),'__name__':'unused_signed862_only'}
    exec(compile(source(),'<863 unused signed current832 preserved>','exec'),namespace);namespace['main']()
