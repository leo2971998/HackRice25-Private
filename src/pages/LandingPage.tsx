import { Link, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  LineChart,
  Wallet,
  Bot,
  Camera,
  PieChart,
  Sparkles,
  Shield,
} from "lucide-react";
import { Card, CardContent } from "@/components/Card";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-24">
        <section className="text-center space-y-6">
          <p className="inline-flex items-center space-x-2 px-4 py-2 rounded-full border border-primary-500/40 bg-primary-500/10 text-primary-200 text-sm">
            <Sparkles className="w-4 h-4" />
            <span>New at HackRice 2025</span>
          </p>
          <h1 className="text-4xl md:text-6xl font-bold text-white leading-tight">
            Inflate-Wise
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-primary-200">
              Your AI Co-Pilot for Beating Personal Inflation
            </span>
          </h1>
          <p className="text-xl text-white max-w-3xl mx-auto">
            Connect your real financial accounts securely with Plaid, understand how inflation affects you—not just the national average—and get personalised coaching powered by Gemini to stay ahead.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={() => navigate("/register")}
              className="px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-semibold rounded-lg shadow-lg transform hover:scale-105 transition-all duration-200 flex items-center space-x-2"
            >
              <span>Create an account</span>
              <ArrowRight className="h-5 w-5" />
            </button>
            <Link
              to="/login"
              className="px-8 py-4 border-2 border-dark-400 text-white font-semibold rounded-lg hover:border-primary-500 hover:bg-dark-200 transition-all duration-200"
            >
              Sign in
            </Link>
          </div>
        </section>

        <section className="grid md:grid-cols-3 gap-8">
          <Card hoverable>
            <CardContent className="p-8 space-y-4">
              <div className="bg-primary-500/20 rounded-lg p-3 w-fit">
                <Shield className="h-8 w-8 text-primary-400" />
              </div>
              <h3 className="text-xl font-semibold text-white">Bank-grade connections</h3>
              <p className="text-white/80">
                Plaid Link keeps credentials safe while you sync credit card and bank accounts directly into Inflate-Wise. No mock data—just your spending, refreshed automatically.
              </p>
            </CardContent>
          </Card>
          <Card hoverable>
            <CardContent className="p-8 space-y-4">
              <div className="bg-accent-emerald/20 rounded-lg p-3 w-fit">
                <LineChart className="h-8 w-8 text-accent-emerald" />
              </div>
              <h3 className="text-xl font-semibold text-white">Personal inflation index</h3>
              <p className="text-white/80">
                Gemini categorises every transaction, maps it to Bureau of Labor Statistics CPI categories, and calculates a weighted rate that reflects your actual lifestyle.
              </p>
            </CardContent>
          </Card>
          <Card hoverable>
            <CardContent className="p-8 space-y-4">
              <div className="bg-purple-500/20 rounded-lg p-3 w-fit">
                <Bot className="h-8 w-8 text-purple-300" />
              </div>
              <h3 className="text-xl font-semibold text-white">AI financial coaching</h3>
              <p className="text-white/80">
                Ask Inflate-Wise why your rate is spiking, receive actionable tips, and trigger function calls that inspect your own spending mix in real time.
              </p>
            </CardContent>
          </Card>
        </section>

        <section className="grid md:grid-cols-2 gap-8 items-stretch">
          <Card className="p-10 bg-dark-200/50 border border-dark-400/60 backdrop-blur">
            <div className="flex items-center space-x-4 mb-6">
              <Wallet className="w-10 h-10 text-primary-400" />
              <div>
                <h2 className="text-2xl font-semibold text-white">How it works</h2>
                <p className="text-white/80">Three simple steps to quantify and beat personal inflation.</p>
              </div>
            </div>
            <ol className="space-y-6 text-left">
              <li className="flex gap-4">
                <span className="w-8 h-8 rounded-full bg-primary-500/30 text-primary-200 flex items-center justify-center font-semibold">1</span>
                <div>
                  <h3 className="text-white font-semibold">Link accounts with Plaid</h3>
                  <p className="text-white/80">Use the trusted Plaid Link flow to add cards and banks from hundreds of institutions in minutes.</p>
                </div>
              </li>
              <li className="flex gap-4">
                <span className="w-8 h-8 rounded-full bg-primary-500/30 text-primary-200 flex items-center justify-center font-semibold">2</span>
                <div>
                  <h3 className="text-white font-semibold">Let Gemini organise the noise</h3>
                  <p className="text-white/80">We send transaction descriptions to Gemini with a constrained taxonomy so each purchase lands in the right CPI bucket.</p>
                </div>
              </li>
              <li className="flex gap-4">
                <span className="w-8 h-8 rounded-full bg-primary-500/30 text-primary-200 flex items-center justify-center font-semibold">3</span>
                <div>
                  <h3 className="text-white font-semibold">Track, learn, and act</h3>
                  <p className="text-white/80">Watch your personalised inflation dashboard update instantly and chat with the assistant for tailored strategies.</p>
                </div>
              </li>
            </ol>
          </Card>

          <Card className="p-10 bg-dark-200/30 border border-dark-400/60 backdrop-blur">
            <div className="flex items-center space-x-4 mb-6">
              <Camera className="w-10 h-10 text-primary-400" />
              <div>
                <h2 className="text-2xl font-semibold text-white">Bring receipts to life</h2>
                <p className="text-white/80">Multimodal uploads powered by Gemini</p>
              </div>
            </div>
            <p className="text-white/80 mb-6">
              Snap a bill or grocery receipt and let Gemini Vision extract line items automatically. Inflate-Wise categorises the expense, updates your dashboard, and summarises the impact on your inflation footprint.
            </p>
            <div className="space-y-4">
              <div className="bg-dark-300/60 border border-dark-400/50 rounded-xl p-4">
                <h4 className="text-white font-semibold mb-2">Automatic parsing</h4>
                <p className="text-white/80 text-sm">Gemini Vision reads totals, dates, and merchants in seconds—no manual data entry required.</p>
              </div>
              <div className="bg-dark-300/60 border border-dark-400/50 rounded-xl p-4">
                <h4 className="text-white font-semibold mb-2">Instant categorisation</h4>
                <p className="text-white/80 text-sm">Receipts flow straight into the same CPI-aligned model driving your personal inflation insights.</p>
              </div>
            </div>
          </Card>
        </section>

        <section className="grid md:grid-cols-3 gap-8">
          <Card hoverable>
            <CardContent className="p-8 space-y-3">
              <div className="bg-blue-500/20 rounded-lg p-3 w-fit">
                <PieChart className="h-8 w-8 text-blue-300" />
              </div>
              <h3 className="text-xl font-semibold text-white">Judge-friendly storytelling</h3>
              <p className="text-white/80">Every widget ties into CPI data and real spending so hackathon judges see a credible, production-ready path.</p>
            </CardContent>
          </Card>
          <Card hoverable>
            <CardContent className="p-8 space-y-3">
              <div className="bg-orange-500/20 rounded-lg p-3 w-fit">
                <Bot className="h-8 w-8 text-orange-300" />
              </div>
              <h3 className="text-xl font-semibold text-white">Function calling intelligence</h3>
              <p className="text-white/80">Gemini dynamically requests personal inflation snapshots before responding, ensuring advice is grounded in live numbers.</p>
            </CardContent>
          </Card>
          <Card hoverable>
            <CardContent className="p-8 space-y-3">
              <div className="bg-green-500/20 rounded-lg p-3 w-fit">
                <Sparkles className="h-8 w-8 text-green-300" />
              </div>
              <h3 className="text-xl font-semibold text-white">Designed to wow</h3>
              <p className="text-white/80">A cinematic UI, dark neon gradients, and motion states highlight complex analysis in a glanceable way.</p>
            </CardContent>
          </Card>
        </section>

        <section className="text-center space-y-4">
          <h2 className="text-3xl font-bold text-white">Ready to know your real inflation rate?</h2>
          <p className="text-white/80 max-w-2xl mx-auto">
            Start free, link a credit card, and let Inflate-Wise become the smartest teammate on your financial journey.
          </p>
          <button
            onClick={() => navigate("/onboarding")}
            className="px-8 py-4 bg-primary-500 hover:bg-primary-600 text-white font-semibold rounded-lg shadow-lg transition-all duration-200 flex items-center space-x-2 mx-auto"
          >
            <span>Begin onboarding</span>
            <ArrowRight className="h-5 w-5" />
          </button>
        </section>
      </main>
    </div>
  );
}
