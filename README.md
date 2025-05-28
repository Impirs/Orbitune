# Orbitune

**Seamlessly transfer playlists, discover availability, and synchronize your music across Spotify, YouTube, Yandex Music , and the others.**

---

## Features

- Cross-platform playlist migration (Spotify → YouTube → Yandex → ...)
- Track search across streaming services
- Smart recommendations based on artist availability
- Encrypted storage of your playlists (optional)
- Fast and lightweight UI powered by Vue 3

---

## Stack

- Frontend: Vue 3 + Vite + SCSS
- Backend: FastAPI (Python 3.11)
- Database: PostgreSQL
- Infrastructure: Docker + Docker Compose

---

Already added:
Welcome page, registration and login to the service. Connecting Spotify and YouTube using oauth with synchronization of playlists and added music.

![image](https://github.com/user-attachments/assets/90c8f291-7068-44a2-8e8a-278770b3c9e2)

![image](https://github.com/user-attachments/assets/6afec1ed-49a5-424b-a3f8-da8141781f90)

![image](https://github.com/user-attachments/assets/ee7b158e-0c91-4891-b263-0df5ebf9a8b9)
For YouTube, the user selects which playlists to import into Orbitune to control that the service stores music.

It is planned to add platform players, as well as connect new music platforms.

---

## Quick Start (Docker)

``` bash
docker-compose up --build
```
