const http = require('http');
const url = require('url');

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);

  // /echo → return request headers
  if (parsedUrl.pathname === '/echo') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(req.headers, null, 2));
  }

  // /slow?ms=3000 → delay response
  else if (parsedUrl.pathname === '/slow') {
    const ms = Number(parsedUrl.query.ms) || 1000;

    setTimeout(() => {
      res.writeHead(200);
      res.end(`Response delayed by ${ms} ms`);
    }, ms);
  }

  // /cache → cache headers + ETag handling
  else if (parsedUrl.pathname === '/cache') {
    const etag = '"my-etag-1"';

    // If client already has this version
    if (req.headers['if-none-match'] === etag) {
      res.writeHead(304);
      return res.end();
    }

    // Send fresh response with cache headers
    res.writeHead(200, {
      'Cache-Control': 'public, max-age=60',
      'ETag': etag,
      'Content-Type': 'text/plain'
    });
    res.end('Cache demo');
  }

  // Default route
  else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

server.listen(3000, () => {
  console.log('Server running at http://localhost:3000');
});
