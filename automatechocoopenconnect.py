import hashlib
import os
from cloudmesh.common.util import readfile
import requests
from datetime import datetime

BASE_URL = "https://gitlab.com/api/v4/projects/openconnect%2Fopenconnect"

def _make_headers(token: str | None):
    if not token:
        return {}
    token = token.strip()
    if not token:
        return {}
    # Prefer modern Authorization header; GitLab still supports PRIVATE-TOKEN too.
    return {"Authorization": f"Bearer {token}"}

def _get(url, headers, desc, allow_unauth_fallback=True, timeout=30):
    r = requests.get(url, headers=headers, timeout=timeout)
    if r.status_code == 401 and allow_unauth_fallback and headers:
        # Try again without auth in case the project is public but token is bad.
        r2 = requests.get(url, timeout=timeout)
        if r2.ok:
            return r2
    if not r.ok:
        print(f"{desc} failed [{r.status_code}]. Body: {r.text[:400]}")
    return r

def find_windows(token: str | None) -> int | None:
    headers = _make_headers(token)
    page = 1
    per_page = 100

    while True:
        pipelines_url = f"{BASE_URL}/pipelines?per_page={per_page}&page={page}&status=success"
        resp = _get(pipelines_url, headers, "Pipeline request")
        if not resp.ok:
            return None

        pipelines = resp.json()
        if not pipelines:
            break

        for pipeline in pipelines:
            pid = pipeline.get("id")
            print(f"Pipeline ID: {pid}")
            jobs_url = f"{BASE_URL}/pipelines/{pid}/jobs"
            jobs_resp = _get(jobs_url, headers, "Jobs request")
            if not jobs_resp.ok:
                continue

            for job in jobs_resp.json():
                name = job.get("name")
                print(f"Job Name: {name}")
                if name == "MinGW64/GnuTLS":
                    job_id = job["id"]
                    artifacts_url = f"{BASE_URL}/jobs/{job_id}/artifacts"
                    art_resp = _get(artifacts_url, headers, "Artifacts request")
                    if art_resp.ok:
                        out = f"wehaveawinner-{job_id}.zip"
                        with open(out, "wb") as f:
                            f.write(art_resp.content)
                        print(f"Artifacts downloaded successfully → {out}")
                        return job_id
                    else:
                        print(f"No artifacts for job {job_id}")
        page += 1

    print("No matching job with downloadable artifacts was found.")
    return None

def construct_url(job_id: int) -> str:
    return f"https://gitlab.com/openconnect/openconnect/-/jobs/{job_id}/artifacts/download?file_type=archive"

def get_sha256_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest().upper()

def modify_ps1_file(url, sha256_hash):
    with open("tools/chocolateyinstall.ps1", "r", encoding="utf-8") as file:
        lines = file.readlines()
    for i, line in enumerate(lines):
        if "$url        =" in line:
            lines[i] = f"$url        = '{url}'\n"
        elif "Checksum      =" in line:
            lines[i] = f"    Checksum      = '{sha256_hash}'\n"
    with open("tools/chocolateyinstall.ps1", "w", encoding="utf-8") as file:
        file.writelines(lines)

def modify_nuspec_file(version):
    with open("openconnect.nuspec", "r", encoding="utf-8") as file:
        lines = file.readlines()
    for i, line in enumerate(lines):
        if "<version>" in line:
            lines[i] = f"    <version>{version}.{datetime.now().strftime('%Y%m%d')}</version>\n"
    with open("openconnect.nuspec", "w", encoding="utf-8") as file:
        file.writelines(lines)

def main():
    token = None
    try:
        token = readfile("apikey.txt")
    except Exception:
        pass

    job_id = find_windows(token)
    if job_id is None:
        print("Aborting: could not locate/download the artifacts.")
        return

    zip_path = f"wehaveawinner-{job_id}.zip"
    if not os.path.exists(zip_path):
        print(f"Aborting: expected {zip_path} to exist, but it does not.")
        return

    final_url = construct_url(job_id)
    hash_value = get_sha256_hash(zip_path)
    modify_ps1_file(final_url, hash_value)
    modify_nuspec_file("9.12.0")
    print("Updated chocolateyinstall.ps1 and openconnect.nuspec successfully.")

if __name__ == "__main__":
    main()
