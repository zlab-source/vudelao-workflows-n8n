# Workflows n8n de démonstration · VudeLao

Automatisations **réelles et testées**, construites pour des petites entreprises, avec une IA qui tourne en local.
Toutes les données sont **fictives** (entreprise de démonstration « Chêne & Cie »).

> Un autre regard sur vos projets · VudeLao · SG_

## Contenu

### `demos/` · trois automatisations prêtes à adapter

| Fichier | Ce que fait le workflow |
|---|---|
| `01_tri_emails_ia.json` | Lit chaque email entrant, l'analyse avec une IA locale, le classe et le route vers le bon service ; archive le spam, alerte le gérant en cas d'urgence. |
| `02_facture_relances.json` | Devis accepté → facture calculée (HT, TVA, TTC, échéance), enregistrée et envoyée. Chaque matin, relances graduées J+1, J+15, J+30 rédigées par l'IA, arrêt automatique au paiement. |
| `03_assistant_documents_rag.json` | Indexe des documents (PDF, texte) dans Qdrant, puis répond aux questions en citant ses sources (RAG local). |

### `catalogue/` · workflows avancés (démos gratuites, versions pro sur demande)

| Dossier | Ce que fait le workflow |
|---|---|
| [`01-factures-fournisseurs`](catalogue/01-factures-fournisseurs/) | Facture PDF lue par une IA locale, contrôles (montants, SIRET, dates, doublons), écriture comptable proposée, récapitulatif à la comptabilité. |
| [`02-agent-mcp-validation`](catalogue/02-agent-mcp-validation/) | Agent IA de service client : lit les données via un serveur MCP, n'accorde un geste commercial qu'après accord du gérant par email. |
| [`03-video-campagne`](catalogue/03-video-campagne/) | Une vidéo transcrite en local (Whisper) devient sous-titres, article de blog, 3 posts LinkedIn, post court, newsletter et chapitres YouTube, avec contrôles automatiques. |
| [`04-rag-avance`](catalogue/04-rag-avance/) | Assistant documentaire : recherche hybride (sens + mots-clés), reclassement par IA, réponses sourcées et citations vérifiées, mise à jour automatique des documents modifiés. |
| [`05-compte-rendu-reunion`](catalogue/05-compte-rendu-reunion/) | Un enregistrement de réunion transcrit en local devient un compte rendu : décisions, tâches avec responsable et échéance, fichier agenda (.ics), envoyé à tous les participants. |
| [`06-sauvegarde-github`](catalogue/06-sauvegarde-github/) | Sauvegarde nocturne des workflows n8n dans GitHub : un commit daté, clés en clair masquées, données épinglées retirées, restauration de n'importe quelle version en copie inactive. |
| [`07-prospects-crm`](catalogue/07-prospects-crm/) | Demandes de devis notées sur 100 (IA pour le besoin, points fixes pour le reste), API publiques (distance, registre des entreprises), CRM sans doublon, purge RGPD automatique. |
| [`08-demandes-rgpd`](catalogue/08-demandes-rgpd/) | Demandes d'accès, d'effacement ou d'opposition : droits reconnus par IA, confirmation du demandeur, recherche dans chaque outil, conservation légale respectée, validation du gérant, registre et rappels d'échéance. |

### `supervision/` · surveiller les automatisations de plusieurs clients

| Fichier | Rôle |
|---|---|
| `s1_reception_erreurs.json` | Reçoit les erreurs et les signaux de vie envoyés par les instances clientes, alerte immédiatement. |
| `s2_controles_5_min.json` | Toutes les 5 minutes : instance hors ligne ? tâche planifiée silencieuse ? Alerte, puis message de rétablissement. |
| `s3_rapport_mensuel.json` | Chaque mois, un rapport de maintenance par client (disponibilité, erreurs, interruptions), à relire avant envoi. |
| `modele_client_signalement.json` | À installer chez chaque client : signale ses erreurs à la supervision. |
| `test_panne_simulee.json` | Provoque volontairement une erreur pour tester la chaîne d'alerte. |

## Pile technique

- **n8n** 2.x (auto-hébergé, Docker)
- **Ollama** en local : modèle de chat `qwen3.6`, embeddings `nomic-embed-text`
- **Qdrant** pour la recherche dans les documents
- Un serveur **SMTP** (Mailpit pour les tests)

Aucune donnée ne quitte la machine : l'IA, l'index des documents et les emails de test restent en local.

## Installation

1. Importer un workflow : dans n8n, *Import from file*, ou en ligne de commande :
   ```bash
   n8n import:workflow --input=demos/02_facture_relances.json
   ```
2. Créer les identifiants attendus (les fichiers ne contiennent **que leur nom**, jamais de secret) :
   - `Ollama local` (API Ollama)
   - `Qdrant local` (API Qdrant)
   - `SMTP Mailpit (démo)` (SMTP)
   - `Clé de supervision (en-tête X-Supervision-Key)` (Header Auth), une clé longue et aléatoire, identique côté supervision et côté clients
3. Pour la supervision, renseigner dans les réglages de chaque workflow client l'identifiant du workflow d'erreur (`À_RENSEIGNER_ID_DU_WORKFLOW_D_ERREUR`).
4. Publier les workflows. Dans n8n 2.x, un workflow d'erreur doit être publié pour être pris en compte.

## Bon à savoir

- Ce sont des **démonstrations** : les déclencheurs de test (formulaires) se remplacent en production par Gmail, Outlook, IMAP, un CRM ou un outil de facturation.
- Les identifiants techniques de l'instance d'origine ont été retirés de l'export.

## Licence

Ces workflows sont publiés sous **[PolyForm Noncommercial 1.0.0](LICENSE.md)**.

- **Autorisé** : les consulter, les installer, les tester, les modifier et les partager pour un usage **non commercial** (apprentissage, test, projet personnel, recherche, association…), en conservant la licence et la mention ci-dessous.
- **Usage commercial** (dans une entreprise, pour un client, revente) : contactez VudeLao pour obtenir le modèle prêt à l'emploi ou une installation clé en main.

Required Notice: Copyright 2026 VudeLao (https://github.com/zlab-source/vudelao-workflows-n8n)

*Résumé informatif en français : seul le texte anglais de la licence fait foi.*
