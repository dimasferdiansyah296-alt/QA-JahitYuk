#!/usr/bin/env node
// Pasang / perbarui skill dari repo GitHub ke QA/.claude/skills/<nama-skill>/SKILL.md
//   npm run skills:install
//   npm run skills:install -- https://github.com/<akun>/<repo-lain>.git
// Nama folder skill diambil dari field `name:` di frontmatter tiap file .md.
// File skill dicari secara rekursif (di root repo maupun subfolder), sehingga
// tetap bekerja baik layout repo menaruh skill di root atau di dalam folder QA/.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const { ROOT } = require('../lib/env');

const REPO = process.argv[2] || 'https://github.com/LurreDev-Official/SKILL-VIBE-CODE.git';
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'skill-src-'));

// Kumpulkan semua file .md di dalam repo (lewati node_modules & .git).
function collectMarkdown(dir, acc = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === 'node_modules' || entry.name === '.git') continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) collectMarkdown(full, acc);
    else if (entry.name.toLowerCase().endsWith('.md') && entry.name.toLowerCase() !== 'readme.md') acc.push(full);
  }
  return acc;
}

try {
  console.log(`Mengambil skill dari ${REPO} ...`);
  execFileSync('git', ['clone', '--depth', '1', REPO, tmp], { stdio: 'inherit' });

  const files = collectMarkdown(tmp);
  const installed = new Map();
  for (const file of files) {
    const text = fs.readFileSync(file, 'utf8');
    const name = (text.match(/^---\s*[\r\n]+[\s\S]*?^name:\s*([\w-]+)/m) || [])[1];
    if (!name) continue; // bukan file skill (tidak ada frontmatter name:)
    if (installed.has(name)) continue; // hindari duplikat (mis. salinan di .claude/skills)
    const dir = path.join(ROOT, '.claude', 'skills', name);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'SKILL.md'), text);
    console.log(`  ✓ ${path.relative(tmp, file)}  →  .claude/skills/${name}/SKILL.md`);
    installed.set(name, true);
  }
  console.log(`\n${installed.size} skill terpasang. Mulai ulang sesi Claude Code agar skill terbaca.`);
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}
