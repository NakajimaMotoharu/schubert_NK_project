"""Lossless PMD diagnostic identity, including columns and raw occurrence provenance."""
import hashlib
import json


def diagnostic_row(path,source_hash,violation,ordinal):
    if type(ordinal)is not int or ordinal<1:raise ValueError('one-based original XML occurrence')
    fields={'sourcePath':path,'sourceSha256':source_hash,**{k:violation.get(k)for k in('rule','beginline','endline','priority')}}
    legacy='F03-PMD-'+hashlib.sha256(json.dumps(fields,sort_keys=True).encode()).hexdigest()
    fields.update({k:violation.get(k)for k in('begincolumn','endcolumn')})
    if any(fields[k]is None for k in('rule','beginline','endline','begincolumn','endcolumn','priority')):raise ValueError('complete original diagnostic coordinates')
    fields.update(diagnosticTextSha256=hashlib.sha256(''.join(violation.itertext()).strip().encode()).hexdigest(),rawXmlOrdinal=ordinal,identitySchema=2)
    digest=hashlib.sha256(json.dumps(fields,sort_keys=True).encode()).hexdigest()
    return {'findingId':'F03-PMD2-'+digest,'legacyFindingId':legacy,**fields,'status':'NOT_REVIEWED_CURRENT_SOURCE'}
