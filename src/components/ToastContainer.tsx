import React, { createContext, useContext, useState, ReactNode } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from 'lucide-react';

export type ToastType = 'success' | 'warning' | 'error' | 'info';

export interface ToastMessage {
  id: string;
  type: ToastType;
  title: string;
  description?: string;
}

interface ToastContextType {
  addToast: (type: ToastType, title: string, description?: string) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export const ToastProvider: React.FC<{ children: ReactNode; darkMode?: boolean }> = ({ children, darkMode = true }) => {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = (type: ToastType, title: string, description?: string) => {
    const id = `toast_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
    const newToast: ToastMessage = { id, type, title, description };

    setToasts((prev) => [...prev, newToast]);

    setTimeout(() => {
      removeToast(id);
    }, 5000);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      {/* Toast Render Container */}
      <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2.5 max-w-sm w-full pointer-events-none">
        {toasts.map((toast) => {
          let bgClass = darkMode ? 'bg-slate-900 border-slate-700 text-slate-100' : 'bg-white border-slate-200 text-slate-800';
          let icon = <Info size={18} className="text-blue-400 shrink-0" />;

          if (toast.type === 'success') {
            bgClass = darkMode ? 'bg-slate-900/95 border-emerald-500/40 text-slate-100 shadow-emerald-950/20' : 'bg-white border-emerald-500/40 text-slate-800 shadow-emerald-500/10';
            icon = <CheckCircle2 size={18} className="text-emerald-400 shrink-0" />;
          } else if (toast.type === 'warning') {
            bgClass = darkMode ? 'bg-slate-900/95 border-amber-500/40 text-slate-100 shadow-amber-950/20' : 'bg-white border-amber-500/40 text-slate-800 shadow-amber-500/10';
            icon = <AlertTriangle size={18} className="text-amber-400 shrink-0" />;
          } else if (toast.type === 'error') {
            bgClass = darkMode ? 'bg-slate-900/95 border-rose-500/40 text-slate-100 shadow-rose-950/20' : 'bg-white border-rose-500/40 text-slate-800 shadow-rose-500/10';
            icon = <XCircle size={18} className="text-rose-400 shrink-0" />;
          }

          return (
            <div
              key={toast.id}
              className={`pointer-events-auto p-3.5 rounded-2xl border ${bgClass} shadow-xl backdrop-blur-md flex items-start gap-3 transition-all duration-300 animate-in slide-in-from-bottom-2`}
            >
              {icon}
              <div className="flex-1 min-w-0">
                <h5 className="text-xs font-bold leading-tight">{toast.title}</h5>
                {toast.description && (
                  <p className={`text-[11px] mt-0.5 leading-relaxed ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{toast.description}</p>
                )}
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                className={`transition p-0.5 ${darkMode ? 'text-slate-500 hover:text-slate-300' : 'text-slate-400 hover:text-slate-600'}`}
              >
                <X size={14} />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};
