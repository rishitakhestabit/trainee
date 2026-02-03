# DAY 1 — Node + Project Architecture

This document explains my Day 1 backend setup as a continuous journey, written in simple language and in my own words. It describes what I created, why I created it, and how everything fits together, from project initialization to running working APIs.

---

I began by creating a new Node.js project and initializing npm using `npm init -y`. After that, I installed the core dependencies required for this architecture: Express for the server, dotenv for environment configuration, mongoose for database connection, and pino with pino-pretty for logging. Once installation was complete, I opened the package.json file and added `"type": "module"` so that I could use ES module syntax with import and export statements. This step was important because the entire project uses modern JavaScript module syntax.


Next, I created the mandatory folder structure as specified in the task. I used a single command to generate all folders inside the src directory, including config, loaders, models, routes, controllers, services, repositories, middlewares, utils, jobs, and logs. I did not skip any folder even if some are empty for now. The purpose of this structure is to follow layered architecture and ensure that each type of responsibility has its own place in the project.


---

After setting up the folders, I created three environment files: .env.local, .env.dev, and .env.prod. Inside each file, I defined values such as PORT and DB_URL. For example, in .env.local I defined port 4000 and a local MongoDB connection string. Then I created a config loader file at src/config/index.js. This file reads NODE_ENV, loads the correct environment file using dotenv, and exports configuration values like port and database URL. Because of this, the same codebase can run in different environments without changing any code.

---

I then set up logging. I created src/utils/logger.js and configured Pino as the logger. This logger is imported wherever logging is needed. Instead of using console.log, the application now uses this centralized logger. This makes logs consistent, structured, and easier to manage.


---

For database handling, I created src/loaders/db.js. This file connects to MongoDB using mongoose and logs whether the connection is successful or fails. Keeping database connection logic inside a loader separates infrastructure concerns from application logic. Before running the project, I started MongoDB using `sudo systemctl start mongod`.


---

The most important part of the architecture is the app loader. I created src/loaders/app.js. This file is responsible for building the Express application in a controlled order. First, it creates the Express app. Then it loads middlewares such as express.json(). After that, it connects to the database using the DB loader. Finally, it mounts all routes. This ensures that the application always starts in a predictable and safe sequence.


---

To verify that the server is working, I created a health endpoint. I added src/controllers/health.controller.js and src/routes/health.routes.js. The endpoint GET /api/health returns a simple JSON response `{ "status": "OK" }`. This endpoint is useful as a basic system check.

![health](health.png)


---

To practice layered architecture, I added a small Users module with two endpoints. I created src/services/users.service.js, src/controllers/users.controller.js, and src/routes/users.routes.js. The GET /api/users endpoint returns a list of users, and the POST /api/users endpoint creates a user. The flow is Route → Controller → Service. Routes only define URLs, controllers handle request and response, and services contain logic. This separation keeps the code clean and scalable.



---

I created src/server.js as the application entry point. This file imports configuration, calls the app loader, and starts the server using app.listen. The server prints a log when it starts.

---

To run the project, I use the command `npm run local`. When the application starts, I see logs indicating that middlewares are loaded, the database is connected, routes are mounted, and the server has started on port 4000.



---

I tested the APIs using the browser and curl. I opened [http://localhost:4000/api/health](http://localhost:4000/api/health) to test the health endpoint 


![health](health.png)



and [http://localhost:4000/api/users](http://localhost:4000/api/users) to test the users list. I used a POST request with curl to create a user.

![users](users.png)



---

The startup flow of the application is as follows. server.js loads configuration, calls the app loader, middlewares are registered, the database connects, routes are mounted, and finally the server starts listening for requests.

---





