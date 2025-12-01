import gradio as gr

html_content = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>咖啡寄杯追蹤器</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { margin: 0; padding: 0; min-height: 100vh; }
        #root { min-height: 100vh; }
    </style>
</head>
<body>
    <div id="root"></div>
    
    <script type="text/babel">
        const { useState, useEffect } = React;
        
        // Lucide Icons 元件
        const Coffee = ({ className = "", ...props }) => (
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
                <path d="M17 8h1a4 4 0 1 1 0 8h-1"></path>
                <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"></path>
                <line x1="6" y1="2" x2="6" y2="4"></line>
                <line x1="10" y1="2" x2="10" y2="4"></line>
                <line x1="14" y1="2" x2="14" y2="4"></line>
            </svg>
        );
        
        const Plus = ({ className = "", ...props }) => (
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
        );
        
        const X = ({ className = "", ...props }) => (
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        );
        
        const ExternalLink = ({ className = "", ...props }) => (
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                <polyline points="15 3 21 3 21 9"></polyline>
                <line x1="10" y1="14" x2="21" y2="3"></line>
            </svg>
        );
        
        const Calendar = ({ className = "", ...props }) => (
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
        );
        
        const MapPin = ({ className = "", ...props }) => (
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
            </svg>
        );
        
        const Package = ({ className = "", ...props }) => (
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
                <line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line>
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
            </svg>
        );

        function CoffeeDepositTracker() {
          const [deposits, setDeposits] = useState([]);
          const [showAddForm, setShowAddForm] = useState(false);
          const [formData, setFormData] = useState({
            item: '',
            quantity: 1,
            store: '',
            redeemMethod: '',
            expiryDate: ''
          });

          const storeOptions = ['7-11', '全家', '星巴克'];
          const redeemMethods = ['遠傳', 'Line禮物', '7-11', '全家', '星巴克'];

          useEffect(() => {
            loadDeposits();
          }, []);

          const loadDeposits = () => {
            try {
              const stored = localStorage.getItem('coffee-deposits');
              if (stored) {
                setDeposits(JSON.parse(stored));
              }
            } catch (error) {
              console.log('載入資料時發生錯誤:', error);
            }
          };

          const saveDeposits = (newDeposits) => {
            try {
              localStorage.setItem('coffee-deposits', JSON.stringify(newDeposits));
              setDeposits(newDeposits);
            } catch (error) {
              alert('儲存失敗，請稍後再試');
            }
          };

          const handleSubmit = () => {
            if (!formData.item || !formData.store || !formData.redeemMethod || !formData.expiryDate || formData.quantity < 1) {
              alert('請填寫所有欄位');
              return;
            }

            const newDeposit = {
              id: Date.now().toString(),
              ...formData,
              quantity: parseInt(formData.quantity),
              createdAt: new Date().toISOString()
            };

            const updatedDeposits = [...deposits, newDeposit];
            saveDeposits(updatedDeposits);
            setFormData({ item: '', quantity: 1, store: '', redeemMethod: '', expiryDate: '' });
            setShowAddForm(false);
          };

          const handleDelete = (id) => {
            const updatedDeposits = deposits.filter(d => d.id !== id);
            saveDeposits(updatedDeposits);
          };

          const handleRedeem = (id) => {
            const deposit = deposits.find(d => d.id === id);
            if (!deposit) return;

            if (deposit.quantity > 1) {
              const updatedDeposits = deposits.map(d => 
                d.id === id ? { ...d, quantity: d.quantity - 1 } : d
              );
              saveDeposits(updatedDeposits);
            } else {
              handleDelete(id);
            }
          };

          const isExpiringSoon = (expiryDate) => {
            const expiry = new Date(expiryDate);
            const today = new Date();
            const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
            return daysUntilExpiry <= 7 && daysUntilExpiry >= 0;
          };

          const isExpired = (expiryDate) => {
            return new Date(expiryDate) < new Date();
          };

          const formatDate = (dateString) => {
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit' });
          };

          const getRedeemLink = (redeemMethod) => {
            const links = {
              '遠傳': 'https://www.fetnet.net/content/cbu/tw/index.html',
              'Line禮物': 'https://gift.line.me/category/coffee',
              '7-11': 'https://www.7-11.com.tw/',
              '全家': 'https://www.family.com.tw/',
              '星巴克': 'https://www.starbucks.com.tw/'
            };
            return links[redeemMethod] || '#';
          };

          return (
            <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100 p-4">
              <div className="max-w-4xl mx-auto">
                <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    <div className="flex items-center gap-3">
                      <div className="bg-amber-600 p-3 rounded-xl">
                        <Coffee className="w-8 h-8 text-white" />
                      </div>
                      <div>
                        <h1 className="text-3xl font-bold text-gray-800">咖啡寄杯記錄</h1>
                        <p className="text-gray-600 mt-1">管理你的咖啡寄杯，不怕忘記兌換</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setShowAddForm(!showAddForm)}
                      className="bg-amber-600 hover:bg-amber-700 text-white px-6 py-3 rounded-xl flex items-center gap-2 transition-colors shadow-md"
                    >
                      <Plus className="w-5 h-5" />
                      新增寄杯
                    </button>
                  </div>
                </div>

                {showAddForm && (
                  <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
                    <h2 className="text-xl font-bold text-gray-800 mb-4">新增寄杯記錄</h2>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">咖啡品項</label>
                        <input
                          type="text"
                          value={formData.item}
                          onChange={(e) => setFormData({ ...formData, item: e.target.value })}
                          placeholder="例如：美式咖啡、拿鐵"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">數量（杯）</label>
                        <input
                          type="number"
                          min="1"
                          value={formData.quantity}
                          onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">商店名稱</label>
                        <select
                          value={formData.store}
                          onChange={(e) => setFormData({ ...formData, store: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                        >
                          <option value="">請選擇商店</option>
                          {storeOptions.map(store => (
                            <option key={store} value={store}>{store}</option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">兌換途徑</label>
                        <select
                          value={formData.redeemMethod}
                          onChange={(e) => setFormData({ ...formData, redeemMethod: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                        >
                          <option value="">請選擇兌換途徑</option>
                          {redeemMethods.map(method => (
                            <option key={method} value={method}>{method}</option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">到期日</label>
                        <input
                          type="date"
                          value={formData.expiryDate}
                          onChange={(e) => setFormData({ ...formData, expiryDate: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                        />
                      </div>

                      <div className="flex gap-3 pt-2">
                        <button
                          onClick={handleSubmit}
                          className="flex-1 bg-amber-600 hover:bg-amber-700 text-white py-2 rounded-lg transition-colors font-medium"
                        >
                          儲存
                        </button>
                        <button
                          onClick={() => setShowAddForm(false)}
                          className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 py-2 rounded-lg transition-colors font-medium"
                        >
                          取消
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                <div className="space-y-4">
                  {deposits.length === 0 ? (
                    <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
                      <Coffee className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-500 text-lg">還沒有寄杯記錄</p>
                      <p className="text-gray-400 mt-2">點擊「新增寄杯」開始記錄吧！</p>
                    </div>
                  ) : (
                    deposits
                      .sort((a, b) => new Date(a.expiryDate) - new Date(b.expiryDate))
                      .map((deposit) => (
                        <div
                          key={deposit.id}
                          className={`bg-white rounded-2xl shadow-lg p-6 transition-all hover:shadow-xl ${
                            isExpired(deposit.expiryDate)
                              ? 'border-2 border-red-300 bg-red-50'
                              : isExpiringSoon(deposit.expiryDate)
                              ? 'border-2 border-yellow-300 bg-yellow-50'
                              : ''
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-3 flex-wrap">
                                <h3 className="text-xl font-bold text-gray-800">{deposit.item}</h3>
                                <span className="bg-amber-100 text-amber-800 px-3 py-1 rounded-full text-sm font-medium">
                                  {deposit.quantity} 杯
                                </span>
                              </div>

                              <div className="space-y-2">
                                <div className="flex items-center gap-2 text-gray-600">
                                  <MapPin className="w-4 h-4" />
                                  <span>{deposit.store}</span>
                                </div>
                                <div className="flex items-center gap-2 text-gray-600">
                                  <Package className="w-4 h-4" />
                                  <span>兌換途徑：{deposit.redeemMethod}</span>
                                </div>
                                <div className="flex items-center gap-2 text-gray-600 flex-wrap">
                                  <Calendar className="w-4 h-4" />
                                  <span>到期日：{formatDate(deposit.expiryDate)}</span>
                                  {isExpired(deposit.expiryDate) && (
                                    <span className="text-red-600 font-medium">（已過期）</span>
                                  )}
                                  {isExpiringSoon(deposit.expiryDate) && !isExpired(deposit.expiryDate) && (
                                    <span className="text-yellow-600 font-medium">（即將到期）</span>
                                  )}
                                </div>
                              </div>

                              <div className="flex gap-2 mt-4 flex-wrap">
                                <button
                                  onClick={() => handleRedeem(deposit.id)}
                                  className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors text-sm font-medium"
                                >
                                  <Coffee className="w-4 h-4" />
                                  兌換一杯
                                </button>
                                <a
                                  href={getRedeemLink(deposit.redeemMethod)}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors text-sm font-medium"
                                >
                                  <ExternalLink className="w-4 h-4" />
                                  前往兌換頁面
                                </a>
                                <a
                                  href={`https://www.google.com/maps/search/${encodeURIComponent(deposit.store)}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors text-sm font-medium"
                                >
                                  <MapPin className="w-4 h-4" />
                                  查看商店位置
                                </a>
                              </div>
                            </div>

                            <button
                              onClick={() => handleDelete(deposit.id)}
                              className="text-gray-400 hover:text-red-600 transition-colors p-2 ml-2"
                            >
                              <X className="w-5 h-5" />
                            </button>
                          </div>
                        </div>
                      ))
                  )}
                </div>

                {deposits.length > 0 && (
                  <div className="bg-white rounded-2xl shadow-lg p-6 mt-6">
                    <h3 className="text-lg font-bold text-gray-800 mb-3">統計資訊</h3>
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <p className="text-3xl font-bold text-amber-600">
                          {deposits.reduce((sum, d) => sum + d.quantity, 0)}
                        </p>
                        <p className="text-gray-600 text-sm mt-1">總杯數</p>
                      </div>
                      <div>
                        <p className="text-3xl font-bold text-green-600">
                          {deposits.filter(d => !isExpired(d.expiryDate)).length}
                        </p>
                        <p className="text-gray-600 text-sm mt-1">有效記錄</p>
                      </div>
                      <div>
                        <p className="text-3xl font-bold text-red-600">
                          {deposits.filter(d => isExpired(d.expiryDate)).length}
                        </p>
                        <p className="text-gray-600 text-sm mt-1">已過期</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        }

        // 確保 DOM 已載入
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', function() {
            const root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(<CoffeeDepositTracker />);
          });
        } else {
          const root = ReactDOM.createRoot(document.getElementById('root'));
          root.render(<CoffeeDepositTracker />);
        }
    </script>
</body>
</html>
"""

demo = gr.Interface(
    fn=lambda: html_content,
    inputs=None,
    outputs=gr.HTML(label="咖啡寄杯追蹤器"),
    title="☕ 咖啡寄杯追蹤器",
    description="管理你的咖啡寄杯，不怕忘記兌換！"
)

if __name__ == "__main__":
    demo.launch()
