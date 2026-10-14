"""Readonly current completed a79 image; no old run replay or native restoration."""
import ast
import inspect
import types
from pyflakes.api import check
import pg2410_retired_current_before as extraction
import pg2566_strict_current_backup_content as current
from pg2514_current_cdbc_before import CURRENT_FIELDS, validate_current_image

SLOT='pg2656-current-a79-before-v1'


def payload(seals):
    raw=inspect.getsource(extraction.payload)
    ns={**extraction.__dict__,'prior':current}
    exec(compile(raw,'<current actual image extraction factory>','exec'),ns)
    raw=ns['payload'](seals).replace(extraction.SLOT,SLOT)
    old="require(set(after)=={'backup','configuration','extraDurable','native','originals','pid1','rows','runtime','startup','unitFilesActual','units'})\nrequire(after['native']==native)\nflat={k:v for k,v in after.items()if k!='native'}"
    if raw.count(old)!=1:raise ValueError('one exact current schema boundary required')
    raw=raw.replace(old,'flat=validate_current_image(after,native)')
    raw='CURRENT_FIELDS='+repr(CURRENT_FIELDS)+'\n'+inspect.getsource(validate_current_image)+'\n'+raw
    marker="save=base/'"+SLOT+"'"
    if raw.count(marker)!=1:raise ValueError('one new-only image extraction required')
    raw=raw.replace(marker,"require(data['source']['commit']=='a79b45b5858a186fa82bec1ff36882271ab996a4')\n"+marker)
    if check('HASHES={}\nRECEIPT="actual"\n'+raw,'<whole current a79 extraction>'):raise ValueError('complete namespace required')
    ast.parse(raw);return raw


def entry():
    fn=current.entry()
    return types.FunctionType(fn.__code__,{**fn.__globals__,'SLOT':SLOT,'payload':payload},'current_a79_before')


if __name__=='__main__':raise SystemExit(entry()())
