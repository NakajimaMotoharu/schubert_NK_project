"""Pure public-source SQL catch lexical digest, identical documented normalization to PG6542."""
import hashlib
import json
import re

LEX=re.compile(r'//[^\r\n]*|/\*[\s\S]*?\*/|"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_$][A-Za-z0-9_$]*|[^\s]')


def close(tokens,begin,left,right):
    if begin>=len(tokens) or tokens[begin][0]!=left:raise ValueError('opening delimiter required')
    depth=1
    for index in range(begin+1,len(tokens)):
        if tokens[index][0]==left:depth+=1
        elif tokens[index][0]==right:depth-=1
        if depth==0:return index
    raise ValueError('unclosed public lexical block')


def digests(text):
    tokens=[('LITERAL' if match.group().startswith(('"',"'")) else match.group(),match.start())
            for match in LEX.finditer(text) if not match.group().startswith(('//','/*'))]
    rows=[]
    for index,(value,offset) in enumerate(tokens):
        if value!='catch':continue
        parameter_end=close(tokens,index+1,'(',')')
        header=[value for value,_ in tokens[index+2:parameter_end]]
        if 'SQLException' not in header:continue
        ending=close(tokens,parameter_end+1,'{','}')
        body=[value for value,_ in tokens[parameter_end+2:ending]]
        rows.append(dict(catchLine=text.count('\n',0,offset)+1,
                         publicTokenDigest=hashlib.sha256(json.dumps(body).encode()).hexdigest()))
    return rows


def captures(lines,row,regex):
    low=max(0,row['startLine']-2)
    window=''.join(lines[low:min(len(lines),row['endLine']+1)])
    result=set()
    for match in regex.finditer(window):
        first=low+window.count('\n',0,match.start(1))+1
        last=low+window.count('\n',0,match.end(1))+1
        if row['startLine']<=first<=last<=row['endLine']:result.add(match.group(1))
    return result


def proven_set(candidates,proofs):
    if not candidates:return None
    if any(value not in proofs for value in candidates):return None
    return [proofs[value] for value in sorted(candidates)]
