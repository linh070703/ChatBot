#!/bin/bash
set -x
set -e

PROJECT_ID="mythic-evening-379401"
APP_NAME="bloomz-3b"

CUSTOM_PREDICTOR_IMAGE_URI="gcr.io/${PROJECT_ID}/junction_predict_${APP_NAME}"
echo $CUSTOM_PREDICTOR_IMAGE_URI
docker build --rm --build-arg APP_NAME=$APP_NAME --tag=$CUSTOM_PREDICTOR_IMAGE_URI -f torchserve/Dockerfile torchserve

# run docker container to start local TorchServe deployment
docker run -t -d --rm -p 7080:7080 --name=torchserve_junction --gpus all $CUSTOM_PREDICTOR_IMAGE_URI
# delay to allow the model to be loaded in torchserve (takes a few seconds)
sleep 30


cat > ./test.json <<END
{ 
   "prompt": "Hello, how are you?"
}
END

curl -X POST \
  -H "Content-Type: application/json; charset=utf-8" \
  -d @./test.json \
  http://localhost:7080/predictions/$APP_NAME/

docker push $CUSTOM_PREDICTOR_IMAGE_URI