cp ../dev_requirements.txt . && \
docker build --no-cache -t supervisely/deploy-cas:0.1.3 . && \
rm dev_requirements.txt && \
docker push supervisely/deploy-cas:0.1.3
