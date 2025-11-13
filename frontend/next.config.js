// Endpoints for rewriting API requests to the backend server
// Create as constants variables in frontend

/** @type {import('next').NextConfig} */
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://backend:8000/:path*',
      },
      {
        source: '/api/voronoi/2dexample',
        destination: 'http://backend:8000/voronoi/2dexample',
      },
      {
        source: '/api/voronoi/2d',
        destination: 'http://backend:8000/voronoi/2d',
      },
      {
        source: '/api/voronoi/stream',
        destination: 'http://backend:8000/voronoi/stream',
      },
      {
        source: '/api/test/ga',
        destination: 'http://backend:8000/test/ga',
      },
      {
        source: '/api/test/ga_async',
        destination: 'http://backend:8000/test/ga_async',
      },
    ];
  },
};
