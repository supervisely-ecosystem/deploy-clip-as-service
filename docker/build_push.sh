TAG=${TAG:-test-1.0.1}

cp ../dev_requirements.txt . && \
docker build --no-cache -t supervisely/deploy-cas:$TAG . && \
rm dev_requirements.txt && \
docker push supervisely/deploy-cas:$TAG
