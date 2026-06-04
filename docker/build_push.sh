cp ../dev_requirements.txt . && \
docker build --no-cache -t supervisely/deploy-cas:0.2.0 . && \
rm dev_requirements.txt && \
docker push supervisely/deploy-cas:0.2.0
