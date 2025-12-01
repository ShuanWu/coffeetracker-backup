import React, { useState, useEffect } from 'react';
import { Coffee, Plus, X, ExternalLink, Calendar, MapPin, Package } from 'lucide-react';

export default function CoffeeDepositTracker() {
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

  const loadDeposits = async () => {
    try {
      const keys = await window.storage.list('coffee:');
      if (keys && keys.keys) {
        const loadedDeposits = await Promise.all(
          keys.keys.map(async (key) => {
            try {
              const result = await window.storage.get(key);
              return result ? JSON.parse(result.value) : null;
            } catch {
              return null;
            }
          })
        );
        setDeposits(loadedDeposits.filter(d => d !== null));
      }
    } catch (error) {
      console.log('載入資料時發生錯誤:', error);
    }
  };

  const handleSubmit = async () => {
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

    try {
      await window.storage.set(`coffee:${newDeposit.id}`, JSON.stringify(newDeposit));
      setDeposits([...deposits, newDeposit]);
      setFormData({ item: '', quantity: 1, store: '', redeemMethod: '', expiryDate: '' });
      setShowAddForm(false);
    } catch (error) {
      alert('儲存失敗，請稍後再試');
    }
  };

  const handleDelete = async (id) => {
    try {
      await window.storage.delete(`coffee:${id}`);
      setDeposits(deposits.filter(d => d.id !== id));
    } catch (error) {
      alert('刪除失敗，請稍後再試');
    }
  };

  const handleRedeem = async (id) => {
    const deposit = deposits.find(d => d.id === id);
    if (!deposit) return;

    if (deposit.quantity > 1) {
      const updatedDeposit = {
        ...deposit,
        quantity: deposit.quantity - 1
      };
      try {
        await window.storage.set(`coffee:${id}`, JSON.stringify(updatedDeposit));
        setDeposits(deposits.map(d => d.id === id ? updatedDeposit : d));
      } catch (error) {
        alert('更新失敗，請稍後再試');
      }
    } else {
      await handleDelete(id);
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
          <div className="flex items-center justify-between">
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
                      <div className="flex items-center gap-3 mb-3">
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
                        <div className="flex items-center gap-2 text-gray-600">
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
                      className="text-gray-400 hover:text-red-600 transition-colors p-2"
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