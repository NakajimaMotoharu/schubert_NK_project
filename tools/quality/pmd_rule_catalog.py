"""Resolve primary vendor definitions and explicit deprecated aliases, never guess by name."""
def definitions(resources,wanted):
    import hashlib
    import xml.etree.ElementTree as E
    nodes={};by_name={};aliases=[]
    for name,raw in resources.items():
        for rule in E.fromstring(raw).findall('{*}rule'):
            key=rule.get('name')
            if key not in wanted:continue
            identity=name+'/'+key
            if identity in nodes:raise ValueError('duplicate rule identity')
            nodes[identity]=(name,raw,rule);by_name.setdefault(key,[]).append(identity)
    def resolve(identity,seen):
        if identity in seen or identity not in nodes:raise ValueError('unknown or cyclic vendor alias')
        name,raw,rule=nodes[identity];ref=rule.get('ref')
        if ref is not None:
            if rule.get('deprecated')!='true':raise ValueError('unqualified alias override refused')
            target=resolve(ref,seen|{identity});aliases.append({'alias':identity,'target':ref,'canonical':target});return target
        if not rule.get('class'):raise ValueError('concrete implementation required')
        return identity
    result={}
    for key in sorted(wanted):
        identities=by_name.get(key,[]);canonical={resolve(identity,set())for identity in identities}
        if len(canonical)!=1:raise ValueError('missing or multiple concrete vendor definitions')
        identity=next(iter(canonical));name,raw,rule=nodes[identity]
        description=rule.find('{*}description');properties=rule.find('{*}properties')
        result[key]={'name':key,'canonical':identity,'resource':name,'resourceSha256':hashlib.sha256(raw).hexdigest(),'attributes':dict(rule.attrib),'description':''.join(description.itertext()).strip()if description is not None else'','priority':rule.findtext('{*}priority'),'propertiesXml':E.tostring(properties,encoding='unicode')if properties is not None else None}
    return result,aliases
