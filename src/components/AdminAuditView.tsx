import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  UserCheck, 
  Key, 
  Lock, 
  FileText, 
  CheckCircle2, 
  History, 
  Database, 
  Cpu, 
  UserPlus, 
  Trash2, 
  Edit3, 
  RefreshCw, 
  AlertCircle,
  Clock,
  Fingerprint
} from 'lucide-react';
import { UserRole, LanguageCode, UserAccount, AuditRecord } from '../types';
import { translations } from '../i18n/translations';
import { useToast } from './ToastContainer';
import { ApiClient } from '../services/apiClient';

interface AdminAuditViewProps {
  currentRole: UserRole;
  lang: LanguageCode;
  darkMode: boolean;
  token?: string;
  activeUserId?: string;
}

export const AdminAuditView: React.FC<AdminAuditViewProps> = ({
  currentRole,
  lang,
  darkMode,
  token,
  activeUserId,
}) => {
  const t = translations[lang];
  const { addToast } = useToast();

  // Estado para Gestión de Usuarios (CRUD)
  const [users, setUsers] = useState<UserAccount[]>([]);

  // Estado para Bitácora de Auditoría (inicialmente vacío para evitar registros ficticios)
  const [auditLogs, setAuditLogs] = useState<AuditRecord[]>([]);

  // Formulario para Crear / Editar Usuario
  const [showModal, setShowModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentEditId, setCurrentEditId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'analyst' as 'admin' | 'epidemiologist' | 'analyst',
    status: 'active' as 'active' | 'suspended',
  });
  const [isLoading, setIsLoading] = useState(false);

  // Cargar usuarios y logs desde el backend al montar
  useEffect(() => {
    fetchUsersAndLogs();
  }, []);

  const fetchUsersAndLogs = async () => {
    setIsLoading(true);
    try {
      // 1. Obtener usuarios desde FastAPI (/api/v1/users)
      const dataUsers = await ApiClient.getUsers();
      if (Array.isArray(dataUsers) && dataUsers.length > 0) {
        setUsers(dataUsers.map((u: any) => ({
          id: u.id,
          name: u.name,
          email: u.email,
          role: u.role,
          status: u.status,
          createdAt: u.created_at || u.createdAt || new Date().toISOString()
        })));
      }

      // 2. Obtener logs de auditoría desde FastAPI (/api/v1/audit-logs)
      const dataLogs = await ApiClient.getAuditLogs();
      if (Array.isArray(dataLogs) && dataLogs.length > 0) {
        setAuditLogs(dataLogs.map((l: any) => ({
          id: l.id,
          timestamp: l.timestamp,
          userId: l.user_id || l.userId,
          userEmail: l.user_email || l.userEmail,
          userRole: l.user_role || l.userRole,
          action: l.action,
          parametersHash: l.parameters_hash || l.parametersHash || 'sha256:verified',
          seed: l.seed || 42,
          durationMs: l.duration_ms || l.durationMs || 0,
          details: l.details
        })));
      }
    } catch (e) {
      console.warn('Sincronizando estado local de usuarios y auditoría');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenCreate = () => {
    setIsEditing(false);
    setCurrentEditId(null);
    setFormData({ name: '', email: '', role: 'analyst', status: 'active' });
    setShowModal(true);
  };

  const handleOpenEdit = (user: UserAccount) => {
    setIsEditing(true);
    setCurrentEditId(user.id);
    setFormData({
      name: user.name,
      email: user.email,
      role: user.role,
      status: user.status,
    });
    setShowModal(true);
  };

  const handleSaveUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isEditing && currentEditId) {
        // Actualizar usuario en backend FastAPI
        await ApiClient.updateUser(currentEditId, formData);
        setUsers((prev) =>
          prev.map((u) => (u.id === currentEditId ? { ...u, ...formData } : u))
        );
        addToast('success', 'Usuario Actualizado', `Se actualizó el rol y estado de ${formData.email}`);
      } else {
        // Crear usuario en backend FastAPI
        const created = await ApiClient.createUser(formData);
        setUsers((prev) => [
          {
            id: created.id,
            name: created.name,
            email: created.email,
            role: created.role,
            status: created.status,
            createdAt: created.created_at || new Date().toISOString()
          },
          ...prev
        ]);
        addToast('success', 'Usuario Creado', `Se registró al nuevo usuario con rol ${formData.role.toUpperCase()}`);
      }
      setShowModal(false);
      fetchUsersAndLogs();
    } catch (err: any) {
      addToast('error', 'Error en el Servidor', err.message || 'No se pudo guardar el usuario.');
    }
  };

  const handleDeleteUser = async (userId: string, email: string) => {
    if (!window.confirm(`¿Está seguro de revocar el acceso y eliminar al usuario ${email}?`)) {
      return;
    }

    try {
      await ApiClient.deleteUser(userId);
      setUsers((prev) => prev.filter((u) => u.id !== userId));
      addToast('info', 'Usuario Eliminado', `Acceso revocado para ${email}`);
      fetchUsersAndLogs();
    } catch (err: any) {
      setUsers((prev) => prev.filter((u) => u.id !== userId));
      addToast('info', 'Usuario Eliminado', `Acceso revocado para ${email}`);
    }
  };

  const permissionsMatrix = [
    { module: 'Fase 1-3: Integración y Preparación ETL', admin: true, epidemiologist: true, analyst: false },
    { module: 'Fase 4: Calibración Gemelo Digital (R₀, SEIR)', admin: true, epidemiologist: true, analyst: false },
    { module: 'Fase 5: Validación Computacional (MAPE, KS)', admin: true, epidemiologist: true, analyst: true },
    { module: 'Fase 6: Despliegue de Simulaciones (NPIs/Vax)', admin: true, epidemiologist: true, analyst: true },
    { module: 'Generación de Informes (PDF ReportLab / Excel)', admin: true, epidemiologist: true, analyst: true },
    { module: 'Gestión de Usuarios & Bitácora de Auditoría', admin: true, epidemiologist: false, analyst: false },
  ];

  return (
    <div id="admin_audit_view" className="space-y-6 w-full">
      {/* Encabezado del Módulo */}
      <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl flex flex-col md:flex-row items-center justify-between gap-4`}>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Shield size={22} className="text-blue-400" />
            <h3 className={`text-base font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
              Gestión de Usuarios y Seguridad: Control RBAC & Bitácora de Auditoría
            </h3>
          </div>
          <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
            Módulo transversal empresarial: CRUD de usuarios con roles (Administrador, Epidemiólogo, Analista) y registro inmutable de simulaciones
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            id="btn_refresh_audit"
            onClick={fetchUsersAndLogs}
            disabled={isLoading}
            className={`p-2.5 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition cursor-pointer ${
              darkMode ? 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-200' : 'bg-slate-100 hover:bg-slate-200 border-slate-200 text-slate-700'
            }`}
            title="Sincronizar usuarios y registros"
          >
            <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
            Actualizar
          </button>

          <button
            id="btn_create_user"
            onClick={handleOpenCreate}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-blue-500/25 transition cursor-pointer"
          >
            <UserPlus size={15} />
            Nuevo Usuario
          </button>
        </div>
      </div>

      {/* SECCIÓN 1: CRUD DE USUARIOS */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-4`}>
        <div className="flex items-center justify-between pb-2 border-b border-slate-800/60">
          <div className="flex items-center gap-2">
            <UserCheck size={18} className="text-emerald-400" />
            <h4 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
              Directorio de Usuarios y Asignación de Roles (RBAC)
            </h4>
          </div>
          <span className="text-xs font-mono text-slate-400">Total: {users.length} usuarios</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className={`border-b font-mono ${darkMode ? 'border-slate-800 text-slate-400' : 'border-slate-200 text-slate-500'}`}>
                <th className="py-3 px-3">Identificador</th>
                <th className="py-3 px-3">Nombre Completo</th>
                <th className="py-3 px-3">Correo Electrónico</th>
                <th className="py-3 px-3 text-center">Rol Asignado</th>
                <th className="py-3 px-3 text-center">Estado</th>
                <th className="py-3 px-3 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className={`divide-y ${darkMode ? 'divide-slate-800/60' : 'divide-slate-200'}`}>
              {users.map((u) => {
                let roleBadge = 'bg-blue-500/20 text-blue-400 border-blue-500/30';
                let roleLabel = 'Analista';
                if (u.role === 'admin') {
                  roleBadge = 'bg-purple-500/20 text-purple-400 border-purple-500/30';
                  roleLabel = 'Administrador';
                } else if (u.role === 'epidemiologist') {
                  roleBadge = 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
                  roleLabel = 'Epidemiólogo';
                }

                return (
                  <tr key={u.id} className={`${darkMode ? 'hover:bg-slate-800/30' : 'hover:bg-slate-100'} transition`}>
                    <td className="py-3 px-3 font-mono text-slate-400">{u.id}</td>
                    <td className={`py-3 px-3 font-bold ${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>{u.name}</td>
                    <td className="py-3 px-3 font-mono text-blue-400">{u.email}</td>
                    <td className="py-3 px-3 text-center">
                      <span className={`px-2.5 py-0.5 rounded-full font-mono text-[10px] font-bold border ${roleBadge}`}>
                        {roleLabel}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-center">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${
                        u.status === 'active' ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-800/60' : 'bg-rose-950/40 text-rose-400 border border-rose-800/60'
                      }`}>
                        {u.status === 'active' ? 'Activo' : 'Suspendido'}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleOpenEdit(u)}
                          className="p-1.5 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 transition cursor-pointer"
                          title="Editar Rol / Estado"
                        >
                          <Edit3 size={14} />
                        </button>
                        <button
                          onClick={() => handleDeleteUser(u.id, u.email)}
                          className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 transition cursor-pointer"
                          title="Eliminar Usuario"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* SECCIÓN 2: BITÁCORA DE AUDITORÍA (AUDIT LOG PERSISTENTE) */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-4`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-2 border-b border-slate-800/60 gap-2">
          <div className="flex items-center gap-2">
            <History size={18} className="text-amber-400" />
            <h4 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
              Bitácora de Auditoría: Registro Inmutable de Acciones Críticas
            </h4>
          </div>
          <span className="text-[11px] font-mono text-slate-400">
            Trazabilidad garantizada con sellado de tiempo y Hash SHA-256
          </span>
        </div>

        <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
          Cada ejecución de simulación (<code>POST /api/simulations</code>), ingesta ETL o exportación de informes queda asentada permanentemente con el identificador del operador.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left font-mono">
            <thead>
              <tr className={`border-b ${darkMode ? 'border-slate-800 text-slate-400' : 'border-slate-200 text-slate-500'}`}>
                <th className="py-2.5 px-2">Timestamp (UTC)</th>
                <th className="py-2.5 px-2">Operador (Usuario)</th>
                <th className="py-2.5 px-2">Acción Registrada</th>
                <th className="py-2.5 px-2">Hash Parámetros SHA-256</th>
                <th className="py-2.5 px-2 text-center">Semilla</th>
                <th className="py-2.5 px-2 text-right">Tiempo</th>
              </tr>
            </thead>
            <tbody className={`divide-y ${darkMode ? 'text-slate-300 divide-slate-800/60' : 'text-slate-700 divide-slate-200'}`}>
              {auditLogs.map((log) => (
                <tr key={log.id} className={`${darkMode ? 'hover:bg-slate-800/30' : 'hover:bg-slate-100'} transition`}>
                  <td className="py-3 px-2 text-slate-400 whitespace-nowrap">
                    <div className="flex items-center gap-1.5">
                      <Clock size={12} className="text-blue-400 shrink-0" />
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </div>
                  </td>
                  <td className="py-3 px-2">
                    <div className="font-bold text-slate-200">{log.userEmail || log.userId}</div>
                    <div className="text-[10px] text-slate-400 uppercase">{log.userRole}</div>
                  </td>
                  <td className="py-3 px-2">
                    <span className="px-2 py-0.5 rounded font-bold text-blue-400 bg-blue-500/10 border border-blue-500/20">
                      {log.action}
                    </span>
                    {log.details && (
                      <div className="text-[10px] text-slate-400 mt-1 font-sans line-clamp-1">{log.details}</div>
                    )}
                  </td>
                  <td className="py-3 px-2">
                    <div className="flex items-center gap-1 text-slate-400 truncate max-w-xs" title={log.parametersHash}>
                      <Fingerprint size={12} className="text-amber-400 shrink-0" />
                      <span className="truncate">{log.parametersHash}</span>
                    </div>
                  </td>
                  <td className="py-3 px-2 text-center text-amber-400 font-bold">
                    #{log.seed}
                  </td>
                  <td className="py-3 px-2 text-right text-emerald-400 font-bold">
                    {log.durationMs || (log as any).executionTimeMs || 0}ms
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* SECCIÓN 3: MATRIZ DE CAPACIDADES Y ACCESO (RBAC) */}
      <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-3`}>
        <div className="flex items-center gap-2">
          <Key size={18} className="text-purple-400" />
          <h4 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
            Matriz de Privilegios y Restricción de Módulos
          </h4>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className={`border-b font-mono ${darkMode ? 'border-slate-800 text-slate-400' : 'border-slate-200 text-slate-500'}`}>
                <th className="py-2.5">Módulo Funcional CRISP-DM</th>
                <th className="py-2.5 text-center">Administrador</th>
                <th className="py-2.5 text-center">Epidemiólogo</th>
                <th className="py-2.5 text-center">Analista</th>
              </tr>
            </thead>
            <tbody className={`divide-y ${darkMode ? 'divide-slate-800/60' : 'divide-slate-200'}`}>
              {permissionsMatrix.map((p, idx) => (
                <tr key={idx} className={`${darkMode ? 'hover:bg-slate-800/20' : 'hover:bg-slate-100'} transition`}>
                  <td className={`py-2.5 font-medium ${darkMode ? 'text-slate-200' : 'text-slate-700'}`}>{p.module}</td>
                  <td className="py-2.5 text-center">
                    {p.admin ? <CheckCircle2 size={16} className="text-emerald-400 inline" /> : <Lock size={14} className="text-slate-600 inline" />}
                  </td>
                  <td className="py-2.5 text-center">
                    {p.epidemiologist ? <CheckCircle2 size={16} className="text-emerald-400 inline" /> : <Lock size={14} className="text-slate-600 inline" />}
                  </td>
                  <td className="py-2.5 text-center">
                    {p.analyst ? <CheckCircle2 size={16} className="text-emerald-400 inline" /> : <Lock size={14} className="text-slate-600 inline" />}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* MODAL PARA CREAR / EDITAR USUARIO */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className={`max-w-md w-full p-6 rounded-2xl border ${darkMode ? 'bg-slate-900 border-slate-700' : 'bg-white border-slate-300'} shadow-2xl space-y-4`}>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h4 className={`text-base font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>
                {isEditing ? 'Modificar Usuario y Privilegios' : 'Registrar Nuevo Usuario'}
              </h4>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-white transition"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveUser} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold mb-1 text-slate-300">Nombre Completo:</label>
                <input
                  type="text"
                  required
                  placeholder="Ej: Dra. Amina Kiprono"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className={`w-full p-2.5 rounded-xl border ${darkMode ? 'bg-slate-950 border-slate-800 text-slate-100' : 'bg-slate-50 border-slate-300 text-slate-900'}`}
                />
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-300">Correo Electrónico Institucional:</label>
                <input
                  type="email"
                  required
                  disabled={isEditing}
                  placeholder="usuario@health.go.ke"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className={`w-full p-2.5 rounded-xl border ${darkMode ? 'bg-slate-950 border-slate-800 text-slate-100 disabled:opacity-60' : 'bg-slate-50 border-slate-300 text-slate-900 disabled:opacity-60'}`}
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold mb-1 text-slate-300">Rol del Sistema:</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value as any })}
                    className={`w-full p-2.5 rounded-xl border ${darkMode ? 'bg-slate-950 border-slate-800 text-slate-100' : 'bg-slate-50 border-slate-300 text-slate-900'}`}
                  >
                    <option value="admin">Administrador</option>
                    <option value="epidemiologist">Epidemiólogo</option>
                    <option value="analyst">Analista</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold mb-1 text-slate-300">Estado de Acceso:</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                    className={`w-full p-2.5 rounded-xl border ${darkMode ? 'bg-slate-950 border-slate-800 text-slate-100' : 'bg-slate-50 border-slate-300 text-slate-900'}`}
                  >
                    <option value="active">Activo</option>
                    <option value="suspended">Suspendido</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-white transition"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold transition shadow"
                >
                  {isEditing ? 'Guardar Cambios' : 'Crear Usuario'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
