import { useEffect, useState } from "react";
import axios from "axios";

const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE || "/api", timeout: 15000 });

export default function AdminSandboxPage() {
  const [customers, setCustomers] = useState<any[]>([]);
  const [customerId, setCustomerId] = useState<string>("");
  const [accountId, setAccountId] = useState<string>("");

  const [custForm, setCustForm] = useState({
    first_name: "John",
    last_name: "Doe",
    address: { street_number: "123", street_name: "Main St", city: "Houston", state: "TX", zip: "77002" }
  });

  const [acctForm, setAcctForm] = useState({ type: "Checking", nickname: "Main Checking", rewards: 0, balance: 5000 });

  const [depForm, setDepForm] = useState({ amount: 1200, description: "Paycheck", transaction_date: new Date().toISOString().slice(0,10) });
  const [purForm, setPurForm] = useState({ amount: 6.58, description: "Starbucks Coffee", purchase_date: new Date().toISOString().slice(0,10) });

  async function reload() {
    const { data } = await api.get("/nessie/customers");
    setCustomers(Array.isArray(data) ? data : []);
  }
  useEffect(() => { reload(); }, []);

  async function createCustomer() {
    const { data } = await api.post("/nessie/customers", custForm);
    setCustomerId(data?._id || "");
    await reload();
  }
  async function createAccount() {
    if (!customerId) return alert("Pick customerId from dropdown after creating or selecting a customer");
    const { data } = await api.post(`/nessie/customers/${customerId}/accounts`, acctForm);
    setAccountId(data?._id || "");
  }
  async function addDeposit() {
    if (!accountId) return alert("Create/select an account first");
    await api.post(`/nessie/accounts/${accountId}/deposits`, depForm);
  }
  async function addPurchase() {
    if (!accountId) return alert("Create/select an account first");
    await api.post(`/nessie/accounts/${accountId}/purchases`, purForm);
  }

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Admin Sandbox</h1>

      <section className="rounded-xl border p-4 space-y-3">
        <h2 className="font-semibold">1) Create Customer</h2>
        <pre className="text-xs bg-neutral-100 dark:bg-neutral-900 p-2 rounded">{JSON.stringify(custForm, null, 2)}</pre>
        <button className="rounded bg-blue-600 text-white px-3 py-2" onClick={createCustomer}>Create Customer</button>

        <div className="mt-3">
          <label className="text-sm opacity-70">Existing customers:</label>
          <select className="ml-2 border px-2 py-1" value={customerId} onChange={(e)=>setCustomerId(e.target.value)}>
            <option value="">— select —</option>
            {customers.map((c:any)=> <option key={c._id} value={c._id}>{c.first_name} {c.last_name} • {c._id}</option>)}
          </select>
        </div>
      </section>

      <section className="rounded-xl border p-4 space-y-3">
        <h2 className="font-semibold">2) Create Account</h2>
        <pre className="text-xs bg-neutral-100 dark:bg-neutral-900 p-2 rounded">{JSON.stringify(acctForm, null, 2)}</pre>
        <button className="rounded bg-blue-600 text-white px-3 py-2" onClick={createAccount}>Create Account</button>
      </section>

      <section className="grid md:grid-cols-2 gap-4">
        <div className="rounded-xl border p-4 space-y-3">
          <h2 className="font-semibold">3a) Add Deposit</h2>
          <pre className="text-xs bg-neutral-100 dark:bg-neutral-900 p-2 rounded">{JSON.stringify(depForm, null, 2)}</pre>
          <button className="rounded bg-green-600 text-white px-3 py-2" onClick={addDeposit}>Post Deposit</button>
        </div>
        <div className="rounded-xl border p-4 space-y-3">
          <h2 className="font-semibold">3b) Add Purchase</h2>
          <pre className="text-xs bg-neutral-100 dark:bg-neutral-900 p-2 rounded">{JSON.stringify(purForm, null, 2)}</pre>
          <button className="rounded bg-rose-600 text-white px-3 py-2" onClick={addPurchase}>Post Purchase</button>
        </div>
      </section>

      <p className="text-xs opacity-70">Note: exact field names for deposits/purchases can vary by endpoint; if you hit a 400, open the Swagger docs and confirm the schema for your path.</p>
    </div>
  );
}