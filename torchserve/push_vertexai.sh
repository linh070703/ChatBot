#!/bin/bash
set -x
set -e

PROJECT_ID="mythic-evening-379401"
APP_NAME="chatbot"

CUSTOM_PREDICTOR_IMAGE_URI=f"gcr.io/${PROJECT_ID}/junction_predict_${APP_NAME}"
echo $CUSTOM_PREDICTOR_IMAGE_URI
docker build --tag=$CUSTOM_PREDICTOR_IMAGE_URI torchserve --build-arg APP_NAME=$APP_NAME


# run docker container to start local TorchServe deployment
docker run -t -d --rm -p 7080:7080 --name=torchserve_junction $CUSTOM_PREDICTOR_IMAGE_URI
# delay to allow the model to be loaded in torchserve (takes a few seconds)
sleep 20


cat > ./predictor/test.json <<END
{ 
   "text": "Hello, how are you?"
}
END

curl -s -X POST \
  -H "Content-Type: application/json; charset=utf-8" \
  -d @./predictor/test.json \
  http://localhost:7080/predictions/$APP_NAME/

docker push $CUSTOM_PREDICTOR_IMAGE_URI