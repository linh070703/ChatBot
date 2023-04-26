FROM pytorch/torchserve:0.7.1-gpu

ARG APP_NAME

# install dependencies
RUN pip3 install transformers

# copy model artifacts, custom handler and other dependencies
COPY ./torchserve_handler.py /home/model-server/
COPY ../models/$APP_NAME/ /home/model-server/

# create torchserve configuration file
USER root
RUN printf "\nservice_envelope=json" >> /home/model-server/config.properties
RUN printf "\ninference_address=http://0.0.0.0:7080" >> /home/model-server/config.properties
RUN printf "\nmanagement_address=http://0.0.0.0:7081" >> /home/model-server/config.properties
USER model-server

# expose health and prediction listener ports from the image
EXPOSE 7080
EXPOSE 7081

# create model archive file packaging model artifacts and dependencies
RUN torch-model-archiver -f \
  --model-name=$APP_NAME \
  --version=1.0 \
  --serialized-file=/home/model-server/pytorch_model.bin \
  --handler=/home/model-server/torchserve_handler.py \
  --extra-files "/home/model-server/config.json,/home/model-server/tokenizer.json,/home/model-server/tokenizer_config.json,/home/model-server/special_tokens_map.json" \
  --export-path=/home/model-server/model-store

# run Torchserve HTTP serve to respond to prediction requests
CMD ["torchserve", \
     "--start", \
     "--ts-config=/home/model-server/config.properties", \
     "--models", \
     "$APP_NAME=$APP_NAME.mar", \
     "--model-store", \
     "/home/model-server/model-store"]