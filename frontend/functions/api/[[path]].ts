// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function onRequest(context: any) {
  // context.request contains the incoming request
  // context.env contains env variables
  const url = new URL(context.request.url);
  
  // The backend Oracle server IP and port
  const backendUrl = `http://161.118.189.191:8000${url.pathname}${url.search}`;
  
  // Forward the request to the backend
  const proxyRequest = new Request(backendUrl, {
    method: context.request.method,
    headers: context.request.headers,
    body: context.request.body,
    redirect: "manual",
  });
  
  // Return the response directly to the client
  try {
    const response = await fetch(proxyRequest);
    
    // Create a new response to allow CORS and prevent Cloudflare caching issues
    const newResponse = new Response(response.body, response);
    newResponse.headers.set("Access-Control-Allow-Origin", "*");
    
    return newResponse;
  } catch {
    return new Response(JSON.stringify({ error: "Failed to proxy request to backend" }), {
      status: 502,
      headers: { "Content-Type": "application/json" }
    });
  }
}
