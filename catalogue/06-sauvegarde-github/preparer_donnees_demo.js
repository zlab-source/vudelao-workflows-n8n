// Construit l'instance n8n fictive servie par les doubles locaux : les démos du catalogue,
// plus un workflow volontairement « sale » (clé API en clair, données épinglées, propriétaire) pour tester le nettoyage.
const fs = require("fs");
const path = require("path");
const racine = path.join(__dirname, "..");
const sources = ["01-factures-fournisseurs/demo.json", "02-agent-mcp-validation/demo_agent.json", "02-agent-mcp-validation/demo_serveur_mcp.json",
  "03-video-campagne/demo.json", "04-rag-avance/demo.json", "05-compte-rendu-reunion/demo.json"];
const t0 = "2026-10-01T08:00:00.000Z";
const wfs = sources.map(s => { const w = JSON.parse(fs.readFileSync(path.join(racine, s), "utf8"));
  return { id: w.id, name: w.name, active: true, nodes: w.nodes, connections: w.connections, settings: w.settings, staticData: null,
    pinData: {}, tags: [{ id: "t1", name: "catalogue" }], createdAt: t0, updatedAt: t0, versionId: "v1-" + w.id,
    shared: [{ role: "workflow:owner", project: { name: "Gérant <gerant@chene-et-cie.demo>" } }] }; });
wfs.push({ id: "demoSyncCrmSale", name: "Synchro CRM horaire (démo, clé en clair)", active: true, createdAt: t0, updatedAt: t0, versionId: "v1-sync",
  tags: [], staticData: { lastId: 4021 }, settings: { executionOrder: "v1" },
  shared: [{ role: "workflow:owner", project: { name: "Gérant <gerant@chene-et-cie.demo>" } }],
  nodes: [
    { id: "a1", name: "Toutes les heures", type: "n8n-nodes-base.scheduleTrigger", typeVersion: 1.2, position: [0, 0], parameters: { rule: { interval: [{ field: "hours" }] } } },
    { id: "a2", name: "Lire le CRM", type: "n8n-nodes-base.httpRequest", typeVersion: 4.2, position: [220, 0], parameters: {
      url: "https://crm.exemple.demo/api/contacts", sendHeaders: true,
      headerParameters: { parameters: [{ name: "Authorization", value: "Bearer sk-demo-4f9a2c7e1b8d3f6a0e5c9b2d7a4f1e8c" }] }, options: {} } },
  ],
  connections: { "Toutes les heures": { main: [[{ node: "Lire le CRM", type: "main", index: 0 }]] } },
  pinData: { "Lire le CRM": [{ json: { nom: "Claire Fontaine", email: "claire.fontaine@client.demo", telephone: "06 00 00 00 00" } }] } });
fs.writeFileSync(path.join(__dirname, "donnees_demo", "instance_n8n.json"), JSON.stringify(wfs, null, 2));
console.log(wfs.length, "workflows écrits");
