# FreeClaw AI Hub

**Open-source AI-assisted software engineering, guided by SPECTION.**

[Site público](https://alexsandsouza.github.io/freeclaw-ai-hub/) · [Framework SPECTION](https://github.com/alexsandsouza/spection)

## Status

The repository now contains the **public website and functional FreeClaw AI Studio 0.2 browser workspace**. The Studio can create local projects, edit SPECTION documents, manage tasks and export Markdown/JSON backups. It does **not** execute agents, run code, call AI APIs or host Python. The experimental Python bridge continues to live separately in the SPECTION repository.\n\n[Open AI Studio 0.2](https://alexsandsouza.github.io/freeclaw-ai-hub/studio.html)

## Deploy to GitHub Pages

1. Go to **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. The workflow `.github/workflows/pages.yml` deploys the contents of `site/` on pushes to `main`.
3. Check **Actions** for a successful deployment.

## Architecture

- **GitHub Pages**: public, static HTML/CSS/JavaScript website and project documentation
- **SPECTION**: requirements, design decisions, acceptance criteria and human approvals
- **FreeClaw engine (planned)**: local Python backend integrating approved specs with supported AI models and gateways
- **AI providers**: user-configured accounts and endpoints, including NVIDIA where available

Studio saves drafts in localStorage on the current browser profile. This is not encrypted and can be cleared by the browser. Do not store secrets, real student data or confidential material in its forms. Export backups periodically.\n\nNever embed API keys in this repository or browser JavaScript. GitHub Pages cannot securely hold secrets or run the Python backend. Provider free tiers have independent quotas and terms.

## Roadmap

- [x] Public website with responsive design
- [x] GitHub Pages deployment workflow
- [x] Browser-based projects, SPECTION editor, task checklist and backup export (local-only MVP)\n- [ ] Connect Studio to an authenticated local engine
- [ ] Optional gateway integration and free-only policy
- [ ] AI-assisted code drafting with review gates
- [ ] Test execution and traceability panel

License selection and attribution review are pending. External dependencies retain their own licenses.
\n## Studio 0.2 user guide\n\n1. Open [the graphical Studio](https://alexsandsouza.github.io/freeclaw-ai-hub/studio.html).\n2. Create a named project and provide a short goal.\n3. Open **Especificações** to edit Product Brief, PRD, HLD, LLD and Feature Specification.\n4. Track tasks in **Tarefas**.\n5. Export a combined Markdown document or an individual specification; use **Exportar backup JSON** for an importable complete backup.\n6. Review documents before transferring them into a real SPECTION Kit project.\n\n**Important:** The combined Markdown export is a readable bundle, not an automatically installed project tree. No APIs are called and the browser cannot control the existing local Python server.\n