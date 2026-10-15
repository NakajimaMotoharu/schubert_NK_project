"""Separate actual full24/original/native/all-resource post after current normal ownedstop."""
import inspect
import pg3496_outbox_owned_post as template
import pg3600_current_browser_owned_sources as role

SLOT='pg3606-current-browser-owned-post-v1'


def namespace():
    ns={**template.__dict__,'role':role,'SLOT':SLOT}
    exec(compile(inspect.getsource(template.namespace),'<current Browser independent full owned post>','exec'),ns);return ns['namespace']()


def main():return namespace()['entry']()()


if __name__=='__main__':raise SystemExit(main())
