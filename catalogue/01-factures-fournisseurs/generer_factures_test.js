// Génère des factures fournisseurs fictives en PDF (texte), pour tester le workflow n°1.
// Usage : node generer_factures_test.js <dossier_sortie>
// Aucune dépendance : écrit un PDF minimal (police Helvetica, encodage WinAnsi).
const fs = require("fs");
const path = require("path");
const out = process.argv[2] || "./factures_test";
fs.mkdirSync(out, { recursive: true });

// SIRET fictif valide (clé de Luhn)
function siret(base13) {
  for (let d = 0; d <= 9; d++) {
    const s = base13 + d;
    let sum = 0;
    for (let i = 0; i < 14; i++) { let n = +s[13 - i]; if (i % 2) { n *= 2; if (n > 9) n -= 9; } sum += n; }
    if (sum % 10 === 0) return s;
  }
}
const eur = n => n.toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";

function pdf(lines) {
  // Encodage WinAnsi : latin-1 + « € » en 0x80
  const enc = s => Buffer.from(s.replace(/€/g, "\u0080").replace(/[’]/g, "'").replace(/ | /g, " "), "latin1")
    .toString("latin1").replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");
  let y = 800, content = "BT\n";
  for (const [txt, size = 10, x = 50, gap = 16] of lines) { content += `/F1 ${size} Tf 1 0 0 1 ${x} ${y} Tm (${enc(txt)}) Tj\n`; y -= gap; }
  content += "ET";
  const objs = [
    "<< /Type /Catalog /Pages 2 0 R >>",
    "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
    "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
    `<< /Length ${Buffer.byteLength(content, "latin1")} >>\nstream\n${content}\nendstream`,
    "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
  ];
  let body = "%PDF-1.4\n", offsets = [];
  objs.forEach((o, i) => { offsets.push(Buffer.byteLength(body, "latin1")); body += `${i + 1} 0 obj\n${o}\nendobj\n`; });
  const xref = Buffer.byteLength(body, "latin1");
  body += `xref\n0 ${objs.length + 1}\n0000000000 65535 f \n` + offsets.map(o => String(o).padStart(10, "0") + " 00000 n \n").join("");
  body += `trailer\n<< /Size ${objs.length + 1} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF`;
  return Buffer.from(body, "latin1");
}

function facture(f) {
  const L = [
    [f.fournisseur, 16, 50, 20], [f.adresse, 9], [`SIRET : ${f.siret} · TVA intracom. : ${f.tvaIntra}`, 9, 50, 28],
    ["FACTURE", 18, 380, 24], [`N° ${f.numero}`, 11, 380, 16], [`Date : ${f.date}`, 10, 380, 14], [`Échéance : ${f.echeance}`, 10, 380, 30],
    ["Facturé à : Chêne & Cie (entreprise fictive de démonstration), 12 rue des Artisans, 19100 Brive", 10, 50, 26],
    ["Désignation", 10, 50, 0], ["Qté", 10, 330, 0], ["P.U. HT", 10, 390, 0], ["Total HT", 10, 480, 18],
  ];
  for (const l of f.lignes) L.push([l[0], 10, 50, 0], [String(l[1]), 10, 330, 0], [eur(l[2]), 10, 390, 0], [eur(l[1] * l[2]), 10, 480, 16]);
  L.push(["", 10, 50, 10], [`Total HT : ${eur(f.ht)}`, 11, 380, 16], [`TVA ${f.taux} % : ${eur(f.tva)}`, 11, 380, 16], [`Total TTC : ${eur(f.ttc)}`, 12, 380, 30],
    [`Règlement par virement à réception de facture. IBAN : ${f.iban}`, 9, 50, 14], ["Pénalités de retard : 3 fois le taux d'intérêt légal. Indemnité forfaitaire de recouvrement : 40 €.", 8]);
  return pdf(L);
}

const base = [
  { fichier: "facture_bois_scierie_limousin.pdf", fournisseur: "Bois & Scierie du Limousin", adresse: "Zone artisanale des Chênes, 87000 Limoges", siret: siret("8123456780001"), tvaIntra: "FR32812345678",
    numero: "BSL-2026-0412", date: "28/09/2026", echeance: "28/10/2026", lignes: [["Chêne massif 27 mm (m²)", 12, 85], ["Livraison sur chantier", 1, 60]], taux: 20, iban: "FR76 3000 4000 0500 0012 3456 789" },
  { fichier: "facture_quincaillerie_pro_ouest.pdf", fournisseur: "Quincaillerie Pro Ouest", adresse: "4 avenue de l'Industrie, 33000 Bordeaux", siret: siret("5234567890002"), tvaIntra: "FR15523456789",
    numero: "QPO-88231", date: "30/09/2026", echeance: "30/10/2026", lignes: [["Charnières invisibles inox (lot de 10)", 5, 42.5], ["Vis à bois 5x60 (boîte de 200)", 4, 32.5]], taux: 20, iban: "FR76 1027 8000 0100 0200 3040 506" },
  { fichier: "facture_vernis_finitions_ERREUR.pdf", fournisseur: "Vernis & Finitions SAS", adresse: "18 rue du Pinceau, 24000 Périgueux", siret: siret("4345678900013"), tvaIntra: "FR90434567890",
    numero: "VF-2026-077", date: "01/10/2026", echeance: "31/10/2026", lignes: [["Vernis marine incolore 5 L", 2, 125]], taux: 20, ttcFaux: 310, iban: "FR76 2004 1000 0101 2345 6789 012" },
];
for (const f of base) {
  f.ht = f.lignes.reduce((s, l) => s + l[1] * l[2], 0); f.tva = Math.round(f.ht * f.taux) / 100; f.ttc = f.ttcFaux ?? Math.round((f.ht + f.tva) * 100) / 100;
  fs.writeFileSync(path.join(out, f.fichier), facture(f));
  console.log(`${f.fichier} · ${f.numero} · HT ${f.ht} · TVA ${f.tva} · TTC ${f.ttc}${f.ttcFaux ? " (erreur volontaire)" : ""}`);
}
// Doublon : même facture renvoyée une seconde fois
fs.copyFileSync(path.join(out, base[0].fichier), path.join(out, "facture_bois_scierie_limousin_DOUBLON.pdf"));
console.log("facture_bois_scierie_limousin_DOUBLON.pdf · copie identique (test de doublon)");
