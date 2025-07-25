# config.py
import os
from dotenv import load_dotenv

# --- Environment Configuration ---
# Load environment variables from .env file for local development.
# In a deployed environment (like Google Cloud Run), these variables
# should be set directly in the service's configuration.
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

# Check if we are in a Google Cloud environment.
IS_GCP_ENVIRONMENT = "K_SERVICE" in os.environ
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")

# --- Secret Management ---
def _get_secret(secret_id: str, version_id: str = "latest") -> str:
    """
    Retrieves a secret, either from Google Cloud Secret Manager or a local
    environment variable, based on the execution environment.
    """
    if IS_GCP_ENVIRONMENT:
        # In a GCP environment, the project ID is required to access secrets.
        # It's automatically available in the metadata service, but we check for clarity.
        gcp_project_id = PROJECT_ID
        if not gcp_project_id:
            # Attempt to get it from the metadata service if not set as an env var
            try:
                import requests
                response = requests.get(
                    "http://metadata.google.internal/computeMetadata/v1/project/project-id",
                    headers={"Metadata-Flavor": "Google"}
                )
                response.raise_for_status()
                gcp_project_id = response.text
            except Exception as e:
                raise ValueError(f"GCP_PROJECT_ID is not set and could not be determined from metadata. Error: {e}")

        try:
            from google.cloud import secretmanager
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{gcp_project_id}/secrets/{secret_id}/versions/{version_id}"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            print(f"Could not fetch secret '{secret_id}' from GCP Secret Manager. Error: {e}")
            return None
    else:
        # For local development, retrieve from environment variables loaded from .env
        return os.getenv(secret_id)

# --- API Credentials ---
DB_API_KEY = _get_secret("DB_API_KEY")
DB_API_SECRET = _get_secret("DB_API_SECRET")

# --- Security Configuration ---
# Custom domain for the MCP server
CUSTOM_DOMAIN = os.environ.get("CUSTOM_DOMAIN", "")

# Cloud Run backend URL (for load balancer routing)
def _get_cloud_run_url():
    """Auto-detect Cloud Run URL from environment variables."""
    # First check if explicitly set
    explicit_url = os.environ.get("CLOUD_RUN_URL", "")
    if explicit_url:
        return explicit_url
    
    # Auto-detect if running on Cloud Run
    if IS_GCP_ENVIRONMENT:
        try:
            # Cloud Run sets this environment variable with the service URL
            service_url = os.environ.get("K_SERVICE_URL", "")
            if service_url:
                return service_url
                
            # Fallback: try to get from PORT and other env vars
            port = os.environ.get("PORT", "8080")
            if port != "8080":  # If PORT is set differently, we might be in Cloud Run
                # This is a simplified approach - in practice, you'd set CLOUD_RUN_URL explicitly
                # if auto-detection doesn't work
                pass
                
        except Exception:
            pass
    
    return ""

CLOUD_RUN_URL = _get_cloud_run_url()

# --- API Base URLs ---
BASE_URL_TIMETABLES = "https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1"
BASE_URL_STADA = "https://apis.deutschebahn.com/db-api-marketplace/apis/station-data/v2"
BASE_URL_PARKING = "https://apis.deutschebahn.com/db-api-marketplace/apis/parking-information/db-bahnpark/v2"
BASE_URL_FASTA = "https://apis.deutschebahn.com/db-api-marketplace/apis/fasta/v2"
#BASE_URL_TOMP_CALLABIKE = "https://apis.deutschebahn.com/db-api-marketplace/apis/tomp/v1"