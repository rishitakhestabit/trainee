# Linux Inside a Docker Container — Day 1 (Hands-on Narrative)

---

## Introduction

Today I worked on understanding **how a real server environment looks internally** by running a Node.js application inside a Docker container and then exploring the Linux operating system from inside that container.

 These are the following I did:

- Built a Node.js app
- Containerized it using Docker
- Ran it as a container
- Entered inside the container
- Explored Linux commands (files, users, processes, disk, logs)

This document records everything I did, along with screenshots captured during the process.

---

## Project Setup

I created a project folder:

```
~/trainee/Week5/day1-node-docker
```

Inside this folder I initialized a Node.js project and installed Express.

Then I created a simple server file:

```js
const express = require("express");
const app = express();

app.get("/", (req, res) => {
  res.send("Hello from inside Docker!");
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log("Server started on port", PORT));
```

This application starts an Express server and returns a message when accessed.

---

## Creating Dockerfile

I created a file named exactly:

```
Dockerfile
```

Content:

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .

EXPOSE 3000
CMD ["node", "server.js"]
```

This Dockerfile:

- Uses Node 20 Alpine image
- Sets working directory to `/app`
- Installs dependencies
- Copies my source code
- Exposes port 3000
- Starts Node server

---

## Building Docker Image

I built the Docker image using:

```
docker build -t day1-node-app .
```

Screenshot of build output:

![](dockerbuild.png)

This created an image named `day1-node-app`.

---

## Running the Container

I ran the container using:

```
docker run -d --name node-app -p 3000:3000 day1-node-app
```

This:

- Runs container in detached mode
- Names it `node-app`
- Maps host port 3000 to container port 3000

I verified by visiting:

```
http://localhost:3000
```

The response appeared correctly.

---

## Viewing Logs

To confirm the server was running, I checked logs:

```
docker logs node-app
```

Screenshot:

![](logs.png)

This showed:

```
Server started on port 3000
```

Meaning the Node server started successfully inside the container.

---

## Entering the Container (Like SSH)

I entered inside the container using:

```
docker exec -it node-app /bin/sh
```

Screenshot:

![](terminalcommand1.png)

Now my terminal prompt changed, indicating I was inside the container environment.

---

## Exploring File System

Commands executed:

```
pwd
ls
ls -la
ls -la /
ls -la /app
```

Screenshot:

![](terminalcommand2.png)

Observations:

- `/app` contains my project files
- Linux root folders like `/bin`, `/etc`, `/usr`, `/var` exist
- Confirms container is a minimal Linux OS

---

## Users & Permissions

Commands:

```
whoami
id
cat /etc/passwd | head
ls -la /app
```

Screenshot:

![](userpermission.png)

Observations:

- Default user is root
- User information is stored in `/etc/passwd`
- Files have Linux permission bits (rwx)

---

## Processes Inside Container

Commands:

```
ps
ps aux
top
```

Screenshot:

![](process.png)

Observations:

- Node server is running as a process
- Only few processes exist compared to full OS
- Confirms containers run minimal processes

---

## Disk Usage

Commands:

```
df -h
du -sh /app
```

Screenshot:

![](disk.png)

Observations:

- Shows filesystem mounted inside container
- `/app` directory size shows app footprint

---

## Exiting Container

```
exit
```

Returned back to host terminal.

---

## Docker Fundamentals Checked

On host machine:

```
docker images
docker ps
docker network ls
docker volume ls
```

This confirmed:

- My image exists
- Container is running
- Default bridge network exists

---

## What I Learned

- Containers run a real Linux environment
- Docker images package OS + runtime + app
- Container filesystem is isolated
- Processes inside container behave like Linux processes
- Logs are accessed using Docker
- Port mapping is required to access app

---

## Final Result

I successfully:

- Built a Node.js application
- Created Docker image
- Ran container
- Entered container
- Explored Linux internals

This simulates how production servers work at a basic level using Docker.

---

