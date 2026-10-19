import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface SyntheticDataBannerProps {
  isSynthetic: boolean;
  className?: string;
}

export const SyntheticDataBanner: React.FC<SyntheticDataBannerProps> = ({ isSynthetic, className = '' }) => {
  if (!isSynthetic) return null;

  return (
    <div
      id="banner_synthetic_data_warning"
      className={`w-full p-4 rounded-2xl bg-amber-500/15 border-2 border-amber-500/60 text-amber-300 flex items-center justify-between shadow-lg shadow-amber-500/10 mb-6 animate-pulse ${className}`}
    >
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center shrink-0 text-amber-400">
          <AlertTriangle size={22} />
        </div>
        <div>
          <h4 className="text-sm font-black tracking-wide uppercase text-amber-200">
            DATOS SINTÉTICOS – NO VÁLIDOS PARA CONCLUSIONES CIENTÍFICAS
          </h4>
          <p className="text-xs text-amber-300/80 mt-0.5">
            Esta simulación utiliza matrices de movilidad gravitacionales artificiales. La validación formal de la Hipótesis H1 y la Aprobación Técnica están estrictamente bloqueadas.
          </p>
        </div>
      </div>
      <span className="text-[10px] font-mono px-2.5 py-1 rounded-full bg-amber-500/30 text-amber-200 font-bold uppercase tracking-wider shrink-0 border border-amber-400/40">
        Modo Sintético
      </span>
    </div>
  );
};
