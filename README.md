# Terminal CV — Nadav Vitri

A personal CV as a **terminal / matrix-hacker themed** static website, served
by **Nginx** inside a **Docker** container, ready to deploy to **Azure
Container Apps**.

## What's in here (and what each file teaches you)

| File | What it is | What you learn |
|---|---|---|
| `cv.yaml` | **Single source of truth** (RenderCV format) — content for both site & PDF | data-driven docs |
| `generate.py` | Reads `cv.yaml` + `template.html` → writes `dist/` (the website) | Python, Jinja2, YAML |
| `template.html` | HTML skeleton with Jinja2 placeholders (filled by `generate.py`) | templating, HTML semantics |
| `styles.css` | The terminal theme, layout, animations | CSS variables, flexbox, `@keyframes`, media queries |
| `matrix.js` | The falling "digital rain" background | `<canvas>` 2D drawing, animation loop |
| `main.js` | The typing animation on the name | DOM + `setInterval` |
| `requirements.txt` | Python deps: RenderCV (PDF) + Jinja2/PyYAML (site) | pip, pinned deps |
| `Dockerfile` | Recipe to build the container image | Docker images, layers, `FROM/COPY/CMD` |
| `nginx.conf` | Web-server config inside the container | how static files are served in prod |
| `.dockerignore` | Files to keep out of the image | build hygiene |

> The resume PDF (`Nadav_Vitri_CV.pdf`) is **generated** during the build by
> `rendercv render cv.yaml`, so it isn't committed. Edit only `cv.yaml`; both the
> website and the PDF are regenerated from it.

## The mental model

```
your files ──build──> Docker image ──run──> container ──serves──> browser
                          │
                          └── push to Azure Container Registry ──> Azure Container Apps ──> public URL
```

An **image** is a frozen snapshot (Nginx + your files). A **container** is a
running instance of that image. It behaves the same on your laptop and in Azure.

## Run it locally (2 commands)

```bash
# 1. Build an image named "cv" from the Dockerfile in this folder ('.')
docker build -t cv .

# 2. Run it, mapping your laptop's port 8080 -> the container's port 80
docker run --rm -p 8080:80 cv
```

Then open <http://localhost:8080>. Stop it with `Ctrl+C`.

- `-t cv` names the image `cv`.
- `--rm` deletes the container when you stop it (keeps things tidy).
- `-p 8080:80` = "send my laptop's :8080 to the container's :80".

## Next step: deploy to Azure Container Apps

Gives you a free `https://<name>.<region>.azurecontainerapps.io` domain +
HTTPS, and **scales to zero** (≈$0 when idle). One command does build + push +
deploy from source:

```bash
az containerapp up \
  --name terminal-cv \
  --resource-group cv-rg \
  --location westeurope \
  --source .
```

> 💡 Before deploying, set a budget alert in the Azure Portal
> (Cost Management → Budgets) so your $150 credit is protected.

## Change the theme

All colors are CSS variables at the top of `styles.css` under `:root`.
Swap `--green` for `--amber: #ffb000` (retro) or cyan for cyberpunk.
