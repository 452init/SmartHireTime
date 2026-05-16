import hashlib
import time

import requests


class CloudinaryConfigError(Exception):
    pass


class CloudinaryRequestError(Exception):
    pass


def ensure_cloudinary_config(config):
    if not config.get("cloud_name") or not config.get("api_key") or not config.get("api_secret"):
        raise CloudinaryConfigError(
            "Cloudinary is not configured. Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET."
        )


def upload_image(file_bytes, filename, content_type, folder, config):
    ensure_cloudinary_config(config)

    timestamp = int(time.time())
    params_to_sign = {
        "folder": folder,
        "timestamp": timestamp,
    }
    signature = sign_params(params_to_sign, config["api_secret"])

    response = requests.post(
        f"https://api.cloudinary.com/v1_1/{config['cloud_name']}/image/upload",
        data={
            "api_key": config["api_key"],
            "folder": folder,
            "timestamp": timestamp,
            "signature": signature,
        },
        files={"file": (filename, file_bytes, content_type)},
        timeout=30,
    )
    data = response.json()

    if not response.ok or not data.get("secure_url") or not data.get("public_id"):
        message = data.get("error", {}).get("message") or "Cloudinary upload failed."
        raise CloudinaryRequestError(message)

    return {
        "secure_url": data["secure_url"],
        "public_id": data["public_id"],
    }


def delete_image(public_id, config):
    if not public_id:
        return

    ensure_cloudinary_config(config)

    timestamp = int(time.time())
    params_to_sign = {
        "invalidate": "true",
        "public_id": public_id,
        "timestamp": timestamp,
    }
    signature = sign_params(params_to_sign, config["api_secret"])

    response = requests.post(
        f"https://api.cloudinary.com/v1_1/{config['cloud_name']}/image/destroy",
        data={
            "api_key": config["api_key"],
            "public_id": public_id,
            "timestamp": timestamp,
            "invalidate": "true",
            "signature": signature,
        },
        timeout=30,
    )
    data = response.json()

    if not response.ok:
        message = data.get("error", {}).get("message") or "Cloudinary delete failed."
        raise CloudinaryRequestError(message)


def sign_params(params, api_secret):
    filtered_params = {
        key: value
        for key, value in params.items()
        if value is not None and value != ""
    }
    payload = "&".join(
        f"{key}={filtered_params[key]}" for key in sorted(filtered_params)
    )
    signature_seed = f"{payload}{api_secret}".encode("utf-8")
    return hashlib.sha1(signature_seed).hexdigest()
