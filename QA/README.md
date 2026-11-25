# QA Workspace: Discovery + QA Automation

Workspace QA siap pakai untuk diletakkan di root proyek web mana pun (`<proyek>/QA/`).
Memakai skill dari <https://github.com/LurreDev-Official/SKILL-VIBE-CODE.git> dengan
Claude Code + Playwright.

## Mulai cepat

```bash
cd QA
npm run skills:install     # pasang skill dari repo ke .claude/skills/
npm run setup              # Playwright + Chromium
cp .env.example .env       # isi BASE_URL & akun uji
npm run demo               # (terminal lain) aplikasi latihan di :4173
npm run test:env           # validasi environment
claude                     # buka Claude Code di folder QA
```

Panduan lengkap langkah demi langkah: **[MODUL_TUTORIAL.md](MODUL_TUTORIAL.md)**.
Aturan kerja untuk Claude: [CLAUDE.md](CLAUDE.md).
