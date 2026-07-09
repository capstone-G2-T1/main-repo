// Minimal landing page just to prove the frontend container is reachable
// on http://localhost:3000. Real UI (vehicle picker, chat, citations)
// gets built in a later story.

export default function Home() {
  return (
    <main style={{ fontFamily: "sans-serif", padding: "2rem" }}>
      <h1>AI.SPIRE — Vehicle Manual RAG</h1>
      <p>Frontend is up. Backend API: {process.env.NEXT_PUBLIC_API_URL}</p>
    </main>
  );
}
