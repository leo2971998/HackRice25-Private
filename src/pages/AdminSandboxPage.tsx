import { useEffect, useState } from "react";
import { Users, CreditCard, PlusCircle, DollarSign, ShoppingCart, CheckCircle, AlertCircle, Settings, Database } from "lucide-react";
import axios from "axios";
import toast from "react-hot-toast";

const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE || "/api", timeout: 15000 });

export default function AdminSandboxPage() {
  const [customers, setCustomers] = useState<any[]>([]);
  const [customerId, setCustomerId] = useState<string>("");
  const [accountId, setAccountId] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [custForm, setCustForm] = useState({
    first_name: "John",
    last_name: "Doe",
    address: { street_number: "123", street_name: "Main St", city: "Houston", state: "TX", zip: "77002" }
  });

  const [acctForm, setAcctForm] = useState({ type: "Checking", nickname: "Main Checking", rewards: 0, balance: 5000 });

  const [depForm, setDepForm] = useState({ amount: 1200, description: "Paycheck", transaction_date: new Date().toISOString().slice(0,10) });
  const [purForm, setPurForm] = useState({ amount: 6.58, description: "Starbucks Coffee", purchase_date: new Date().toISOString().slice(0,10) });

  async function reload() {
    try {
      setLoading(true);
      const { data } = await api.get("/nessie/customers");
      setCustomers(Array.isArray(data) ? data : []);
    } catch (error) {
      toast.error("Failed to load customers");
      setCustomers([]);
    } finally {
      setLoading(false);
    }
  }
  
  useEffect(() => { reload(); }, []);

  async function createCustomer() {
    try {
      setLoading(true);
      const { data } = await api.post("/nessie/customers", custForm);
      setCustomerId(data?._id || "");
      toast.success("Customer created successfully!");
      await reload();
    } catch (error) {
      toast.error("Failed to create customer");
    } finally {
      setLoading(false);
    }
  }
  
  async function createAccount() {
    if (!customerId) {
      toast.error("Please select a customer first");
      return;
    }
    try {
      setLoading(true);
      const { data } = await api.post(`/nessie/customers/${customerId}/accounts`, acctForm);
      setAccountId(data?._id || "");
      toast.success("Account created successfully!");
    } catch (error) {
      toast.error("Failed to create account");
    } finally {
      setLoading(false);
    }
  }
  
  async function addDeposit() {
    if (!accountId) {
      toast.error("Please create/select an account first");
      return;
    }
    try {
      setLoading(true);
      await api.post(`/nessie/accounts/${accountId}/deposits`, depForm);
      toast.success("Deposit added successfully!");
    } catch (error) {
      toast.error("Failed to add deposit");
    } finally {
      setLoading(false);
    }
  }
  
  async function addPurchase() {
    if (!accountId) {
      toast.error("Please create/select an account first");
      return;
    }
    try {
      setLoading(true);
      await api.post(`/nessie/accounts/${accountId}/purchases`, purForm);
      toast.success("Purchase added successfully!");
    } catch (error) {
      toast.error("Failed to add purchase");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-dark-100 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="bg-dark-200 rounded-2xl shadow-xl p-6 border border-dark-400">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-full p-3">
                <Settings className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
                <p className="text-dark-900">Manage customers, accounts, and transactions</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-dark-900 bg-dark-300 hover:bg-dark-400 rounded-lg transition-colors"
              >
                <Database className="h-4 w-4" />
                <span>{showAdvanced ? 'Hide' : 'Show'} Advanced</span>
              </button>
              <div className="text-right">
                <div className="text-sm font-medium text-white">{customers.length} Customers</div>
                <div className="text-xs text-dark-900">Total managed</div>
              </div>
            </div>
          </div>
        </div>

        {/* Customer Management */}
        <div className="bg-dark-200 rounded-2xl shadow-xl overflow-hidden border border-dark-400">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4">
            <div className="flex items-center space-x-3">
              <Users className="h-6 w-6 text-white" />
              <h2 className="text-xl font-semibold text-white">Customer Management</h2>
            </div>
          </div>
          
          <div className="p-6 space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Create Customer Form */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
                  <PlusCircle className="h-5 w-5 text-blue-600" />
                  <span>Create New Customer</span>
                </h3>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-dark-900 mb-1">First Name</label>
                      <input
                        type="text"
                        value={custForm.first_name}
                        onChange={(e) => setCustForm({...custForm, first_name: e.target.value})}
                        className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-dark-900 mb-1">Last Name</label>
                      <input
                        type="text"
                        value={custForm.last_name}
                        onChange={(e) => setCustForm({...custForm, last_name: e.target.value})}
                        className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-dark-900 mb-1">Street</label>
                      <input
                        type="text"
                        value={`${custForm.address.street_number} ${custForm.address.street_name}`}
                        onChange={(e) => {
                          const parts = e.target.value.split(' ');
                          setCustForm({
                            ...custForm, 
                            address: {
                              ...custForm.address,
                              street_number: parts[0] || '',
                              street_name: parts.slice(1).join(' ') || ''
                            }
                          });
                        }}
                        className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-dark-900 mb-1">City</label>
                      <input
                        type="text"
                        value={custForm.address.city}
                        onChange={(e) => setCustForm({...custForm, address: {...custForm.address, city: e.target.value}})}
                        className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-dark-900 mb-1">State</label>
                      <input
                        type="text"
                        value={custForm.address.state}
                        onChange={(e) => setCustForm({...custForm, address: {...custForm.address, state: e.target.value}})}
                        className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-dark-900 mb-1">ZIP Code</label>
                      <input
                        type="text"
                        value={custForm.address.zip}
                        onChange={(e) => setCustForm({...custForm, address: {...custForm.address, zip: e.target.value}})}
                        className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                  </div>
                  
                  <button 
                    onClick={createCustomer}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {loading ? (
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <>
                        <PlusCircle className="h-4 w-4" />
                        <span>Create Customer</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Customer List */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
                  <Users className="h-5 w-5 text-green-600" />
                  <span>Existing Customers</span>
                </h3>
                
                <div className="space-y-3">
                  <select 
                    value={customerId} 
                    onChange={(e) => setCustomerId(e.target.value)}
                    className="w-full rounded-lg border-2 border-dark-400 px-3 py-3 text-sm focus:border-blue-500 focus:outline-none"
                  >
                    <option value="">— Select a customer —</option>
                    {customers.map((c: any) => (
                      <option key={c._id} value={c._id}>
                        {c.first_name} {c.last_name} • {c._id}
                      </option>
                    ))}
                  </select>
                  
                  {customers.length > 0 ? (
                    <div className="max-h-48 overflow-y-auto space-y-2">
                      {customers.map((customer: any) => (
                        <div 
                          key={customer._id}
                          className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                            customerId === customer._id 
                              ? 'border-blue-500 bg-blue-50' 
                              : 'border-dark-400 hover:border-gray-300'
                          }`}
                          onClick={() => setCustomerId(customer._id)}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="font-medium text-white">
                                {customer.first_name} {customer.last_name}
                              </div>
                              <div className="text-xs text-dark-900">{customer._id}</div>
                            </div>
                            {customerId === customer._id && (
                              <CheckCircle className="h-5 w-5 text-blue-600" />
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-dark-900">
                      <Users className="h-12 w-12 mx-auto mb-3 opacity-50" />
                      <p>No customers found</p>
                      <p className="text-xs">Create your first customer above</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Account Management */}
        <div className="bg-dark-200 rounded-2xl shadow-xl overflow-hidden border border-dark-400">
          <div className="bg-gradient-to-r from-green-600 to-emerald-600 px-6 py-4">
            <div className="flex items-center space-x-3">
              <CreditCard className="h-6 w-6 text-white" />
              <h2 className="text-xl font-semibold text-white">Account Management</h2>
            </div>
          </div>
          
          <div className="p-6">
            {!customerId ? (
              <div className="text-center py-8 text-dark-900">
                <AlertCircle className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p className="font-medium">Select a customer first</p>
                <p className="text-sm">Choose a customer from the list above to manage their accounts</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-dark-900 mb-1">Account Type</label>
                    <select
                      value={acctForm.type}
                      onChange={(e) => setAcctForm({...acctForm, type: e.target.value})}
                      className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-green-500 focus:outline-none"
                    >
                      <option value="Checking">Checking</option>
                      <option value="Savings">Savings</option>
                      <option value="Credit Card">Credit Card</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-dark-900 mb-1">Nickname</label>
                    <input
                      type="text"
                      value={acctForm.nickname}
                      onChange={(e) => setAcctForm({...acctForm, nickname: e.target.value})}
                      className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-green-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-dark-900 mb-1">Initial Balance</label>
                    <input
                      type="number"
                      value={acctForm.balance}
                      onChange={(e) => setAcctForm({...acctForm, balance: Number(e.target.value)})}
                      className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-green-500 focus:outline-none"
                    />
                  </div>
                </div>
                
                <button 
                  onClick={createAccount}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    <>
                      <CreditCard className="h-4 w-4" />
                      <span>Create Account</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Transaction Management */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Deposits */}
          <div className="bg-dark-200 rounded-2xl shadow-xl overflow-hidden border border-dark-400">
            <div className="bg-gradient-to-r from-emerald-600 to-green-600 px-6 py-4">
              <div className="flex items-center space-x-3">
                <DollarSign className="h-6 w-6 text-white" />
                <h3 className="text-lg font-semibold text-white">Add Deposit</h3>
              </div>
            </div>
            
            <div className="p-6">
              {!accountId ? (
                <div className="text-center py-8 text-dark-900">
                  <AlertCircle className="h-8 w-8 mx-auto mb-3 opacity-50" />
                  <p className="text-sm">Create an account first</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-dark-900 mb-1">Amount</label>
                    <input
                      type="number"
                      step="0.01"
                      value={depForm.amount}
                      onChange={(e) => setDepForm({...depForm, amount: Number(e.target.value)})}
                      className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-dark-900 mb-1">Description</label>
                    <input
                      type="text"
                      value={depForm.description}
                      onChange={(e) => setDepForm({...depForm, description: e.target.value})}
                      className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-dark-900 mb-1">Date</label>
                    <input
                      type="date"
                      value={depForm.transaction_date}
                      onChange={(e) => setDepForm({...depForm, transaction_date: e.target.value})}
                      className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                  
                  <button 
                    onClick={addDeposit}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {loading ? (
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <>
                        <DollarSign className="h-4 w-4" />
                        <span>Add Deposit</span>
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Purchases */}
          <div className="bg-dark-200 rounded-2xl shadow-xl overflow-hidden border border-dark-400">
            <div className="bg-gradient-to-r from-red-600 to-rose-600 px-6 py-4">
              <div className="flex items-center space-x-3">
                <ShoppingCart className="h-6 w-6 text-white" />
                <h3 className="text-lg font-semibold text-white">Add Purchase</h3>
              </div>
            </div>
            
            <div className="p-6">
              {!accountId ? (
                <div className="text-center py-8 text-dark-900">
                  <AlertCircle className="h-8 w-8 mx-auto mb-3 opacity-50" />
                  <p className="text-sm">Create an account first</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-dark-900 mb-1">Amount</label>
                    <input
                      type="number"
                      step="0.01"
                      value={purForm.amount}
                      onChange={(e) => setPurForm({...purForm, amount: Number(e.target.value)})}
                      className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-red-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-dark-900 mb-1">Description</label>
                    <input
                      type="text"
                      value={purForm.description}
                      onChange={(e) => setPurForm({...purForm, description: e.target.value})}
                      className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-red-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-dark-900 mb-1">Date</label>
                    <input
                      type="date"
                      value={purForm.purchase_date}
                      onChange={(e) => setPurForm({...purForm, purchase_date: e.target.value})}
                      className="w-full rounded-lg border-2 border-dark-400 px-3 py-2 text-sm focus:border-red-500 focus:outline-none"
                    />
                  </div>
                  
                  <button 
                    onClick={addPurchase}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {loading ? (
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <>
                        <ShoppingCart className="h-4 w-4" />
                        <span>Add Purchase</span>
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Advanced Debug Info */}
        {showAdvanced && (
          <div className="bg-dark-200 rounded-2xl shadow-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
              <Database className="h-5 w-5 text-dark-900" />
              <span>Debug Information</span>
            </h3>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-dark-900 mb-2">Customer Form Data</h4>
                <pre className="text-xs bg-dark-300/60 p-3 rounded-lg overflow-auto max-h-32 border">
                  {JSON.stringify(custForm, null, 2)}
                </pre>
              </div>
              <div>
                <h4 className="font-medium text-dark-900 mb-2">Account Form Data</h4>
                <pre className="text-xs bg-dark-300/60 p-3 rounded-lg overflow-auto max-h-32 border">
                  {JSON.stringify(acctForm, null, 2)}
                </pre>
              </div>
              <div>
                <h4 className="font-medium text-dark-900 mb-2">Deposit Form Data</h4>
                <pre className="text-xs bg-dark-300/60 p-3 rounded-lg overflow-auto max-h-32 border">
                  {JSON.stringify(depForm, null, 2)}
                </pre>
              </div>
              <div>
                <h4 className="font-medium text-dark-900 mb-2">Purchase Form Data</h4>
                <pre className="text-xs bg-dark-300/60 p-3 rounded-lg overflow-auto max-h-32 border">
                  {JSON.stringify(purForm, null, 2)}
                </pre>
              </div>
            </div>
            
            <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <p className="text-xs text-amber-800">
                <strong>Note:</strong> Field names for deposits/purchases may vary by endpoint. 
                If you encounter a 400 error, consult the Swagger documentation to confirm the correct schema for your API path.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}