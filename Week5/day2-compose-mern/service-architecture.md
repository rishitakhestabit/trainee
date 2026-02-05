
# Day 2 — Multi-Container Full Stack Application using Docker Compose  
React Client + Node.js Server + MongoDB

---

## Introduction

On Day 2 of Week 5, my objective was to understand how real production systems run multiple services together instead of a single container. On the previous day, I had learned how to run a Node.js application inside Docker, but real-world applications are never just one container. They usually consist of a frontend, a backend, and a database, all working together.

So in this project, I built a multi-container full-stack application using Docker Compose where:

- A React client runs in one container  
- A Node.js + Express server runs in another container  
- MongoDB runs in a third container  

All services start together using one command:

docker compose up -d

This project helped me understand container orchestration, internal container networking, persistent storage using volumes, and production-style architecture.

---

## What I Started With

Before starting this project, I had:

- Basic understanding of Docker images and containers  
- Experience running a single Node.js app inside Docker  
- No real experience with Docker Compose  

My main goal was to move from single-container thinking to system-level thinking.

---

## Planning the System

I first planned the system into three separate services:

- Client (React)
- Server (Node.js + Express)
- Database (MongoDB)

Folder structure:

day2-compose-mern/
- client/
- server/
- docker-compose.yml
- service-architecture.md

Each folder represents one service.

---

## High-Level Architecture

Browser  
→ Client Container (React + Nginx)  
→ Server Container (Node + Express)  
→ MongoDB Container  

The browser never communicates with MongoDB directly. Everything flows through the server.

---

## Building the Server

Inside the server folder:

npm init -y  
npm install express mongoose cors  

I created server.js that:

- Connects to MongoDB  
- Exposes /health endpoint  
- Exposes /api/hello endpoint  

This helped verify that the server and database were working.

---

## Server Dockerfile

FROM node:20-alpine  
WORKDIR /app  
COPY package*.json ./  
RUN npm ci --omit=dev  
COPY . .  
EXPOSE 5000  
CMD ["node","server.js"]  

Learnings:

- Images are built layer by layer  
- Dependencies should be installed before copying code  
- CMD defines startup command  

---

## Building the Client

I created a React app using Vite inside client folder.

Inside src/App.jsx I wrote code that fetches:

/api/hello  

and displays the result.

---

## Client Dockerfile

FROM node:20-alpine AS build  
WORKDIR /app  
COPY package*.json ./  
RUN npm ci  
COPY . .  
RUN npm run build  

FROM nginx:alpine  
COPY --from=build /app/dist /usr/share/nginx/html  
COPY nginx.conf /etc/nginx/conf.d/default.conf  
EXPOSE 80  

---

## Nginx Reverse Proxy

location /api/ {  
  proxy_pass http://server:5000/api/;  
}

This forwards frontend API requests to the server container.

---

## Adding MongoDB

Mongo uses official image:

mongo:7

Mongo stores data in:

/data/db

---

## Docker Compose File

services:

mongo  
- image: mongo:7  
- volume: mongo_data:/data/db  

server  
- build: ./server  
- PORT=5000  
- MONGO_URI=mongodb://mongo:27017/appdb  
- ports: 5001:5000  

client  
- build: ./client  
- ports: 5173:80  

volumes:  
mongo_data  

network:  
appnet  

---

## Container Networking

Server connects using:

mongodb://mongo:27017/appdb  

mongo is service name, not localhost.

---

## Volumes

mongo_data volume stores database permanently.

---

## Running the System

docker compose up -d --build

---

## Verification

docker compose ps  

curl http://localhost:5001/health  

curl http://localhost:5001/api/hello  

Open browser:

http://localhost:5173

---

## Logs

docker compose logs server  
docker compose logs client  
docker compose logs mongo  

---

## Problems Faced

- Docker permission denied → fixed with newgrp docker  
- Port confusion → learned host:container mapping  
- Container name conflicts → removed old containers  

---

## What I Learned

- Multi-container architecture  
- Docker Compose orchestration  
- Container networking  
- Volumes for persistence  
- Reverse proxy with Nginx  

---

## Final Result

I successfully built a full-stack multi-container application where frontend, backend, and database run independently but work together as a single system.

---

