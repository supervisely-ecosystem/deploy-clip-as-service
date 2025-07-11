cp ../dev_requirements.txt . && \
docker build --no-cache -f Dockerfile.test -t supervisely/deploy-cas:test . && \
rm dev_requirements.txt && \
docker push supervisely/deploy-cas:test
