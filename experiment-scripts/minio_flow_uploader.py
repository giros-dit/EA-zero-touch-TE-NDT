import json
import time
import boto3
import logging

# Import MinIO configuration from config file
from config.b5g import S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET

# Create logger for this module
logger = logging.getLogger(__name__)

# Create S3 client (same as your existing code)
s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name='local'
)

# Flag to ensure we only upload once per session
_initial_flows_created = False

def create_initial_flows_file(dst_ips):
    """
    Create and upload initial flows JSON to S3 - ONLY THE FIRST TIME "Start Variation" is clicked
    After this, ALL operations are handled via HTTP API, this method is NEVER used again.
    """
    global _initial_flows_created
    
    logger.debug("========== create_initial_flows_file LLAMADA ==========")
    logger.debug(f"_initial_flows_created = {_initial_flows_created}")
    
    # Only create the initial file once per session
    if _initial_flows_created:
        logger.debug("*** Ya creado en esta sesión - SALTANDO ***")
        return
    
    logger.debug("*** CREANDO ARCHIVO INICIAL - PRIMERA VEZ EN ESTA SESIÓN ***")
    
    # Use the same timestamp for all flows
    current_timestamp = time.time()
    
    flows_data = {
        "flows": [],
        "inactive_routers": []
    }
    
    # Create flow entries for each destination IP with same timestamp
    for dst_ip in dst_ips:
        flow_entry = {
            "_id": dst_ip,
            "version": 2,
            "timestamps": {
                "ts_api_created": current_timestamp
            }
        }
        flows_data["flows"].append(flow_entry)
    
    # Upload to S3
    content = json.dumps(flows_data, indent=4)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    file_key = f"flows/flows_{timestamp}.json"
    
    logger.debug(f"Subiendo archivo: {file_key}")
    s3_client.put_object(
        Bucket=S3_BUCKET, 
        Key=file_key, 
        Body=content.encode("utf-8")
    )
    
    logger.info(f"✓ ARCHIVO CREADO: s3://{S3_BUCKET}/{file_key}")
    logger.info(f"✓ {len(flows_data['flows'])} flujos con timestamp: {current_timestamp}")
    
    # Mark as created - won't create again in this session
    _initial_flows_created = True
    logger.debug(f"✓ Variable _initial_flows_created = {_initial_flows_created}")
    logger.debug("========== create_initial_flows_file COMPLETADO ==========")

def monitor_s3_files():
    """Función de debug para listar archivos en S3"""
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix="flows/")
        if 'Contents' in response:
            logger.debug("=== ARCHIVOS ACTUALES EN S3/flows/ ===")
            for obj in response['Contents']:
                logger.debug(f"- {obj['Key']} (LastModified: {obj['LastModified']})")
        else:
            logger.debug("=== NO HAY ARCHIVOS EN S3/flows/ ===")
    except Exception as e:
        logger.error(f"Error listando S3: {e}")

def log_current_stack(message):
    """Log quien está llamando esta función"""
    import traceback
    logger.debug(f"STACK_TRACE: {message}")
    for line in traceback.format_stack()[-5:-1]:  # Últimas 4 llamadas
        logger.debug(f"STACK_TRACE: {line.strip()}")
    logger.debug("STACK_TRACE: ====================")