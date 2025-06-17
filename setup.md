# Overall settings

First of all, you need to have PostgreSQL and Docker on your computer for further configuration. If you don't have these tools, you can install them from the following resources:

PostgreSQL: https://www.postgresql.org/download/

Docker Desktop: https://www.docker.com/products/docker-desktop/

Node.js (for frontend local development): https://nodejs.org/

---

## Docker Compose and Database Setup

Below is an example of a `docker-compose.yml` file for local development. Replace `USERNAME` and `PASSWORD` with your own values if needed.

```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    container_name: orbitune-postgres
    restart: always
    environment:
      POSTGRES_USER: USERNAME
      POSTGRES_PASSWORD: PASSWORD
      POSTGRES_DB: orbitune
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    container_name: orbitune-backend
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://USERNAME:PASSWORD@db:5432/orbitune
      - SPOTIFY_CLIENT_ID=...
      - SPOTIFY_CLIENT_SECRET=...
      - SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/oauth/spotify/callback
      - GOOGLE_CLIENT_ID=...
      - GOOGLE_CLIENT_SECRET=...
      - GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/oauth/google/callback
    depends_on:
      - db

  frontend:
    build: ./frontend
    container_name: orbitune-frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

### Alembic (Database Migrations)

Use these commands to generate a migration and apply it to the database:

```sh
docker compose exec backend alembic revision --autogenerate -m "comment"
docker compose exec backend alembic upgrade head
```

After this, stop Docker and run build again if needed:

```sh
docker compose up --build
```

**Note:**
- Make sure your database is initialized and migrations are applied before using the app.
- If you want to initialize the database manually (not recommended for production), you can run:

```sh
docker compose exec backend python -c "from app.init_db import init_db; init_db()"
```

---

## Backend

Example backend Dockerfile (`backend/Dockerfile`):

```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y git
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--reload" , "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
```

---

## Frontend

Example frontend Dockerfile (`frontend/Dockerfile`):

```dockerfile
FROM node:20

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
```

---

### Vite config example (`frontend/vite.config.js`)

```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const API_URL = process.env.VITE_API_URL || '/api';

export default defineConfig({
  plugins: [vue()],
  server: {
    watch: {
      usePolling: true,
      interval: 100,
    },
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/auth': {
        target: 'http://backend:8000',  
        changeOrigin: true,
      },
      '/oauth': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/connected_services': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/favorites': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/playlists': { 
        target: 'http://backend:8000', 
        changeOrigin: true 
      },
      '/yandex_music': {
        target: 'http://backend:8000',
        changeOrigin: true
      },
      '/youtube': {
        target: 'http://backend:8000',
        changeOrigin: true
      }
    }
  },
  define: {
    __API_URL__: JSON.stringify(API_URL)
  }
})
```

---

## Useful Docker Compose Commands

- Build all containers:
  ```sh
  docker compose up --build
  ```
- Build and restart only the backend:
  ```sh
  docker compose build backend
  docker compose up -d backend
  ```
- View running containers:
  ```sh
  docker compose ps
  ```
- Stop all containers:
  ```sh
  docker compose down
  ```

---

## Notes

- All environment variables for OAuth (Spotify, Google, Yandex) must match the settings in your developer dashboards.
- For public access (e.g., via ngrok), update the `*_REDIRECT_URI` variables and add the new URIs to your OAuth app settings.
- If you encounter issues with ports, make sure nothing else is running on 5432 (Postgres), 8000 (backend), or 5173 (frontend).
- If you change models, always generate and apply a new Alembic migration.
- If you want to run the backend or frontend locally (not in Docker), make sure to install all dependencies from `requirements.txt` or `package.json`.

---

This guide should be enough to get your project running locally and in Docker. If you need to expose your app publicly, see the section about ngrok and public access in the main documentation or ask for help.
