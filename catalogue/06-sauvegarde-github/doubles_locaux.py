#!/usr/bin/env python3
"""Doubles locaux pour tester le workflow n°6 sans compte ni clé réels.

- API n8n (port 9101) : GET /api/v1/workflows (pagination par curseur), POST /api/v1/workflows.
  Les workflows servis viennent d'un fichier JSON (données de démonstration).
- API GitHub « Git Data » (port 9102), adossée à un VRAI dépôt git local :
  GET  /repos/{o}/{r}/git/ref/heads/{branche}
  GET  /repos/{o}/{r}/git/commits/{sha}
  GET  /repos/{o}/{r}/git/trees/{sha}?recursive=1
  POST /repos/{o}/{r}/git/trees      (base_tree + entrées avec « content »)
  POST /repos/{o}/{r}/git/commits
  PATCH /repos/{o}/{r}/git/refs/heads/{branche}
  GET  /repos/{o}/{r}/contents/{chemin}?ref=...
  Les SHA renvoyés sont ceux de git : identiques à ce que calculerait GitHub pour le même contenu.

Chaque requête doit porter la clé de test attendue (en-tête X-N8N-API-KEY ou Authorization: Bearer).
Usage : python doubles_locaux.py --donnees workflows_demo.json --depot /chemin/depot.git
        --cle-n8n CLE --cle-github CLE
"""
import argparse
import base64
import json
import os
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

A = None
verrou = threading.Lock()


def git(*args, entree=None, env=None):
    r = subprocess.run(["git", "--git-dir", A.depot, *args], input=entree, capture_output=True, env={**os.environ, **(env or {})})
    if r.returncode:
        raise RuntimeError(r.stderr.decode())
    return r.stdout.decode().strip()


class Base(BaseHTTPRequestHandler):
    def repondre(self, code, obj):
        d = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(d)))
        self.end_headers()
        self.wfile.write(d)

    def corps(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n) or b"{}")

    def log_message(self, fmt, *args):
        print(f"[{self.__class__.__name__}] {fmt % args}", flush=True)


class N8n(Base):
    def autorise(self):
        if self.headers.get("X-N8N-API-KEY") != A.cle_n8n:
            self.repondre(401, {"message": "unauthorized"})
            return False
        return True

    def do_GET(self):
        if not self.autorise():
            return
        u = urlparse(self.path)
        if u.path != "/api/v1/workflows":
            return self.repondre(404, {"message": "not found"})
        q = parse_qs(u.query)
        limite = int(q.get("limit", ["100"])[0])
        debut = int(q.get("cursor", ["0"])[0] or 0)
        wfs = json.load(open(A.donnees))
        page = wfs[debut:debut + limite]
        suivant = str(debut + limite) if debut + limite < len(wfs) else None
        self.repondre(200, {"data": page, "nextCursor": suivant})

    def do_POST(self):
        if not self.autorise():
            return
        if urlparse(self.path).path != "/api/v1/workflows":
            return self.repondre(404, {"message": "not found"})
        wf = self.corps()
        manquants = [k for k in ("name", "nodes", "connections", "settings") if k not in wf]
        if manquants:
            return self.repondre(400, {"message": "request/body must have required property " + manquants[0]})
        with verrou:
            wfs = json.load(open(A.donnees))
            wf["id"] = "restaure" + str(len(wfs))
            wf["active"] = False
            wfs.append(wf)
            json.dump(wfs, open(A.donnees, "w"), ensure_ascii=False, indent=2)
        self.repondre(200, wf)


