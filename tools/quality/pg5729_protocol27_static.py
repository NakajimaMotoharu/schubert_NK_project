"""Static/ABI analysis for all27 protocol enum fields; no tests or runtime operations."""
import hashlib
import inspect
import json
import re
import pg5726_enum_static_abi as previous
from pg5728_protocol27 import SLOT as PROTOCOL

SLOT='pg5729-protocol27-static-v1'
ROOT=previous.ROOT
PREFIX='src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/'
BROKER=PREFIX+'transport/BrokerTopology.java'
REVERSE={'encodedValue':'wireValue','encodedAddress':'address','queueName':'queue','qualifiedQueueName':'fullyQualifiedQueue','bodyLengthLimit':'maximumBodyLength','ttlMillis':'timeToLiveMillis'}


def rename_fields():
    path=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5584-field-accessor-inspection-v1/manifest.json';raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!='31a2a4f92e8a5a2ad0c320a1e6d78008bd560f61e4e3284388ed0a560217bc04':raise ValueError('original typed64field inventory')
    result={}
    for row in json.loads(raw)['fields']:
        if row['ownerKind']=='ENUM'and row['sourcePath'].startswith(PREFIX):result.setdefault(row['sourcePath'],[]).append(row['field'])
    if len(result)!=23 or sum(map(len,result.values()))!=27:raise ValueError('exact23 protocol enum types/27 private fields')
    return result


def renamed_source(path,raw):
    if path!=BROKER:
        if len(re.findall(r'private final (?:String|char) wireValue;',raw))!=1:raise ValueError('one private wire backing declaration')
        raw=re.sub(r'(private final (?:String|char)) wireValue;',r'\1 encodedValue;',raw)
        return raw.replace('this.wireValue = wireValue;','this.encodedValue = wireValue;').replace('return wireValue;','return encodedValue;').replace('candidate.wireValue.equals(value)','candidate.encodedValue.equals(value)')
    replacements={
      'private final String address;':'private final String encodedAddress;',
      'private final String queue;':'private final String queueName;',
      'private final String fullyQualifiedQueue;':'private final String qualifiedQueueName;',
      'private final int maximumBodyLength;':'private final int bodyLengthLimit;',
      'private final long timeToLiveMillis;':'private final long ttlMillis;',
      'this.address = address;':'this.encodedAddress = address;',
      'queue = address + ".q";':'queueName = address + ".q";',
      'fullyQualifiedQueue = address + "::" + queue;':'qualifiedQueueName = address + "::" + queueName;',
      'this.maximumBodyLength = maximumBodyLength;':'this.bodyLengthLimit = maximumBodyLength;',
      'this.timeToLiveMillis = timeToLiveMillis;':'this.ttlMillis = timeToLiveMillis;',
      'return address;':'return encodedAddress;','return queue;':'return queueName;',
      'return fullyQualifiedQueue;':'return qualifiedQueueName;',
      'return maximumBodyLength;':'return bodyLengthLimit;',
      'return timeToLiveMillis;':'return ttlMillis;',
      'return timeToLiveMillis > 0;':'return ttlMillis > 0;',
      'destination.address.equals(address)':'destination.encodedAddress.equals(address)'}
    for old,new in replacements.items():
        if raw.count(old)!=1:raise ValueError('each exact private topology field reference, never the public/local name')
        raw=raw.replace(old,new,1)
    return raw


def normalize_contract(text):
    text=re.sub(r'\b(?:'+ '|'.join(REVERSE)+r')\b',lambda m:REVERSE[m[0]],text)
    return re.sub(r'#\d+','<cp>',text)


def main():
    renames=rename_fields();raw=inspect.getsource(previous.main)
    old="if len(changes)!=18 or any(not p.startswith('src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/')for p in changes):raise ValueError('only eighteen declared enum sources changed')"
    if raw.count(old)!=1:raise ValueError('exact original complete-input predicate')
    raw=raw.replace(old,"if set(changes)!=set(RENAMES):raise ValueError('all23 declared enum sources only')",1)
    old="required=old.replace('private final String wireValue;','private final String encodedValue;').replace('this.wireValue = wireValue;','this.encodedValue = wireValue;').replace('return wireValue;','return encodedValue;')"
    if raw.count(old)!=1:raise ValueError('one explicit expected-source construction')
    raw=raw.replace(old,'required=renamed_source(path,old)',1)
    raw=raw.replace("if old.count('private final String wireValue;')!=1 or new!=required:","if new!=required:",1)
    raw=raw.replace("normalize=lambda text:re.sub(r'#\\d+','<cp>',text.replace('encodedValue','wireValue'))",'normalize=normalize_contract',1)
    raw=raw.replace("'privateTokenEdits':3","'renamedPrivateFields':len(RENAMES[path])",1)
    raw=raw.replace('target18StaticAndAbiQualified','target27StaticAndAbiQualified').replace('PG5726-enum-static-v1','PG5729-protocol27-static-v1')
    ns={**vars(previous),'SLOT':SLOT,'PROTOCOL':PROTOCOL,'RENAMES':renames,'renamed_source':renamed_source,'normalize_contract':normalize_contract}
    exec(compile(raw,'<same reviewed static-only runner/new27 private names>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
