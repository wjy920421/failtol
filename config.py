# AWS region
AWS_REGION = "us-west-2"

# DynamoDB
DEFAULT_DB_WAIT_S = 0.1
BASE_DYNAMODB_NAME = 'Team-LoadBalance-'
DELETE_DYNAMODB_ON_EXIT = True

# Parameters for DB
DEFAULT_VISIBILITY_TIMEOUT = 20

# Default arguments of DB instance
DEFAULT_SQS_IN  = "TEAM_LOADBALANCE_IN"
DEFAULT_SQS_OUT = "TEAM_LOADBALANCE_OUT"
DEFAULT_BASE_PORT       = 7777
DEFAULT_SUBSCRIBE_TO    = "localhost"
DEFAULT_WRITE_CAPACITY  = 10
DEFAULT_READ_CAPACITY   = 10

# Additional constants for frontend and backend
PORT = 8080
MAX_SECONDS = 180
PORT_BACK = 8081

# Instance naming
BASE_INSTANCE_NAME = "TEAM_LOADBALANCE"

# Names for ZooKeeper hierarchy
APP_DIR = "/" + BASE_INSTANCE_NAME
PUB_PORT = "/Pub"
SUB_PORTS = "/Sub"
SEQUENCE_OBJECT = APP_DIR + "/SeqNum"
DEFAULT_NAME = BASE_INSTANCE_NAME + "1"
BARRIER_NAME = "/Ready"
