"""
Execute the deployed UiPath agent via Orchestrator API
"""
import requests
import json
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Get UiPath configuration from .env
UIPATH_URL = os.getenv("UIPATH_URL")
UIPATH_ACCESS_TOKEN = os.getenv("UIPATH_ACCESS_TOKEN")
UIPATH_TENANT_ID = os.getenv("UIPATH_TENANT_ID")
UIPATH_ORGANIZATION_ID = os.getenv("UIPATH_ORGANIZATION_ID")

# API endpoints
BASE_URL = UIPATH_URL.replace("/DefaultTenant", "")
ORCHESTRATOR_API = f"{BASE_URL}/DefaultTenant/orchestrator_"

def get_headers():
    """Get authorization headers"""
    return {
        "Authorization": f"Bearer {UIPATH_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-UIPATH-TenantName": "DefaultTenant",
        "X-UIPATH-OrganizationUnitId": UIPATH_TENANT_ID
    }

def list_processes():
    """List all available processes"""
    url = f"{ORCHESTRATOR_API}/odata/Releases"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code == 200:
        data = response.json()
        print("\n📋 Available Processes:")
        for process in data.get("value", []):
            print(f"  - {process.get('Name')} (Key: {process.get('Key')})")
        return data.get("value", [])
    else:
        print(f"❌ Failed to list processes: {response.status_code}")
        print(response.text)
        return []

def start_job(process_key, input_data):
    """Start a job for the given process"""
    url = f"{ORCHESTRATOR_API}/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs"
    
    payload = {
        "startInfo": {
            "ReleaseKey": process_key,
            "Strategy": "Specific",
            "InputArguments": json.dumps(input_data)
        }
    }
    
    response = requests.post(url, headers=get_headers(), json=payload)
    
    if response.status_code == 201:
        job = response.json()
        print(f"\n✅ Job started successfully!")
        print(f"   Job ID: {job.get('Id')}")
        print(f"   Job Key: {job.get('Key')}")
        return job
    else:
        print(f"\n❌ Failed to start job: {response.status_code}")
        print(response.text)
        return None

def get_job_status(job_key):
    """Get job status"""
    url = f"{ORCHESTRATOR_API}/odata/Jobs?$filter=Key eq {job_key}"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code == 200:
        data = response.json()
        jobs = data.get("value", [])
        if jobs:
            return jobs[0]
    return None

def main():
    print("🤖 UiPath Agent Executor")
    print("=" * 50)
    
    # List available processes
    processes = list_processes()
    
    if not processes:
        print("\n⚠️  No processes found. Please ensure your agent is deployed.")
        return
    
    # Find the MultiIntentIdentification_App process
    target_process = None
    for process in processes:
        if "MultiIntentIdentification" in process.get("Name", ""):
            target_process = process
            break
    
    if not target_process:
        print("\n⚠️  MultiIntentIdentification_App not found in processes.")
        print("Available processes are listed above.")
        return
    
    print(f"\n✓ Found process: {target_process.get('Name')}")
    
    # Load input from input.json
    try:
        with open("input.json", "r") as f:
            input_data = json.load(f)
        print(f"\n📥 Input data: {json.dumps(input_data, indent=2)}")
    except FileNotFoundError:
        print("\n⚠️  input.json not found, using default input")
        input_data = {"user_prompt": "I want to apply for leave from next Monday to Wednesday"}
    
    # Start the job
    job = start_job(target_process.get("Key"), input_data)
    
    if job:
        job_key = job.get("Key")
        print(f"\n🔗 Monitor your job at:")
        print(f"   {UIPATH_URL}/orchestrator_/jobs?tid=45799&fid=169487")
        
        # Poll for job status
        print("\n⏳ Waiting for job to complete...")
        for i in range(30):  # Poll for up to 30 seconds
            time.sleep(1)
            status = get_job_status(job_key)
            if status:
                state = status.get("State")
                print(f"   Status: {state}")
                
                if state in ["Successful", "Faulted", "Stopped"]:
                    if state == "Successful":
                        print("\n✅ Job completed successfully!")
                        output = status.get("OutputArguments")
                        if output:
                            print(f"\n📤 Output:")
                            print(json.dumps(json.loads(output), indent=2))
                    else:
                        print(f"\n❌ Job ended with state: {state}")
                    break
        else:
            print("\n⏱️  Job is still running. Check the URL above for updates.")

if __name__ == "__main__":
    main()
