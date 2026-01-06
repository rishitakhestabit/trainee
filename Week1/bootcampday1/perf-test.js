const fs = require("fs");

const results = {};

// -------- BUFFER TEST --------
console.log("BUFFER TEST START");

let startTime = Date.now();
let startMemory = process.memoryUsage().heapUsed;

fs.readFile("large-file.txt", (err, data) => {
  if (err) throw err;

  let endTime = Date.now();
  let endMemory = process.memoryUsage().heapUsed;

  results.buffer = {
    time_ms: endTime - startTime,
    memory_bytes: endMemory - startMemory,
  };

  console.log("BUFFER TEST DONE");

  // -------- STREAM TEST --------
  console.log("STREAM TEST START");

  startTime = Date.now();
  startMemory = process.memoryUsage().heapUsed;

  const stream = fs.createReadStream("large-file.txt");

  stream.on("data", () => {});

  stream.on("end", () => {
    endTime = Date.now();
    endMemory = process.memoryUsage().heapUsed;

    results.stream = {
      time_ms: endTime - startTime,
      memory_bytes: endMemory - startMemory,
    };

    console.log("STREAM TEST DONE");

    fs.writeFileSync(
      "logs/day1-perf.json",
      JSON.stringify(results, null, 2)
    );

    console.log("Final Result:", results);
  });
});