class GitHub(Base):
    def autorise(self):
        if self.headers.get("Authorization") != "Bearer " + A.cle_github:
            self.repondre(401, {"message": "Bad credentials"})
            return False
        return True

    def route(self):
        u = urlparse(self.path)
        p = u.path.strip("/").split("/")
        if len(p) < 4 or p[0] != "repos":
            return None, None, parse_qs(u.query)
        return p[3:], "/".join(p[1:3]), parse_qs(u.query)

    def do_GET(self):
        if not self.autorise():
            return
        p, depot, q = self.route()
        try:
            if p[:3] == ["git", "ref", "heads"]:
                return self.repondre(200, {"ref": "refs/heads/" + p[3], "object": {"sha": git("rev-parse", "refs/heads/" + p[3]), "type": "commit"}})
            if p[:2] == ["git", "commits"]:
                tree = git("rev-parse", p[2] + "^{tree}")
                msg = git("log", "-1", "--format=%B", p[2])
                return self.repondre(200, {"sha": p[2], "tree": {"sha": tree}, "message": msg})
            if p[:2] == ["git", "trees"]:
                lignes = (git("ls-tree", "-r", p[2]) if q.get("recursive") else git("ls-tree", p[2])).splitlines()
                arbre = []
                for l in lignes:
                    meta, chemin = l.split("\t", 1)
                    mode, type_, sha = meta.split()
                    arbre.append({"path": chemin, "mode": mode, "type": type_, "sha": sha})
                return self.repondre(200, {"sha": p[2], "tree": arbre, "truncated": False})
            if p[0] == "contents":
                chemin = "/".join(p[1:])
                ref = q.get("ref", ["main"])[0]
                try:
                    contenu = subprocess.run(["git", "--git-dir", A.depot, "show", f"{ref}:{chemin}"], capture_output=True, check=True).stdout
                except subprocess.CalledProcessError:
                    return self.repondre(404, {"message": "Not Found"})
                return self.repondre(200, {"path": chemin, "encoding": "base64", "content": base64.b64encode(contenu).decode(),
                                           "sha": git("rev-parse", f"{ref}:{chemin}")})
        except RuntimeError as e:
            return self.repondre(404, {"message": "Not Found", "detail": str(e)[:200]})
        self.repondre(404, {"message": "Not Found"})

    def do_POST(self):
        if not self.autorise():
            return
        p, depot, q = self.route()
        b = self.corps()
        with verrou:
            if p == ["git", "trees"]:
                with tempfile.TemporaryDirectory() as d:
                    env = {"GIT_INDEX_FILE": os.path.join(d, "index")}
                    if b.get("base_tree"):
                        git("read-tree", b["base_tree"], env=env)
                    for e in b["tree"]:
                        if e.get("sha") is None and "content" not in e:
                            git("update-index", "--force-remove", e["path"], env=env)
                            continue
                        sha = e.get("sha") or git("hash-object", "-w", "--stdin", entree=e["content"].encode())
                        git("update-index", "--add", "--cacheinfo", f"{e.get('mode', '100644')},{sha},{e['path']}", env=env)
                    arbre = git("write-tree", env=env)
                return self.repondre(201, {"sha": arbre})
            if p == ["git", "commits"]:
                args = ["commit-tree", b["tree"], "-m", b["message"]]
                for parent in b.get("parents", []):
                    args += ["-p", parent]
                sha = git(*args, env={"GIT_AUTHOR_NAME": "Sauvegarde n8n", "GIT_AUTHOR_EMAIL": "sauvegarde@exemple.demo",
                                      "GIT_COMMITTER_NAME": "Sauvegarde n8n", "GIT_COMMITTER_EMAIL": "sauvegarde@exemple.demo"})
                return self.repondre(201, {"sha": sha, "html_url": f"https://github.com/{depot}/commit/{sha}"})
        self.repondre(404, {"message": "Not Found"})

    def do_PATCH(self):
        if not self.autorise():
            return
        p, depot, q = self.route()
        b = self.corps()
        if p[:3] == ["git", "refs", "heads"]:
            with verrou:
                actuel = git("rev-parse", "refs/heads/" + p[3])
                if not b.get("force") and git("merge-base", actuel, b["sha"]) != actuel:
                    return self.repondre(422, {"message": "Update is not a fast forward"})
                git("update-ref", "refs/heads/" + p[3], b["sha"])
            return self.repondre(200, {"ref": "refs/heads/" + p[3], "object": {"sha": b["sha"]}})
        self.repondre(404, {"message": "Not Found"})


def main():
    global A
    ap = argparse.ArgumentParser()
    ap.add_argument("--donnees", required=True)
    ap.add_argument("--depot", required=True)
    ap.add_argument("--cle-n8n", required=True)
    ap.add_argument("--cle-github", required=True)
    A = ap.parse_args()
    if not os.path.exists(A.depot):
        subprocess.run(["git", "init", "--bare", "-q", "-b", "main", A.depot], check=True)
        vide = git("hash-object", "-w", "--stdin", entree=b"# Sauvegardes n8n\n")
        with tempfile.TemporaryDirectory() as d:
            env = {"GIT_INDEX_FILE": os.path.join(d, "index")}
            git("update-index", "--add", "--cacheinfo", f"100644,{vide},README.md", env=env)
            arbre = git("write-tree", env=env)
        c = git("commit-tree", arbre, "-m", "Initialisation", env={"GIT_AUTHOR_NAME": "Démo", "GIT_AUTHOR_EMAIL": "demo@exemple.demo",
                                                                   "GIT_COMMITTER_NAME": "Démo", "GIT_COMMITTER_EMAIL": "demo@exemple.demo"})
        git("update-ref", "refs/heads/main", c)
    for port, cls in ((9101, N8n), (9102, GitHub)):
        threading.Thread(target=ThreadingHTTPServer(("127.0.0.1", port), cls).serve_forever, daemon=True).start()
    print("Doubles prêts : API n8n sur :9101, API GitHub sur :9102", flush=True)
    threading.Event().wait()


if __name__ == "__main__":
    main()
