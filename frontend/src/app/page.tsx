"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";
import { AlertCircle, ArrowDownCircle, ArrowUpCircle, CheckCircle } from "lucide-react";

interface CompetitorPrice {
  id: number;
  competitor_name: string;
  price: number;
  discount_price?: number;
  in_stock: boolean;
  timestamp: string;
}

interface Recommendation {
  action: "raise" | "lower" | "keep";
  suggested_price: number;
  reason: string;
  timestamp: string;
}

interface Product {
  id: number;
  name: string;
  my_price: number;
  url: string;
  competitor_prices: CompetitorPrice[];
  latest_recommendation?: Recommendation;
}

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchProducts = async () => {
    try {
      const res = await axios.get("http://localhost:8000/products");
      setProducts(res.data);
    } catch (error) {
      console.error("Failed to fetch products:", error);
    } finally {
      setLoading(false);
    }
  };

  const triggerScan = async (productId: number) => {
    try {
      await axios.post(`http://localhost:8000/trigger_scan/${productId}`);
      alert("Scan triggered! It will run in the background. Refresh in a few seconds.");
    } catch (error) {
      console.error("Failed to trigger scan:", error);
      alert("Failed to trigger scan.");
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 text-black">
        <p className="text-xl">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8 text-black">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">E-Commerce AI Monitoring</h1>
          <p className="text-gray-600 mt-2">
            Track competitors, analyze prices with LangGraph agents, and maximize profit.
          </p>
        </header>

        <div className="space-y-8">
          {products.map((product) => {
            // Prepare data for Recharts
            const chartData = [...product.competitor_prices]
              .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
              .map((cp) => ({
                time: new Date(cp.timestamp).toLocaleTimeString(),
                [cp.competitor_name]: cp.price,
                "My Price": product.my_price,
              }));

            const rec = product.latest_recommendation;

            return (
              <div key={product.id} className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h2 className="text-xl font-bold">{product.name}</h2>
                    <p className="text-gray-500">My Price: ${product.my_price.toFixed(2)}</p>
                    <a href={product.url} target="_blank" rel="noreferrer" className="text-blue-500 text-sm hover:underline">
                      View Competitor Page
                    </a>
                  </div>
                  <button
                    onClick={() => triggerScan(product.id)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    Run AI Analysis
                  </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Chart Section */}
                  <div className="lg:col-span-2 h-72">
                    {chartData.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} />
                          <XAxis dataKey="time" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Line type="monotone" dataKey="My Price" stroke="#10b981" strokeWidth={2} />
                          {Array.from(new Set(product.competitor_prices.map((p) => p.competitor_name))).map((comp, idx) => (
                            <Line
                              key={comp}
                              type="monotone"
                              dataKey={comp}
                              stroke={['#ef4444', '#f59e0b', '#3b82f6'][idx % 3]}
                              strokeWidth={2}
                            />
                          ))}
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-full flex items-center justify-center border-2 border-dashed border-gray-200 rounded-lg">
                        <p className="text-gray-400">No competitor data yet. Run an analysis!</p>
                      </div>
                    )}
                  </div>

                  {/* Recommendation Section */}
                  <div className="bg-gray-50 rounded-lg p-5 border border-gray-200 flex flex-col justify-center">
                    <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
                      AI Recommendation
                    </h3>
                    {rec ? (
                      <div>
                        <div className="flex items-center space-x-2 mb-3">
                          {rec.action === "raise" && <ArrowUpCircle className="text-green-500 w-8 h-8" />}
                          {rec.action === "lower" && <ArrowDownCircle className="text-red-500 w-8 h-8" />}
                          {rec.action === "keep" && <CheckCircle className="text-blue-500 w-8 h-8" />}
                          <span className="text-xl font-bold capitalize">{rec.action} Price</span>
                        </div>
                        <p className="text-3xl font-black mb-2">${rec.suggested_price.toFixed(2)}</p>
                        <p className="text-sm text-gray-600 italic bg-white p-3 rounded shadow-sm border border-gray-100">
                          "{rec.reason}"
                        </p>
                      </div>
                    ) : (
                      <div className="text-center text-gray-400">
                        <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>No recommendations yet.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
