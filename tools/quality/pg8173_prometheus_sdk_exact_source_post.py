"""New-only full-source SDK metadata requalification; no download or target execution."""
import pg8172_prometheus_sdk_post as post
if __name__=='__main__':
    post.OUT=post.BASE/'PG8173-prometheus-sdk-exact-source-post-v1'
    post.main()
