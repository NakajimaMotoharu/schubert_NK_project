"""Typed successor gate for PT-OPS-PG553-PRE003; no VM operations."""
import re

SOURCE='969d8ded10c0bf5841d9e3a5c531e922caf4a24a'
DIGEST='a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b'


def successful_preflight(exit_bytes,receipt):
    return (type(exit_bytes)is bytes and exit_bytes==b'0\n' and type(receipt)is dict
            and receipt.get('run')=='PG553-newrun-preflight-v2'
            and receipt.get('snapshot24')is True and receipt.get('starts0')is True
            and receipt.get('source')==SOURCE and receipt.get('manifestSha256')==DIGEST
            and type(receipt.get('beforeSha256'))is str
            and re.fullmatch('[0-9a-f]{64}',receipt['beforeSha256'])is not None)
