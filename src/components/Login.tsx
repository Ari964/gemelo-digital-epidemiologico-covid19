import React, { useState } from 'react';
import { 
  Activity, 
  Shield, 
  Lock, 
  Eye, 
  EyeOff, 
  LogIn, 
  User as UserIcon, 
  KeyRound, 
  WifiOff, 
  AlertTriangle, 
  Database, 
  ShieldAlert,
  Globe
} from 'lucide-react';
import { ApiClient } from '../services/apiClient';
import { LanguageCode } from '../types';

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'epidemiologist' | 'analyst';
}

interface LoginProps {
  onLogin: (token: string, user: AuthUser) => void;
  darkMode: boolean;
  currentLang?: LanguageCode;
  onLanguageChange?: (lang: LanguageCode) => void;
}

const LOGIN_I18N: Record<LanguageCode, {
  title: string;
  subtitle: string;
  emailLabel: string;
  emailPlaceholder: string;
  passwordLabel: string;
  loginBtn: string;
  loggingIn: string;
  demoTitle: string;
  demoAdmin: string;
  demoEpi: string;
  demoAnalyst: string;
  badgeDisconnected: string;
  badgeCredentials: string;
  badgeDatabase: string;
  badgeServer: string;
  badgeGeneric: string;
}> = {
  es: {
    title: "Population Digital Twin",
    subtitle: "Preparación Pandémica · Kenia 47 Condados (FastAPI)",
    emailLabel: "Correo Electrónico",
    emailPlaceholder: "usuario@epidemic-twin.ke",
    passwordLabel: "Contraseña de Acceso",
    loginBtn: "Iniciar Sesión",
    loggingIn: "Conectando con Backend...",
    demoTitle: "Cuentas de demostración oficiales (clic para autocompletar)",
    demoAdmin: "Administrador del Sistema (Admin)",
    demoEpi: "Epidemióloga Jefe (Dra. Wanjiku)",
    demoAnalyst: "Analista de Vigilancia MOH (Omondi)",
    badgeDisconnected: "FALLO DE CONEXIÓN: BACKEND DESCONECTADO",
    badgeCredentials: "ERROR DE ACCESO: CREDENCIALES INCORRECTAS",
    badgeDatabase: "ERROR DE PERSISTENCIA: PROBLEMA DE BASE DE DATOS",
    badgeServer: "ERROR INTERNO: FALLO EN SERVIDOR FASTAPI (HTTP 500)",
    badgeGeneric: "ERROR DE AUTENTICACIÓN"
  },
  en: {
    title: "Population Digital Twin",
    subtitle: "Pandemic Preparedness · Kenya 47 Counties (FastAPI)",
    emailLabel: "Email Address",
    emailPlaceholder: "user@epidemic-twin.ke",
    passwordLabel: "Access Password",
    loginBtn: "Sign In",
    loggingIn: "Connecting to Backend...",
    demoTitle: "Official Demonstration Accounts (Click to auto-fill)",
    demoAdmin: "System Administrator (Admin)",
    demoEpi: "Chief Epidemiologist (Dr. Wanjiku)",
    demoAnalyst: "MOH Surveillance Analyst (Omondi)",
    badgeDisconnected: "CONNECTION FAILURE: BACKEND DISCONNECTED",
    badgeCredentials: "ACCESS ERROR: INVALID CREDENTIALS",
    badgeDatabase: "PERSISTENCE ERROR: DATABASE ISSUE",
    badgeServer: "INTERNAL ERROR: FASTAPI SERVER FAILURE (HTTP 500)",
    badgeGeneric: "AUTHENTICATION ERROR"
  },
  sw: {
    title: "Population Digital Twin",
    subtitle: "Kujitayarisha kwa Janga · Kaunti 47 za Kenya (FastAPI)",
    emailLabel: "Barua Pepe",
    emailPlaceholder: "mwanachama@epidemic-twin.ke",
    passwordLabel: "Nenosiri la Kuingia",
    loginBtn: "Ingia kwenye Mfumo",
    loggingIn: "Inaunganisha na Seva...",
    demoTitle: "Akaunti Rasmi za Maonyesho (Bofya kujaza kiotomatiki)",
    demoAdmin: "Msimamizi wa Mfumo (Admin)",
    demoEpi: "Mkuu wa Epidemiolojia (Dkt. Wanjiku)",
    demoAnalyst: "Mchambuzi wa MOH (Omondi)",
    badgeDisconnected: "HITILAFU YA MUUNGANISHO: SEVA HAIJAUNGANISHWA",
    badgeCredentials: "HITILAFU YA KUTAMBULISHA: VITAMBULISHO VISIVYO SAHIHI",
    badgeDatabase: "HITILAFU YA DATA: SHIDA YA POSTGRESQL",
    badgeServer: "HITILAFU YA NDANI: HITILAFU YA SEVA FASTAPI (HTTP 500)",
    badgeGeneric: "HITILAFU YA KUINGIA"
  }
};

