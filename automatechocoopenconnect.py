import hashlib
from cloudmesh.common.util import readfile
import requests
from datetime import datetime


def find_windows(token: str) -> str:
    base_url = "https://gitlab.com/api/v4/projects/openconnect%2Fopenconnect"
    headers = {"PRIVATE-TOKEN": token}
    page = 1
    per_page = 100  # increase per_page count as needed

    while True:
        pipelines_url = f"{base_url}/pipelines?per_page={per_page}&page={page}&status=success"
        response = requests.get(pipelines_url, headers=headers)
        if response.status_code != 200:
            print(f"Pipeline request failed with status code {response.status_code}")
            break

        pipelines = response.json()
        if not pipelines:  # no more pipelines on this page
            break

        for pipeline in pipelines:
            print(f"Pipeline ID: {pipeline['id']}")
            jobs_url = f"{base_url}/pipelines/{pipeline['id']}/jobs"
            jobs_response = requests.get(jobs_url, headers=headers)
            if jobs_response.status_code != 200:
                print(f"Request for jobs failed with status code {jobs_response.status_code}")
                continue

            jobs = jobs_response.json()
            for job in jobs:
                print(f"Job Name: {job['name']}")
                if job['name'] == 'MinGW64/GnuTLS':
                    artifacts_url = f"{base_url}/jobs/{job['id']}/artifacts"
                    artifacts_response = requests.get(artifacts_url, headers=headers)
                    if artifacts_response.status_code == 200:
                        print("FOUND!!!!!!")
                        with open('wehaveawinner.zip', 'wb') as f:
                            f.write(artifacts_response.content)
                        print("Artifacts downloaded successfully.")
                        return job['id']
                    else:
                        print(f"Request for artifacts failed with status code {artifacts_response.status_code}")
        page += 1

    return None


def construct_url(job_id) -> str:
    base = 'https://gitlab.com/openconnect/openconnect/-/jobs/'
    end = '/artifacts/download?file_type=archive'
    return base + str(job_id) + end



def get_sha256_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path,"rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest().upper()


def modify_ps1_file(url, sha256_hash):
    with open("tools/chocolateyinstall.ps1", "r") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if "$url        =" in line:
            lines[i] = f"$url        = '{url}'\n"
        elif "Checksum      =" in line:
            lines[i] = f"    Checksum      = '{sha256_hash}'\n"

    with open("tools/chocolateyinstall.ps1", "w") as file:
        file.writelines(lines)

def modify_nuspec_file(version):
    with open("openconnect.nuspec", "r", encoding='utf-8') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if "<version>" in line:
            lines[i] = f"    <version>{version}.{datetime.now().strftime('%Y%m%d')}</version>\n"

    with open("openconnect.nuspec", "w", encoding='utf-8') as file:
        file.writelines(lines)



job_id = find_windows(readfile("apikey.txt"))
final_url = construct_url(job_id)
hash_value = get_sha256_hash('wehaveawinner.zip')

modify_ps1_file(final_url, hash_value)
modify_nuspec_file('9.12.0')
