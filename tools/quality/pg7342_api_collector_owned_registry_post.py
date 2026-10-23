"""Independent fixed-source24/exact five executable API classes."""
import pg7330_api_async_collector_post as previous
import pg7340_api_collector_owned_registry_host as host

if __name__=='__main__':
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7340-api-collector-owned-registry-host-v1'
    post.OUT=post.host.BASE/'PG7342-api-collector-owned-registry-post-v1'
    post.PRIVATE=post.host.W/'pg7342-api-collector-owned-registry-post-v1'
    post.main()
