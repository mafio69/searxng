FROM node:24-alpine AS frontend
WORKDIR /build
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY mcp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mcp/server.py mcp/web_app.py ./
COPY --from=frontend /build/dist ./static
CMD ["python", "web_app.py"]
