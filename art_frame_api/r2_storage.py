"""
Cloudflare R2 Object Storage module (S3-compatible).

Environment variables required:
  R2_ACCOUNT_ID       – Cloudflare account ID
  R2_ACCESS_KEY_ID    – R2 token access key ID
  R2_SECRET_ACCESS_KEY – R2 token secret access key
  R2_BUCKET_NAME      – R2 bucket name
  R2_PUBLIC_URL       – (optional) public bucket URL for serving files
"""

import os
import boto3
from botocore.config import Config

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client

    account_id = os.environ.get("R2_ACCOUNT_ID", "")
    access_key = os.environ.get("R2_ACCESS_KEY_ID", "")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY", "")

    if not all([account_id, access_key, secret_key]):
        return None

    _client = boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )
    return _client


def _bucket():
    return os.environ.get("R2_BUCKET_NAME", "paintola")


def is_enabled():
    """Return True when R2 credentials are configured."""
    return _get_client() is not None


def upload_file(local_path: str, r2_key: str, content_type: str = "image/jpeg") -> str:
    """Upload a local file to R2. Returns the R2 key."""
    client = _get_client()
    if client is None:
        raise RuntimeError("R2 storage is not configured")
    client.upload_file(
        local_path,
        _bucket(),
        r2_key,
        ExtraArgs={"ContentType": content_type},
    )
    return r2_key


def upload_bytes(data: bytes, r2_key: str, content_type: str = "image/jpeg") -> str:
    """Upload raw bytes to R2. Returns the R2 key."""
    client = _get_client()
    if client is None:
        raise RuntimeError("R2 storage is not configured")
    client.put_object(
        Bucket=_bucket(),
        Key=r2_key,
        Body=data,
        ContentType=content_type,
    )
    return r2_key


def download_file(r2_key: str, local_path: str) -> str:
    """Download a file from R2 to a local path. Returns the local path."""
    client = _get_client()
    if client is None:
        raise RuntimeError("R2 storage is not configured")
    os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
    client.download_file(_bucket(), r2_key, local_path)
    return local_path


def download_bytes(r2_key: str) -> bytes:
    """Download a file from R2 and return its bytes."""
    client = _get_client()
    if client is None:
        raise RuntimeError("R2 storage is not configured")
    resp = client.get_object(Bucket=_bucket(), Key=r2_key)
    return resp["Body"].read()


def get_public_url(r2_key: str) -> str:
    """Return a public URL for the object, or a presigned URL if no public URL is set."""
    public_base = os.environ.get("R2_PUBLIC_URL", "").rstrip("/")
    if public_base:
        return f"{public_base}/{r2_key}"
    # Fall back to a presigned URL valid for 1 hour
    client = _get_client()
    if client is None:
        raise RuntimeError("R2 storage is not configured")
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": _bucket(), "Key": r2_key},
        ExpiresIn=3600,
    )


def delete_object(r2_key: str):
    """Delete an object from R2."""
    client = _get_client()
    if client is None:
        raise RuntimeError("R2 storage is not configured")
    client.delete_object(Bucket=_bucket(), Key=r2_key)


def list_objects(prefix: str = "") -> list:
    """List object keys under a prefix."""
    client = _get_client()
    if client is None:
        raise RuntimeError("R2 storage is not configured")
    resp = client.list_objects_v2(Bucket=_bucket(), Prefix=prefix)
    return [obj["Key"] for obj in resp.get("Contents", [])]
