## Error 1: LocalStorage JSON parse error

**Problem**
In script.js, 
```bash
localStorage.setItem("todos", todos);
```
LocalStorage expects strings but an array was stored directly.

**Error Message**
Uncaught SyntaxError: Unexpected token o in JSON

![Error message](screenshots/image.jpg)

**Cause**
Missing JSON.stringify while saving data.

**Fix**
Wrapped the data using JSON.stringify before storing.

## Error: Can't fetch todo 

### Description
The Todo application failed to load saved tasks on page refresh and displayed a
"can't fetch todo" error in the console.

### Error Message
can't fetch todo  
Unexpected token u in JSON at position 0

### Where it occurred
During application initialization while calling `loadtodos()` inside a try–catch block.

### Root Cause
The app attempted to parse `null` using `JSON.parse()` because an incorrect
localStorage key was used while fetching saved todos.


![Error message](screenshots/error.jpg)