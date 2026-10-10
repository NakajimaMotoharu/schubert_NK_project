"""Distinct sealed pre-Root schema and successful source/hash receipt authority."""
SOURCE = 'd5b00104280028d9ea81b44c1d1c805f3c2861ed'
SHA = '57a5889403d752e2558f144b41e9ddd702451d78bf0deab5b6f2fd462b02966e'
FIELDS = frozenset('backup configuration extraDurable native originals pid1 rows runtime startup unitFilesActual units'.split())


def verify(receipt, snapshot):
    if type(receipt) is not dict or type(snapshot) is not dict or set(snapshot) != FIELDS:
        raise ValueError('explicit before schema refused')
    if type(receipt.get('actualExit')) is not int or receipt['actualExit'] != 0 or receipt.get('productionSource') != SOURCE or receipt.get('privateBeforeSha256') != SHA or receipt.get('ordinaryNoargs') is not True or receipt.get('newJstDate') != '2026-10-11':
        raise ValueError('separate before source/hash authority refused')
    if type(snapshot['rows']) is not dict or len(snapshot['rows']) != 24 or any(type(v) is not list for v in snapshot['rows'].values()):
        raise ValueError('complete before tables required')
    return {'sealedBeforeSha256': SHA, 'productionSource': SOURCE, 'beforeSchemaFields': len(FIELDS)}
