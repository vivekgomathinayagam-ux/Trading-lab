"""Push ledger snapshots to the "data" branch on GitHub via the Contents API.
Never pushes to main, so Railway deploys don't loop. Needs GITHUB_DATA_TOKEN
(fine-grained token, Contents read/write on this repo only). Without it the
bot keeps running and just logs that pushes are off.
"""
from __future__ import annotations

import base64
import logging
from pathlib import Path

import requests

log = logging.getLogger("datapush")
API = "https://api.github.com"


class DataPusher:
    def __init__(self, repo: str, branch: str, token: str | None, timeout: int = 20):
        self.repo, self.branch, self.token, self.timeout = repo, branch, token, timeout
        self.enabled = bool(token)
        self.s = requests.Session()
        if token:
            self.s.headers.update({"Authorization": f"Bearer {token}",
                                   "Accept": "application/vnd.github+json",
                                   "X-GitHub-Api-Version": "2022-11-28"})

    def _url(self, path: str) -> str:
        return f"{API}/repos/{self.repo}/{path}"

    def ensure_branch(self) -> bool:
        if not self.enabled:
            return False
        r = self.s.get(self._url(f"git/ref/heads/{self.branch}"), timeout=self.timeout)
        if r.status_code == 200:
            return True
        repo = self.s.get(self._url(""), timeout=self.timeout).json()
        default = repo.get("default_branch", "main")
        base = self.s.get(self._url(f"git/ref/heads/{default}"), timeout=self.timeout).json()
        sha = base["object"]["sha"]
        r = self.s.post(self._url("git/refs"), json={"ref": f"refs/heads/{self.branch}", "sha": sha},
                        timeout=self.timeout)
        ok = r.status_code in (200, 201)
        log.info("created branch %s: %s", self.branch, ok)
        return ok

    def put_file(self, local: Path, remote: str, message: str) -> bool:
        if not self.enabled:
            return False
        content = base64.b64encode(local.read_bytes()).decode()
        url = self._url(f"contents/{remote}")
        cur = self.s.get(url, params={"ref": self.branch}, timeout=self.timeout)
        body = {"message": message, "content": content, "branch": self.branch}
        if cur.status_code == 200:
            if cur.json().get("content", "").replace("\n", "") == content:
                return True  # unchanged
            body["sha"] = cur.json()["sha"]
        r = self.s.put(url, json=body, timeout=self.timeout)
        if r.status_code not in (200, 201):
            log.warning("push %s failed %s: %s", remote, r.status_code, r.text[:200])
            return False
        return True

    def push_dir(self, local_dir: Path, remote_prefix: str, message: str) -> int:
        if not self.enabled:
            log.info("data push skipped: GITHUB_DATA_TOKEN not set")
            return 0
        self.ensure_branch()
        n = 0
        for p in sorted(local_dir.glob("*")):
            if p.is_file() and self.put_file(p, f"{remote_prefix}/{p.name}", message):
                n += 1
        log.info("pushed %d files to %s/%s", n, self.branch, remote_prefix)
        return n
