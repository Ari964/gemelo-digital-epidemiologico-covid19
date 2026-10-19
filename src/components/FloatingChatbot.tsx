import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, MessageSquare, X, Send, Bot, User, AlertCircle, RefreshCw } from 'lucide-react';
import { ApiClient } from '../services/apiClient';

interface FloatingChatbotProps {
  darkMode: boolean;
  simulationContext?: any;
}

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
}

export const FloatingChatbot: React.FC<FloatingChatbotProps> = ({
  darkMode,
  simulationContext,
}) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: '¡Hola! Soy el Copiloto Epidemiológico con IA para el Gemelo Digital de Kenia (47 condados). ¿En qué puedo orientarte sobre las proyecciones, NPIs o camas UCI?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputValue, setInputValue] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      chatEndRef.current?.scrollIntoView?.({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userText = inputValue.trim();
    const userMsg: Message = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);
    setErrorMsg(null);

    try {
      const resp = await ApiClient.chatAi(userText, simulationContext);
      const assistantMsg: Message = {
        id: `ai-${Date.now()}`,
        sender: 'assistant',
        text: resp.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setErrorMsg(err.message || 'Error al comunicarse con el servicio de IA.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div id="floating_chatbot_root" className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* Ventana de Chat Flotante */}
      {isOpen && (
        <div
          id="floating_chat_window"
          className={`mb-4 w-96 max-w-[calc(100vw-2rem)] h-[520px] rounded-3xl shadow-2xl flex flex-col overflow-hidden border transition-all animate-in fade-in slide-in-from-bottom-5 duration-200 ${
            darkMode
              ? 'bg-slate-950/95 border-slate-800 text-slate-100'
              : 'bg-white/95 border-slate-200 text-slate-900'
          } backdrop-blur-xl`}
        >
          {/* Header */}
          <div className="p-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 text-white flex items-center justify-between shadow-md">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-2xl bg-white/20 flex items-center justify-center backdrop-blur-sm">
                <Sparkles size={18} className="text-amber-300 animate-pulse" />
              </div>
              <div>
                <h4 className="text-sm font-bold tracking-tight">AI Epidemiologist Copilot</h4>
                <p className="text-[10px] text-blue-100 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping inline-block" />
                  Ollama (qwen2.5:0.5b) • 47 Condados
                </p>
              </div>
            </div>
            <button
              id="btn_close_floating_chat"
              onClick={() => setIsOpen(false)}
              className="p-1.5 rounded-full hover:bg-white/20 text-white/80 hover:text-white transition cursor-pointer"
              title="Cerrar ventana de asistente"
            >
              <X size={18} />
            </button>
          </div>

          {/* Historial de Mensajes */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 text-xs">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.sender === 'assistant' && (
                  <div className="w-7 h-7 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center shrink-0 text-blue-400">
                    <Bot size={14} />
                  </div>
                )}
                <div
                  className={`max-w-[80%] p-3 rounded-2xl leading-relaxed ${
                    m.sender === 'user'
                      ? 'bg-blue-600 text-white rounded-br-none shadow-md'
                      : darkMode
                      ? 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none'
                      : 'bg-slate-100 border border-slate-200 text-slate-800 rounded-bl-none'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{m.text}</p>
                  <span
                    className={`text-[9px] block text-right mt-1 font-mono ${
                      m.sender === 'user' ? 'text-blue-200' : 'text-slate-400'
                    }`}
                  >
                    {m.timestamp}
                  </span>
                </div>
                {m.sender === 'user' && (
                  <div className="w-7 h-7 rounded-full bg-slate-700 flex items-center justify-center shrink-0 text-slate-300">
                    <User size={14} />
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-2 items-center text-slate-400 text-xs pl-2">
                <RefreshCw size={14} className="animate-spin text-blue-400" />
                <span>Analizando contexto epidemiológico...</span>
              </div>
            )}

            {errorMsg && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 flex items-start gap-2 text-xs">
                <AlertCircle size={16} className="shrink-0 mt-0.5" />
                <span>{errorMsg}</span>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Formulario de Entrada */}
          <form
            onSubmit={handleSendMessage}
            className={`p-3 border-t flex items-center gap-2 ${
              darkMode ? 'border-slate-800/80 bg-slate-900/60' : 'border-slate-200 bg-slate-50'
            }`}
          >
            <input
              id="input_floating_chat_message"
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Pregunta sobre la simulación o Kenia..."
              disabled={isLoading}
              className={`flex-1 px-3.5 py-2 rounded-xl text-xs outline-none transition ${
                darkMode
                  ? 'bg-slate-800/80 border border-slate-700 text-slate-100 placeholder-slate-500 focus:border-blue-500'
                  : 'bg-white border border-slate-300 text-slate-900 placeholder-slate-400 focus:border-blue-500'
              }`}
            />
            <button
              id="btn_submit_floating_chat"
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="p-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:opacity-90 transition disabled:opacity-40 cursor-pointer shadow-md"
              title="Enviar mensaje"
            >
              <Send size={15} />
            </button>
          </form>
        </div>
      )}

      {/* Botón Flotante Permanente */}
      <button
        id="btn_floating_chatbot_trigger"
        onClick={() => setIsOpen((prev) => !prev)}
        className="w-14 h-14 rounded-full bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-500 text-white flex items-center justify-center shadow-xl shadow-blue-500/30 hover:scale-105 active:scale-95 transition-all duration-200 border-2 border-white/20 cursor-pointer group"
        title="Copiloto Epidemiológico IA (Único Punto de Acceso)"
      >
        {isOpen ? (
          <X size={24} className="group-hover:rotate-90 transition-transform duration-200" />
        ) : (
          <div className="relative">
            <MessageSquare size={24} />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500" />
            </span>
          </div>
        )}
      </button>
    </div>
  );
};
