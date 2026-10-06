# Sauvegarde des workflows n8n

Mise à jour automatiquement. Un fichier par workflow, l'historique est dans les commits.

| Workflow | Actif | Nœuds | Fichier |
|---|---|---|---|
| Catalogue 01 · Factures fournisseurs → lecture IA locale → comptabilité (démo) | oui | 13 | [catalogue-01-factures-fournisseurs-lecture-ia-locale-comptab--cat01FacturesIA.json](workflows/catalogue-01-factures-fournisseurs-lecture-ia-locale-comptab--cat01FacturesIA.json) |
| Catalogue 02 · Agent service client · outils MCP + validation humaine (démo) | oui | 9 | [catalogue-02-agent-service-client-outils-mcp-validation-huma--cat02AgentHitl.json](workflows/catalogue-02-agent-service-client-outils-mcp-validation-huma--cat02AgentHitl.json) |
| Catalogue 02 · Outils Chêne & Cie exposés en MCP (démo) | oui | 4 | [catalogue-02-outils-chene-cie-exposes-en-mcp-demo--cat02OutilsMcp.json](workflows/catalogue-02-outils-chene-cie-exposes-en-mcp-demo--cat02OutilsMcp.json) |
| Catalogue 04 · Assistant documentaire avancé · RAG hybride (démo) | oui | 33 | [catalogue-04-assistant-documentaire-avance-rag-hybride-demo--cat04RagAvance.json](workflows/catalogue-04-assistant-documentaire-avance-rag-hybride-demo--cat04RagAvance.json) |
| Catalogue 05 · Compte rendu de réunion automatique (démo) | oui | 12 | [catalogue-05-compte-rendu-de-reunion-automatique-demo--cat05CompteRendu.json](workflows/catalogue-05-compte-rendu-de-reunion-automatique-demo--cat05CompteRendu.json) |
| Synchro CRM horaire (démo, clé en clair) | oui | 2 | [synchro-crm-horaire-demo-cle-en-clair--demoSyncCrmSale.json](workflows/synchro-crm-horaire-demo-cle-en-clair--demoSyncCrmSale.json) |

## Secrets masqués

Ces nœuds contenaient une clé écrite en clair. Elle a été masquée dans la sauvegarde ; déplacez-la dans un identifiant n8n.

- Synchro CRM horaire (démo, clé en clair) › Lire le CRM

## Archivés

Workflows supprimés de n8n : leur dernière sauvegarde est conservée.

- workflows/catalogue-03-une-video-une-campagne-de-contenus-demo--cat03VideoCampagne.json
