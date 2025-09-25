"""
Firebase configuration and client management.
Fixed for Vercel serverless environment - Event Loop handling.
"""

import os
import json
import logging
import asyncio
from typing import Tuple
from google.cloud import firestore
from google.oauth2 import service_account
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration constants
CREDENTIALS_JSON_ENV_VAR = "GCP_FIREBASE_CREDENTIALS_JSON"
PROJECT_ID_ENV_VAR = "GCP_PROJECT_ID"


class FirebaseConfigError(Exception):
    """Custom exception for Firebase configuration errors."""
    pass


class FirebaseConfig:
    """Firebase configuration manager."""
    
    def __init__(self):
        """Initialize Firebase configuration."""
        self._credentials = None
        self._project_id = None
        self._client = None
    
    def _load_credentials_from_env(self) -> Tuple[service_account.Credentials, str]:
        """
        Load Firebase credentials from environment variables.
        
        Returns:
            Tuple of (credentials, project_id)
            
        Raises:
            FirebaseConfigError: If credentials cannot be loaded or parsed
        """
        # Get credentials JSON string from environment
        credentials_json_string = os.getenv(CREDENTIALS_JSON_ENV_VAR)
        
        if not credentials_json_string:
            raise FirebaseConfigError(
                f"Environment variable {CREDENTIALS_JSON_ENV_VAR} not set or empty. "
                "Please ensure your .env file contains the Firebase service account JSON."
            )
        
        # Parse JSON credentials
        try:
            credentials_info = json.loads(credentials_json_string)
        except json.JSONDecodeError as e:
            raise FirebaseConfigError(
                f"Failed to decode JSON from {CREDENTIALS_JSON_ENV_VAR}. "
                "Please check the JSON format in your environment variable."
            ) from e
        
        # Fix private key format - replace \\n with actual newlines
        if 'private_key' in credentials_info:
            credentials_info['private_key'] = credentials_info['private_key'].replace('\\n', '\n')
        
        # Extract project ID
        project_id = credentials_info.get('project_id')
        if not project_id:
            # Fallback to separate project ID environment variable
            project_id = os.getenv(PROJECT_ID_ENV_VAR)
            if not project_id:
                raise FirebaseConfigError(
                    "Project ID not found in credentials JSON or PROJECT_ID environment variable. "
                    "Please ensure 'project_id' exists in your credentials JSON."
                )
        
        # Create credentials object
        try:
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            return credentials, project_id
        except Exception as e:
            raise FirebaseConfigError(
                f"Failed to create credentials from service account info: {str(e)}"
            ) from e
    
    def get_credentials(self) -> Tuple[service_account.Credentials, str]:
        """
        Get Firebase credentials and project ID.
        
        Returns:
            Tuple of (credentials, project_id)
        """
        if self._credentials is None or self._project_id is None:
            self._credentials, self._project_id = self._load_credentials_from_env()
            logger.info(f"Firebase credentials loaded for project: {self._project_id}")
        
        return self._credentials, self._project_id
    
    def get_firestore_client(self) -> firestore.AsyncClient:
        """
        Get or create Firestore async client with event loop handling.
        
        Returns:
            Firestore AsyncClient instance
        """
        # For serverless environments like Vercel, always create a new client
        # to avoid event loop issues
        try:
            credentials, project_id = self.get_credentials()
            client = firestore.AsyncClient(
                credentials=credentials,
                project=project_id
            )
            logger.info("Firestore async client initialized successfully")
            return client
        except Exception as e:
            if "Event loop is closed" in str(e):
                logger.warning("Event loop closed, creating new client")
                # Reset any cached state and try again
                credentials, project_id = self.get_credentials()
                client = firestore.AsyncClient(
                    credentials=credentials,
                    project=project_id
                )
                return client
            raise
    
    async def close(self):
        """Close the Firestore client connection."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Firestore client connection closed")


# For serverless environments, create new instances per request
def create_firebase_config() -> FirebaseConfig:
    """Create a new Firebase config instance."""
    return FirebaseConfig()


# Public API functions - modified for serverless compatibility
def get_credentials() -> Tuple[service_account.Credentials, str]:
    """
    Get Firebase credentials and project ID.
    
    Returns:
        Tuple of (credentials, project_id)
    """
    config = create_firebase_config()
    return config.get_credentials()


async def get_firestore_client() -> firestore.AsyncClient:
    """
    Get Firestore async client instance.
    Always creates a new client for serverless environments.
    
    Returns:
        Firestore AsyncClient instance
    """
    config = create_firebase_config()
    return config.get_firestore_client()


async def close_firestore_client():
    """Close the Firestore client connection."""
    # In serverless, clients are short-lived, no need to explicitly close
    pass


# Synchronous version for backward compatibility
def get_firestore_client_sync() -> firestore.Client:
    """
    Get synchronous Firestore client.
    
    Returns:
        Firestore Client instance
    """
    credentials, project_id = get_credentials()
    return firestore.Client(credentials=credentials, project=project_id)


def get_collection(collection_name: str):
    """
    Get a Firestore collection reference (synchronous).
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Collection reference
    """
    client = get_firestore_client_sync()
    return client.collection(collection_name)


# Initialize logging message
logger.info("Firebase configuration module initialized successfully")