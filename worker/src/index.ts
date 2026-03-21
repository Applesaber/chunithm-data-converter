// Cloudflare Worker: CORS proxy for diving-fish API
// Only proxies requests to www.diving-fish.com

interface Env {
  ALLOWED_ORIGIN: string
}

const ALLOWED_TARGET = 'https://www.diving-fish.com'

function corsHeaders(origin: string): Record<string, string> {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Import-Token, Developer-Token',
    'Access-Control-Max-Age': '86400',
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const origin = request.headers.get('Origin') || ''
    const allowedOrigin = env.ALLOWED_ORIGIN || 'https://munet-oss.github.io'

    // Also allow localhost for development
    const isAllowed = origin === allowedOrigin
      || origin.startsWith('http://localhost:')
      || origin.startsWith('http://127.0.0.1:')

    if (!isAllowed && origin !== '') {
      return new Response('Forbidden', { status: 403 })
    }

    const responseOrigin = origin || allowedOrigin

    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: corsHeaders(responseOrigin),
      })
    }

    // Extract target URL from query parameter
    const url = new URL(request.url)
    const targetUrl = url.searchParams.get('url')

    if (!targetUrl) {
      return new Response(JSON.stringify({ error: 'Missing ?url= parameter' }), {
        status: 400,
        headers: { ...corsHeaders(responseOrigin), 'Content-Type': 'application/json' },
      })
    }

    // Only allow proxying to diving-fish
    if (!targetUrl.startsWith(ALLOWED_TARGET)) {
      return new Response(JSON.stringify({ error: 'Only diving-fish.com is allowed' }), {
        status: 403,
        headers: { ...corsHeaders(responseOrigin), 'Content-Type': 'application/json' },
      })
    }

    // Forward the request, preserving auth headers
    const proxyHeaders = new Headers()
    const forwardHeaders = ['content-type', 'import-token', 'developer-token']
    for (const name of forwardHeaders) {
      const value = request.headers.get(name)
      if (value) proxyHeaders.set(name, value)
    }

    const proxyResponse = await fetch(targetUrl, {
      method: request.method,
      headers: proxyHeaders,
      body: request.method !== 'GET' ? request.body : undefined,
    })

    // Return response with CORS headers
    const responseHeaders = new Headers(proxyResponse.headers)
    for (const [key, value] of Object.entries(corsHeaders(responseOrigin))) {
      responseHeaders.set(key, value)
    }

    return new Response(proxyResponse.body, {
      status: proxyResponse.status,
      headers: responseHeaders,
    })
  },
}
