"""SS321/UI231 literal physical Broker oracle, independent from Production code."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET

NS = '{urn:activemq:core}'
ADDRESS = ['nk.sync.request', 'nk.sync.reply.web', 'nk.async.work', 'nk.web.log', 'nk.dead.letter', 'nk.expiry']
GLOBAL = {
    'name': 'schubert-nk-broker', 'persistence-enabled': 'true', 'graceful-shutdown-enabled': 'true',
    'graceful-shutdown-timeout': '60000', 'resolve-protocols': 'false', 'journal-type': 'NIO',
    'paging-directory': 'data/paging', 'bindings-directory': 'data/bindings', 'journal-directory': 'data/journal',
    'large-messages-directory': 'data/large-messages', 'journal-datasync': 'true', 'journal-file-size': '10MiB',
    'journal-min-files': '4', 'journal-pool-files': '20', 'journal-compact-percentage': '30',
    'journal-compact-min-files': '10', 'global-max-messages': '50000', 'global-max-size': '512MiB',
    'max-disk-usage': '90', 'disk-scan-period': '5000', 'id-cache-size': '20000', 'persist-id-cache': 'true',
    'management-message-rbac': 'true', 'management-rbac-prefix': 'mops',
}
COMMON = {
    'dead-letter-address': 'nk.dead.letter', 'expiry-address': 'nk.expiry', 'redelivery-delay': '1000',
    'redelivery-delay-multiplier': '5.0', 'redelivery-collision-avoidance-factor': '0.0',
    'max-redelivery-delay': '30000', 'max-delivery-attempts': '4', 'page-size-bytes': '8MiB',
    'max-read-page-messages': '100', 'max-read-page-bytes': '16MiB', 'address-full-policy': 'PAGE',
    'disk-full-policy': 'BLOCK', 'page-full-policy': 'FAIL', 'auto-create-queues': 'false',
    'auto-delete-queues': 'false', 'auto-delete-created-queues': 'false', 'auto-create-addresses': 'false',
    'auto-delete-addresses': 'false', 'auto-create-dead-letter-resources': 'false',
    'auto-create-expiry-resources': 'false', 'enable-metrics': 'true', 'enable-ingress-timestamp': 'true',
}
# Independent SS321 section5.3 ordered memory bytes/messages and page bytes/messages.
CAPACITY = [(32, 50, 224, 450), (32, 50, 224, 450), (128, 1000, 896, 9000),
            (64, 1000, 192, 9000), (128, 1000, 1920, 9000), (64, 1000, 960, 9000)]
ACL = {
    'nk.sync.request': {'send': {'nk_web'}, 'consume': {'nk_api'}, 'browse': {'nk_ops'}},
    'nk.sync.reply.web': {'send': {'nk_api'}, 'consume': {'nk_web'}, 'browse': {'nk_ops'}},
    'nk.async.work': {'send': {'nk_api', 'nk_ops'}, 'consume': {'nk_api'}, 'browse': {'nk_ops'}},
    'nk.web.log': {'send': {'nk_web'}, 'consume': {'nk_api'}, 'browse': {'nk_ops'}},
    'nk.dead.letter': {'send': {'nk_web', 'nk_api'}, 'consume': {'nk_ops'}, 'browse': {'nk_ops'}, 'manage': {'nk_ops'}},
    'nk.expiry': {'consume': {'nk_ops', 'nk_mq_maintenance'}, 'browse': {'nk_ops', 'nk_mq_maintenance'}, 'manage': {'nk_ops'}},
    'activemq.management.#': {k: {'nk_ops', 'nk_mq_maintenance'} for k in ['manage', 'send', 'consume', 'createAddress', 'deleteAddress', 'createNonDurableQueue', 'deleteNonDurableQueue']},
    'mops.#': {k: {'nk_ops'} for k in ['manage', 'view', 'edit']},
    'mops.queue.nk.expiry.q.countMessages': {k: {'nk_ops', 'nk_mq_maintenance'} for k in ['manage', 'view']},
    'mops.queue.nk.expiry.q.removeMessages': {k: {'nk_ops', 'nk_mq_maintenance'} for k in ['manage', 'edit']},
    'mops.queue.nk.expiry.q.getMessageCount': {k: {'nk_ops', 'nk_mq_maintenance'} for k in ['manage', 'view']},
    'mops.queue.nk.expiry.q.getPersistentSize': {k: {'nk_ops', 'nk_mq_maintenance'} for k in ['manage', 'view']},
    '#': {},
}


def require(value, label):
    if not value:
        raise ValueError(label)


def validate(root):
    require(root.tag == '{urn:activemq}configuration' and len(root) == 1, 'exact root/core')
    core = root[0]; require(core.tag == NS + 'core', 'exact core namespace')
    globals_actual = {e.tag.removeprefix(NS): e.text for e in core if len(e) == 0}
    require(globals_actual == GLOBAL and len(core) == len(GLOBAL) + 4, 'global exact scope/values')
    acceptors = core.find(NS + 'acceptors'); require(acceptors is not None and len(acceptors) == 1, 'one acceptor')
    require(acceptors[0].tag == NS + 'acceptor' and acceptors[0].attrib == {'name': 'core'}
            and acceptors[0].text == 'tcp://127.0.0.1:61616?protocols=CORE', 'loopback CORE only')
    addresses = core.find(NS + 'addresses'); require(addresses is not None and len(addresses) == 6, 'all6 addresses')
    require([a.attrib for a in addresses] == [{'name': a} for a in ADDRESS], 'fixed ordered6 no duplicates')
    for address, name in zip(addresses, ADDRESS):
        require(len(address) == 1 and address[0].tag == NS + 'anycast' and len(address[0]) == 1, 'one anycast queue')
        require(address[0][0].tag == NS + 'queue' and address[0][0].attrib == {'name': name + '.q'}, 'fixed queue attributes')
    settings = core.find(NS + 'address-settings'); require(settings is not None and len(settings) == 6, 'all6 policies')
    for element, name, capacity in zip(settings, ADDRESS, CAPACITY):
        require(element.attrib == {'match': name}, 'exact ordered policy match')
        memory, count, page, page_count = capacity
        expected = {**COMMON, 'max-size-bytes': str(memory) + 'MiB', 'max-size-messages': str(count),
                    'page-limit-bytes': str(page) + 'MiB', 'page-limit-messages': str(page_count)}
        require(len(element) == len(expected) and {e.tag.removeprefix(NS): e.text for e in element} == expected,
                'full policy no duplicate/missing/unapproved fields')
    security = core.find(NS + 'security-settings'); require(security is not None and len(security) == len(ACL), 'all13 ACL')
    actual = {}
    for setting in security:
        match = setting.attrib['match']; require(match not in actual, 'no duplicate ACL')
        permissions = {}
        for permission in setting:
            kind = permission.attrib['type']; require(kind not in permissions, 'no duplicate permission')
            permissions[kind] = set(permission.attrib['roles'].split(','))
        actual[match] = permissions
    require(actual == ACL, 'exact closed ACL, no wildcard fallback privilege')
    return {'globalFields': len(GLOBAL), 'addresses': 6, 'policyFieldsEach': len(COMMON) + 4, 'aclMatches': len(ACL)}


def self_check(path):
    original = ET.parse(path).getroot(); result = validate(original)
    mutations = []
    external = copy.deepcopy(original); external[0].find(NS + 'acceptors')[0].text = 'tcp://0.0.0.0:61616?protocols=CORE'; mutations.append(external)
    retry = copy.deepcopy(original); retry[0].find(NS + 'address-settings')[0].find(NS + 'max-delivery-attempts').text = '5'; mutations.append(retry)
    acl = copy.deepcopy(original); acl[0].find(NS + 'security-settings')[0][0].set('roles', 'nk_web,nk_api'); mutations.append(acl)
    for mutation in mutations:
        refused = False
        try:
            validate(mutation)
        except ValueError:
            refused = True
        require(refused, 'independent policy negative must fail')
    require(validate(original) == result, 'original immutable after negative fixtures')
    return {**result, 'independentSemanticNegatives': len(mutations), 'allRefused': True}


if __name__ == '__main__':
    import json
    print(json.dumps(self_check(Path(__file__).resolve().parents[2] / 'src/deployment/artemis/etc/broker.xml')))