const DEMO_ACCOUNTS = [
  { role: 'admin', email: 'admin@epidemic-twin.ke', password: 'AdminSecure2026!', labelKey: 'demoAdmin' as const },
  { role: 'epidemiologist', email: 'dr.wanjiku@health.go.ke', password: 'EpiChief2026!', labelKey: 'demoEpi' as const },
  { role: 'analyst', email: 'omondi@moh.go.ke', password: 'AnalystMOH2026!', labelKey: 'demoAnalyst' as const },
];

export const Login: React.FC<LoginProps> = ({ 
  onLogin, 
  darkMode,
  currentLang = 'es',
  onLanguageChange
}) => {
  const [selectedLang, setSelectedLang] = useState<LanguageCode>(currentLang);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [errorCategory, setErrorCategory] = useState<'disconnected' | 'credentials' | 'database' | 'server' | 'generic' | null>(null);
  const [loading, setLoading] = useState(false);

  const t = LOGIN_I18N[selectedLang] || LOGIN_I18N.es;

  const handleLangSelect = (code: LanguageCode) => {
    setSelectedLang(code);
    localStorage.setItem('gdti_lang', code);
    if (onLanguageChange) {
      onLanguageChange(code);
    }
  };

  const categorizeError = (msg: string) => {
    const lower = msg.toLowerCase();
    if (lower.includes('desconectado') || lower.includes('conexión') || lower.includes('failed to fetch') || lower.includes('network') || lower.includes('502') || lower.includes('503') || lower.includes('504')) {
      return 'disconnected';
    }
    if (lower.includes('credenciales') || lower.includes('contraseña') || lower.includes('invalid') || lower.includes('401') || lower.includes('autenticación')) {
      return 'credentials';
    }
    if (lower.includes('base de datos') || lower.includes('database') || lower.includes('postgres') || lower.includes('sql')) {
      return 'database';
    }
    if (lower.includes('servidor') || lower.includes('500') || lower.includes('internal server')) {
      return 'server';
    }
    return 'generic';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setErrorCategory(null);
    setLoading(true);
    try {
      const data = await ApiClient.login(email, password);
      const user: AuthUser = {
        id: data.user_id,
        name: data.name,
        email: data.email,
        role: data.role as any,
      };
      onLogin(data.access_token, user);
    } catch (err: any) {
      const errMsg = err.message || 'Error de autenticación.';
      setError(errMsg);
      setErrorCategory(categorizeError(errMsg));
      setLoading(false);
    }
  };

  const fillDemo = (acc: typeof DEMO_ACCOUNTS[number]) => {
    setEmail(acc.email);
    setPassword(acc.password);
    setError('');
    setErrorCategory(null);
  };

  return (
    <div className={`min-h-screen flex items-center justify-center p-4 transition-colors ${darkMode ? 'bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900'}`}>
      <div className={`w-full max-w-md rounded-3xl border shadow-2xl overflow-hidden transition-all ${darkMode ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200'}`}>
        
        {/* Top bar with Language Selector */}
        <div className={`px-6 py-2.5 flex items-center justify-between border-b text-xs ${darkMode ? 'bg-slate-900/90 border-slate-800 text-slate-400' : 'bg-slate-50 border-slate-200 text-slate-600'}`}>
          <div className="flex items-center gap-1.5 font-medium">
            <Globe size={14} className="text-blue-500" />
            <span className="text-[11px] uppercase tracking-wider font-bold">Language / Idioma:</span>
          </div>
          <div className="flex items-center gap-1">
            {(['es', 'en', 'sw'] as LanguageCode[]).map((lCode) => (
              <button
                key={lCode}
                type="button"
                onClick={() => handleLangSelect(lCode)}
                className={`px-2 py-0.5 rounded-md text-[11px] font-bold uppercase transition cursor-pointer ${
                  selectedLang === lCode
                    ? 'bg-blue-600 text-white shadow-sm'
                    : darkMode
                    ? 'hover:bg-slate-800 text-slate-400 hover:text-slate-200'
                    : 'hover:bg-slate-200 text-slate-600 hover:text-slate-900'
                }`}
              >
                {lCode}
              </button>
            ))}
          </div>
        </div>

        {/* Header */}
        <div className="p-7 pb-5 text-center bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-white/20 backdrop-blur flex items-center justify-center text-white shadow-lg mb-3">
            <Activity size={26} />
          </div>
          <h1 className="text-lg font-extrabold text-white tracking-tight">{t.title}</h1>
          <p className="text-[11px] text-blue-100 mt-0.5">{t.subtitle}</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-7 space-y-4">
          <div>
            <label className={`text-xs font-semibold block mb-1.5 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
              {t.emailLabel}
            </label>
            <div className="relative">
              <UserIcon size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t.emailPlaceholder}
                className={`w-full rounded-xl pl-9 pr-3 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none border transition ${darkMode ? 'bg-slate-950 border-slate-700 text-slate-200 focus:border-blue-500' : 'bg-white border-slate-300 text-slate-800 focus:border-blue-500'}`}
              />
            </div>
          </div>

          <div>
            <label className={`text-xs font-semibold block mb-1.5 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
              {t.passwordLabel}
            </label>
            <div className="relative">
              <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className={`w-full rounded-xl pl-9 pr-10 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none border transition ${darkMode ? 'bg-slate-950 border-slate-700 text-slate-200 focus:border-blue-500' : 'bg-white border-slate-300 text-slate-800 focus:border-blue-500'}`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-500 cursor-pointer"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* Error Banner Categorizado Rigurosamente */}
          {error && (
            <div className={`p-3 rounded-xl text-xs border space-y-1 ${
              errorCategory === 'disconnected'
                ? 'bg-amber-500/10 border-amber-500/40 text-amber-300'
                : errorCategory === 'credentials'
                ? 'bg-red-500/10 border-red-500/40 text-red-300'
                : errorCategory === 'database'
                ? 'bg-purple-500/10 border-purple-500/40 text-purple-300'
                : errorCategory === 'server'
                ? 'bg-rose-500/10 border-rose-500/40 text-rose-300'
                : 'bg-red-500/10 border-red-500/30 text-red-400'
            }`}>
              <div className="flex items-center gap-1.5 font-bold tracking-wider uppercase text-[10px]">
                {errorCategory === 'disconnected' && <WifiOff size={13} className="text-amber-400 shrink-0" />}
                {errorCategory === 'credentials' && <ShieldAlert size={13} className="text-red-400 shrink-0" />}
                {errorCategory === 'database' && <Database size={13} className="text-purple-400 shrink-0" />}
                {errorCategory === 'server' && <AlertTriangle size={13} className="text-rose-400 shrink-0" />}
                <span>
                  {errorCategory === 'disconnected' && t.badgeDisconnected}
                  {errorCategory === 'credentials' && t.badgeCredentials}
                  {errorCategory === 'database' && t.badgeDatabase}
                  {errorCategory === 'server' && t.badgeServer}
                  {errorCategory === 'generic' && t.badgeGeneric}
                </span>
              </div>
              <p className="text-[11px] leading-relaxed font-normal opacity-95">
                {error}
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-sm font-bold shadow-lg shadow-blue-500/25 transition disabled:opacity-50 cursor-pointer"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>{t.loggingIn}</span>
              </>
            ) : (
              <>
                <LogIn size={16} />
                <span>{t.loginBtn}</span>
              </>
            )}
          </button>

          {/* Demo Accounts */}
          <div className={`pt-3 border-t ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
            <div className="flex items-center gap-1.5 mb-2">
              <KeyRound size={14} className="text-blue-400" />
              <span className={`text-[10px] font-mono uppercase tracking-wider font-bold ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                {t.demoTitle}
              </span>
            </div>
            <div className="grid grid-cols-1 gap-2">
              {DEMO_ACCOUNTS.map((acc) => (
                <button
                  key={acc.role}
                  type="button"
                  onClick={() => fillDemo(acc)}
                  className={`flex items-center justify-between px-3 py-2 rounded-xl border text-[11px] font-medium text-left transition cursor-pointer ${darkMode ? 'bg-slate-950 border-slate-700 hover:border-blue-500 text-slate-300' : 'bg-slate-50 border-slate-200 hover:border-blue-400 text-slate-700'}`}
                >
                  <div className="flex items-center gap-2">
                    <Shield size={13} className="text-blue-400 shrink-0" />
                    <span className="font-semibold">{t[acc.labelKey]}</span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">{acc.email}</span>
                </button>
              ))}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
