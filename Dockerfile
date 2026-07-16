# Multi-stage build: generate the site with Python, then serve it with Nginx.

# Stage 1: run generate.py to build the static dist/ folder.
FROM python:3.12-alpine AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY cv.yaml template.html generate.py styles.css matrix.js main.js Nadav_Vitri_CV.pdf ./
RUN python generate.py

# Stage 2: serve only the generated output (no Python in the final image).
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
