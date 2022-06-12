# Sonarr proxy

This small project allows you to add the french titles show as alias on Sonarr.

## Configuration
You will need to get mitmproxy certificate named as `certs`. The easiest way to do this is :
```bash
pip3 install mitmproxy
copy -r ~/.mitmproxy certs
```

You can then build the images
```bash
docker build -t proxy -f Dockerfile.sonarr .
docker build -t sonarr -f Dockerfile.sonarr .
docker run --name proxy -e SONARR_HOST=https://myhostedsonarr.hosted.fr -e SONARR_API_KEY=<api_key> proxy
```

The last thing to do is to set on sonarr the correct proxy settings and you are done !