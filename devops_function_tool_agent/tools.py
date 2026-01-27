import subprocess
import requests


def check_pod_status(namespace: str = "default") -> dict:
    """Check the status of pods in a Kubernetes namespace.

    Use this tool when the user wants to see what pods are running,
    check pod health, or troubleshoot pod issues.

    Args:
        namespace: The Kubernetes namespace to check. Defaults to "default".

    Returns:
        dict with "output" containing pod information in JSON format,
        and "error" if any errors occurred.
    """
    try:
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.stderr else None
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out after 30 seconds"}
    except FileNotFoundError:
        return {"success": False, "error": "kubectl not found. Is it installed and in PATH?"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def get_gcp_instance(instance_name: str, zone: str, project: str) -> dict:
    """Get details of a GCP Compute Engine VM instance.

    Use this tool when the user wants to see VM details like status,
    machine type, IP addresses, disks, or other instance configuration.

    Args:
        instance_name: The name of the VM instance.
        zone: The GCP zone where the instance is located (e.g., "us-central1-a").
        project: The GCP project ID.

    Returns:
        dict with "output" containing instance details in JSON format,
        and "error" if any errors occurred.
    """
    try:
        result = subprocess.run(
            ["gcloud", "compute", "instances", "describe", instance_name,
             "--zone", zone, "--project", project, "--format", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.stderr else None
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out after 30 seconds"}
    except FileNotFoundError:
        return {"success": False, "error": "gcloud not found. Is it installed and in PATH?"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def scale_deployment(deployment: str, replicas: int, namespace: str = "default") -> dict:
    """Scale a Kubernetes deployment to the specified number of replicas.

    IMPORTANT: This modifies infrastructure. Always confirm with the user before calling.

    Use this tool when the user wants to scale up or scale down a deployment.

    Args:
        deployment: The name of the Kubernetes deployment to scale.
        replicas: The target number of replicas (must be 0-100).
        namespace: The Kubernetes namespace. Defaults to "default".

    Returns:
        dict with "success" boolean and "message" describing the result.
    """
    # Safety check: limit replicas to reasonable range
    if replicas < 0 or replicas > 100:
        return {
            "success": False,
            "message": f"Replicas must be between 0 and 100. Got: {replicas}"
        }

    try:
        result = subprocess.run(
            ["kubectl", "scale", "deployment", deployment,
             f"--replicas={replicas}", "-n", namespace],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "message": result.stdout if result.returncode == 0 else result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Command timed out after 30 seconds"}
    except FileNotFoundError:
        return {"success": False, "message": "kubectl not found. Is it installed and in PATH?"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}


def check_service_health(url: str, timeout: int = 5) -> dict:
    """Check if an HTTP service endpoint is healthy and responding.

    Use this tool when the user wants to verify if a service is up,
    check response times, or troubleshoot connectivity issues.

    Args:
        url: The full URL to check (e.g., "https://api.example.com/health").
        timeout: Request timeout in seconds. Defaults to 5.

    Returns:
        dict with "healthy" boolean, "status_code", "response_time_ms",
        and "error" if the request failed.
    """
    # Basic URL validation
    if not url.startswith(("http://", "https://")):
        return {
            "healthy": False,
            "error": "URL must start with http:// or https://"
        }

    try:
        response = requests.get(url, timeout=timeout)
        return {
            "healthy": response.status_code == 200,
            "status_code": response.status_code,
            "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2)
        }
    except requests.Timeout:
        return {"healthy": False, "error": f"Request timed out after {timeout} seconds"}
    except requests.ConnectionError:
        return {"healthy": False, "error": "Connection failed. Check if the URL is correct and accessible."}
    except requests.RequestException as e:
        return {"healthy": False, "error": str(e)}
