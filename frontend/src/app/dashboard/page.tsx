export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-6">PRISM Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-700">
          <h2 className="text-xl font-semibold">Active PRs</h2>
          <p className="text-4xl font-bold mt-4 text-blue-400">12</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg shadow-lg border border-red-900/30">
          <h2 className="text-xl font-semibold">High Risk</h2>
          <p className="text-4xl font-bold mt-4 text-red-500">3</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-700">
          <h2 className="text-xl font-semibold">Avg Risk Score</h2>
          <p className="text-4xl font-bold mt-4 text-yellow-500">42/100</p>
        </div>
      </div>
    </div>
  );
}
