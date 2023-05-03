from google.cloud import aiplatform

PROJECT_ID="mythic-evening-379401"
# APP_NAME="bigscience/bloomz-3b"
APP_NAME="bloomz-3b"

CUSTOM_PREDICTOR_IMAGE_URI=f"gcr.io/${PROJECT_ID}/junction_predict_${APP_NAME}"

VERSION = 1
model_display_name = f"{APP_NAME}-v{VERSION}"
model_description = "PyTorch based text classifier with custom container"
MODEL_NAME = APP_NAME
health_route = "/ping"
predict_route = f"/predictions/{MODEL_NAME}"
serving_container_ports = [7080]
model = aiplatform.Model.upload(
    display_name=model_display_name,
    description=model_description,
    serving_container_image_uri=CUSTOM_PREDICTOR_IMAGE_URI,
    serving_container_predict_route=predict_route,
    serving_container_health_route=health_route,
    serving_container_ports=serving_container_ports,
)
model.wait()
print(model.display_name)
print(model.resource_name)

endpoint_display_name = f"chatbot-junctionx"
endpoint = aiplatform.Endpoint.create(display_name=endpoint_display_name)

traffic_percentage = 100
machine_type = "n1-standard-2"
accelerator_type = "NVIDIA_TESLA_T4"
accelerator_count = 1
min_replica_count = 1
max_replica_count = 1

model.deploy(
    endpoint=endpoint,
    deployed_model_display_name=model_display_name,
    machine_type=machine_type,
    min_replica_count=min_replica_count,
    max_replica_count=max_replica_count,
    traffic_percentage=traffic_percentage,
    accelerator_type=accelerator_type,
    accelerator_count=accelerator_count,
    sync=True,
)

print(endpoint.name)
model.wait()
print("Done!")