# FreeClaw AI Hub

**Open-source AI-assisted software engineering, guided by SPECTION.**

[Site público](https://alexsandsouza.github.io/freeclaw-ai-hub/) · [Framework SPECTION](https://github.com/alexsandsouza/spection)

## Status

This repository currently contains a **static informational website** (MVP 0.1). The browser UI does not yet run AI agents, build applications, or host Python. The existing experimental SPECTION FreeClaw Bridge lives separately in the SPECTION repository.

## Deploy to GitHub Pages

1. Go to **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. The workflow `.github/workflows/pages.yml` deploys the contents of `site/` on pushes to `main`.
3. Check **Actions** for a successful deployment.

## Architecture

- **GitHub Pages**: public, static HTML/CSS/JavaScript website and project documentation
- **SPECTION**: requirements, design decisions, acceptance criteria and human approvals
- **FreeClaw engine (planned)**: local Python backend integrating approved specs with supported AI models and gateways
- **AI providers**: user-configured accounts and endpoints, including NVIDIA where available

Never embed API keys in this repository or browser JavaScript. GitHub Pages cannot securely hold secrets or run the Python backend. Provider free tiers have independent quotas and terms.

## Roadmap

- [x] Public website with responsive design
- [x] GitHub Pages deployment workflow
- [ ] Visual project builder connected to local engine
- [ ] Optional gateway integration and free-only policy
- [ ] AI-assisted code drafting with review gates
- [ ] Test execution and traceability panel

License selection and attribution review are pending. External dependencies retain their own licenses.
