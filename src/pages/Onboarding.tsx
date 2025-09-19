import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import {
  createPlaidLinkToken,
  exchangePlaidPublicToken,
  getPlaidStatus,
} from "@/api/client";
import { me } from "@/api/auth";
import { useAuth } from "@/context/Auth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/Card";

export default function Onboarding() {
  const [linkToken, setLinkToken] = useState<string | null>(null);
  const [status, setStatus] = useState<{ linked: boolean; balances?: any }>({ linked: false });
  const [loading, setLoading] = useState(false);
  const { setUser } = useAuth();
  const navigate = useNavigate();

  const refreshStatus = async () => {
    try {
      const data = await getPlaidStatus();
      setStatus(data);
      if (data.linked) {
        const updated = await me();
        setUser(updated);
        navigate("/dashboard");
      }
    } catch (error) {
      setStatus({ linked: false });
    }
  };

  useEffect(() => {
    refreshStatus();
  }, []);

  const handleCreateLinkToken = async () => {
    setLoading(true);
    try {
      const token = await createPlaidLinkToken();
      setLinkToken(token.link_token);
      toast.success("Plaid link token generated");
    } catch (error) {
      toast.error("Failed to create link token");
    } finally {
      setLoading(false);
    }
  };

  const handleSandboxExchange = async () => {
    if (!linkToken) {
      toast.error("Generate a link token first");
      return;
    }
    setLoading(true);
    try {
      await exchangePlaidPublicToken({
        public_token: linkToken,
        institution: { name: "Plaid Sandbox Bank" },
      });
      toast.success("Accounts linked");
      await refreshStatus();
    } catch (error) {
      toast.error("Could not link accounts");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-12 px-4 bg-dark-100 min-h-[calc(100vh-8rem)]">
      <div className="max-w-3xl mx-auto space-y-8">
        <Card className="bg-dark-200/60 border border-dark-400/60">
          <CardHeader>
            <CardTitle className="text-white text-2xl">Connect your accounts</CardTitle>
            <p className="text-dark-800 text-sm">
              Inflate-Wise uses Plaid to securely pull transactions so Gemini can personalise your inflation model.
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-dark-300/50 border border-dark-400/60 rounded-xl p-6 space-y-4">
              <h3 className="text-lg font-semibold text-white">Step 1 · Generate a Plaid Link token</h3>
              <p className="text-dark-800 text-sm">
                In production this token is passed into Plaid Link on the client. For the hackathon sandbox, click the button to create a token and preview the payload.
              </p>
              <button
                onClick={handleCreateLinkToken}
                disabled={loading}
                className="inline-flex items-center justify-center px-4 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-sm transition disabled:opacity-60"
              >
                {loading ? "Working..." : "Create link token"}
              </button>
              {linkToken && (
                <pre className="bg-dark-800 text-primary-200 text-xs rounded-lg p-4 overflow-x-auto">
                  {linkToken}
                </pre>
              )}
            </div>

            <div className="bg-dark-300/50 border border-dark-400/60 rounded-xl p-6 space-y-4">
              <h3 className="text-lg font-semibold text-white">Step 2 · Complete sandbox linking</h3>
              <p className="text-dark-800 text-sm">
                Normally Plaid Link returns a public token. We simulate that handshake here so you can move straight to the dashboard.
              </p>
              <button
                onClick={handleSandboxExchange}
                disabled={loading || !linkToken}
                className="inline-flex items-center justify-center px-4 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-sm transition disabled:opacity-60"
              >
                {loading ? "Linking..." : "Exchange sandbox token"}
              </button>
              <p className="text-dark-400 text-xs">
                Tip: in production you would launch Plaid Link and call this endpoint inside the onSuccess callback.
              </p>
            </div>

            <div className="bg-dark-300/50 border border-dark-400/60 rounded-xl p-6 space-y-3">
              <h3 className="text-lg font-semibold text-white">Current status</h3>
              {status.linked ? (
                <>
                  <p className="text-emerald-300">Accounts linked successfully.</p>
                  <div className="bg-dark-900/50 rounded-lg p-4 text-sm text-dark-200">
                    <pre className="whitespace-pre-wrap break-all">{JSON.stringify(status.balances, null, 2)}</pre>
                  </div>
                </>
              ) : (
                <p className="text-dark-800 text-sm">No financial institutions linked yet.</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
