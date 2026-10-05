#!/usr/bin/env python3
"""Service de transcription local, compatible avec l'API OpenAI (/v1/audio/transcriptions).

Catalogue VudeLao · n°3. Aucune dépendance hors du paquet openai-whisper (et ffmpeg).
Usage : python transcription_locale.py [--modele turbo] [--port 9000] [--hote 127.0.0.1]

Le workflow n8n envoie la vidéo ou l'audio en multipart (champ « file »), comme à l'API d'OpenAI.
On peut donc remplacer ce service par OpenAI, Groq ou tout serveur compatible sans toucher au workflow.
"""
import argparse
import json
import os
import tempfile
import time
from email.parser import BytesParser
from email.policy import default as politique
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

import whisper

MAX_OCTETS = 2 * 1024 ** 3  # 2 Go
verrou = Lock()  # une transcription à la fois : le modèle occupe déjà toute la machine


def horodatage(s, sep=","):
    h, r = divmod(int(s * 1000), 3_600_000)
    m, r = divmod(r, 60_000)
    sec, ms = divmod(r, 1000)
    return f"{h:02}:{m:02}:{sec:02}{sep}{ms:03}"


def en_srt(segments):
    return "\n".join(f"{i}\n{horodatage(s['start'])} --> {horodatage(s['end'])}\n{s['text'].strip()}\n" for i, s in enumerate(segments, 1))


def en_vtt(segments):
    return "WEBVTT\n\n" + "\n".join(f"{horodatage(s['start'], '.')} --> {horodatage(s['end'], '.')}\n{s['text'].strip()}\n" for s in segments)


class Gestionnaire(BaseHTTPRequestHandler):
    modele = None

    def repondre(self, code, corps, type_="application/json; charset=utf-8"):
        donnees = corps.encode() if isinstance(corps, str) else corps
        self.send_response(code)
        self.send_header("Content-Type", type_)
        self.send_header("Content-Length", str(len(donnees)))
        self.end_headers()
        self.wfile.write(donnees)

    def erreur(self, code, message):
        self.repondre(code, json.dumps({"error": {"message": message}}, ensure_ascii=False))

    def do_GET(self):
        if self.path in ("/sante", "/health"):
            return self.repondre(200, json.dumps({"statut": "ok", "modele": self.server.nom_modele}))
        self.erreur(404, "Route inconnue")

    def do_POST(self):
        if self.path.rstrip("/") != "/v1/audio/transcriptions":
            return self.erreur(404, "Route inconnue")
        taille = int(self.headers.get("Content-Length", 0))
        if not taille or taille > MAX_OCTETS:
            return self.erreur(413, "Fichier absent ou trop volumineux")
        corps = self.rfile.read(taille)
        message = BytesParser(policy=politique).parsebytes(
            f"Content-Type: {self.headers.get('Content-Type')}\r\n\r\n".encode() + corps)
        champs, fichier, nom = {}, None, "media"
        for partie in message.iter_parts():
            cle = partie.get_param("name", header="content-disposition")
            if cle == "file":
                fichier, nom = partie.get_payload(decode=True), partie.get_filename() or nom
            elif cle:
                champs[cle] = partie.get_content().strip()
        if not fichier:
            return self.erreur(400, "Champ « file » manquant")

        format_ = champs.get("response_format", "json")
        suffixe = os.path.splitext(nom)[1] or ".bin"
        with tempfile.NamedTemporaryFile(suffix=suffixe, delete=False) as tmp:
            tmp.write(fichier)
            chemin = tmp.name
        try:
            debut = time.time()
            with verrou:
                r = self.modele.transcribe(chemin, language=champs.get("language") or None,
                                           initial_prompt=champs.get("prompt") or None, fp16=False)
            duree = round(time.time() - debut, 1)
        except Exception as e:  # fichier illisible, format non géré par ffmpeg…
            return self.erreur(422, f"Transcription impossible : {e}")
        finally:
            os.unlink(chemin)

        segments = [{"id": s["id"], "start": round(s["start"], 2), "end": round(s["end"], 2), "text": s["text"].strip()} for s in r["segments"]]
        if format_ == "text":
            return self.repondre(200, r["text"].strip(), "text/plain; charset=utf-8")
        if format_ == "srt":
            return self.repondre(200, en_srt(segments), "text/plain; charset=utf-8")
        if format_ == "vtt":
            return self.repondre(200, en_vtt(segments), "text/vtt; charset=utf-8")
        reponse = {"text": r["text"].strip()}
        if format_ == "verbose_json":
            reponse.update(task="transcribe", language=r.get("language"), duration=segments[-1]["end"] if segments else 0,
                           segments=segments, temps_de_calcul_s=duree)
        self.repondre(200, json.dumps(reponse, ensure_ascii=False))

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}", flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--modele", default="turbo", help="modèle Whisper : tiny, base, small, medium, turbo, large-v3")
    p.add_argument("--port", type=int, default=9000)
    p.add_argument("--hote", default="127.0.0.1", help="0.0.0.0 pour accepter les autres machines du réseau")
    a = p.parse_args()
    print(f"Chargement du modèle Whisper « {a.modele} »…", flush=True)
    Gestionnaire.modele = whisper.load_model(a.modele, device="cpu")
    serveur = ThreadingHTTPServer((a.hote, a.port), Gestionnaire)
    serveur.nom_modele = a.modele
    print(f"Prêt : http://{a.hote}:{a.port}/v1/audio/transcriptions", flush=True)
    serveur.serve_forever()


if __name__ == "__main__":
    main()
