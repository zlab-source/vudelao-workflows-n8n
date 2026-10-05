// Génère la notice de pose fictive (PDF texte, sans dépendance) utilisée par la démo n°4.
const fs = require("fs");
const out = process.argv[2] || "./documents/Notice_pose_fenetre_FX68.pdf";
function pdf(pages) {
  const enc = s => Buffer.from(s.replace(/€/g, "\u0080").replace(/[’]/g, "'"), "latin1").toString("latin1").replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");
  const objs = ["<< /Type /Catalog /Pages 2 0 R >>", null, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"];
  const kids = [];
  for (const lines of pages) {
    let y = 800, c = "BT\n";
    for (const [t, size = 10, gap = 15] of lines) { c += `/F1 ${size} Tf 1 0 0 1 50 ${y} Tm (${enc(t)}) Tj\n`; y -= gap; }
    c += "ET";
    objs.push(`<< /Length ${Buffer.byteLength(c, "latin1")} >>\nstream\n${c}\nendstream`);
    const contentId = objs.length;
    objs.push(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> /Contents ${contentId} 0 R >>`);
    kids.push(`${objs.length} 0 R`);
  }
  objs[1] = `<< /Type /Pages /Kids [${kids.join(" ")}] /Count ${kids.length} >>`;
  let body = "%PDF-1.4\n"; const off = [];
  objs.forEach((o, i) => { off.push(Buffer.byteLength(body, "latin1")); body += `${i + 1} 0 obj\n${o}\nendobj\n`; });
  const x = Buffer.byteLength(body, "latin1");
  body += `xref\n0 ${objs.length + 1}\n0000000000 65535 f \n` + off.map(o => String(o).padStart(10, "0") + " 00000 n \n").join("");
  return Buffer.from(body + `trailer\n<< /Size ${objs.length + 1} /Root 1 0 R >>\nstartxref\n${x}\n%%EOF`, "latin1");
}
const p1 = [["Notice de pose - Fenêtre chêne FX68", 16, 22], ["Document fictif de démonstration. Chêne & Cie est une entreprise imaginaire.", 9, 28],
  ["1. Avant la pose", 12, 18],
  ["Vérifier que la maçonnerie est saine, sèche et d'aplomb. Le jeu périphérique entre le dormant", 10], ["et la maçonnerie doit être compris entre 5 et 10 mm sur chaque côté.", 10, 24],
  ["2. Fixation du dormant", 12, 18],
  ["Fixer le dormant avec des vis de 7,5 x 112 mm, à 15 cm de chaque angle puis tous les 60 cm au plus.", 10],
  ["Caler sous les points de fixation pour ne pas déformer le dormant. Contrôler l'équerrage :", 10],
  ["l'écart entre les deux diagonales ne doit pas dépasser 2 mm.", 10, 24],
  ["3. Réglage des paumelles", 12, 18],
  ["Les paumelles se règlent avec une clé Allen de 4 mm. Couple de serrage des vis de paumelles :", 10],
  ["3,5 N.m, sans dépasser 4 N.m pour ne pas écraser le bois. Le réglage en hauteur est de plus ou moins 2 mm.", 10, 24],
  ["4. Étanchéité", 12, 18],
  ["Poser un mastic acrylique côté intérieur et un mastic silicone neutre côté extérieur. Le fond de joint est", 10],
  ["obligatoire au-delà de 6 mm de largeur de joint.", 10]];
const p2 = [["5. Option oscillo-battant (FX68-OB)", 12, 18],
  ["La crémone oscillo-battante se graisse une fois par an. Si le vantail frotte en position soufflet,", 10],
  ["régler le compas d'angle : un quart de tour correspond à environ 1 mm de déplacement.", 10, 24],
  ["6. Contrôle final", 12, 18],
  ["Ouvrir et fermer chaque vantail cinq fois. La manoeuvre doit se faire sans effort, la poignée", 10],
  ["doit revenir en position sans point dur. Remettre au client la fiche d'entretien des menuiseries bois.", 10]];
fs.writeFileSync(out, pdf([p1, p2]));
console.log("écrit :", out);
