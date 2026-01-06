const os = require("os");

console.log("Name of OS:", os.platform());

console.log("Architecture:", os.arch());

console.log("CPU Cores:", os.cpus().length);

// Total memory converted bytes to GB
console.log("Total Memory:", (os.totalmem() / 1024 / 1024 / 1024).toFixed(2), "GB");

// System uptime converted second to minutes
console.log("System Uptime:", Math.floor(os.uptime() / 60), "minutes");

console.log("Current Logged User:", os.userInfo().username);

console.log("Node Path:", process.execPath);
