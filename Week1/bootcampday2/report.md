This file is created for my own understanding and documentation.

So the task we got to learn how to use node.js to build a command line program. Reading and processing a very large text file,Using asynchronus programming, improve speed using concurrency , measure performance(time taken)

Node.js lets us run JavaScript outside the browser instead of just in chrome, and we run node like 
```
node filename.js
```
CLI is command line interface that means a program we run using terminal commands.
We give optional(flags)like --file,--top like --top 10 to show top 10 words,--file corpus.txt means input file. 

Asynchronus programming means normally code runs one line at a time.
But when we read files and process big data,Node uses async code so it does not block the program.
like in example 
await fs.promises.readFile("file.txt")
this means waiting for file to load, not just freeze the app

Concurrency means doing multiple things at the same time that means reading a file in parts and processing each part in parallel.

So in the task,what i did was generate a large corpus file.
Then i build the cli command
node wordstat.js --file corpus.txt --top 10 --minLen 5 --unique

--file:	File to analyze
--top 10:	Top 10 repeated words
--minLen 5:	Ignore words shorter than 5
--unique:	Count unique words

If we do it without concurrency and try to read the whole file and process it once,it will is slow and blocks execution.

Instead what i did, read the file and split it into chunks and processed each chunk in parallel
