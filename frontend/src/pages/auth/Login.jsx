import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTranslation } from 'react-i18next';

const Login = () => {
  const navigate = useNavigate();
  const { loginCustomer, loginStaff } = useAuth();
  const { t, i18n } = useTranslation();
  
  const [isStaff, setIsStaff] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = isStaff
      ? await loginStaff(username, password)
      : await loginCustomer(username, password);

    if (result.success) {
      navigate(isStaff ? '/dashboard' : '/customer');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'bg' : 'en';
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Language Switcher */}
        <div className="flex justify-end mb-4">
          <button
            onClick={toggleLanguage}
            className="btn btn-secondary text-sm"
          >
            {i18n.language === 'en' ? 'БГ' : 'EN'}
          </button>
        </div>

        <div className="card">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              AutoShop CRM
            </h1>
            <p className="text-gray-600">
              {isStaff ? t('staffLogin') : t('customerLogin')}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {isStaff ? t('username') : t('phone')}
              </label>
              <input
                type="text"
                className="input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder={isStaff ? t('username') : '+359 888 123 456'}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('password')}
              </label>
              <input
                type="password"
                className="input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="w-full btn btn-primary py-3"
              disabled={loading}
            >
              {loading ? t('loading') : t('login')}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => setIsStaff(!isStaff)}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              {isStaff
                ? t('customerLogin')
                : t('staffLogin')}
            </button>
          </div>
        </div>

        <div className="mt-8 text-center text-sm text-gray-600">
          <p>Demo Credentials:</p>
          <p>Customer: +359888100000 / customer0</p>
          <p>Staff: manager / manager123</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
