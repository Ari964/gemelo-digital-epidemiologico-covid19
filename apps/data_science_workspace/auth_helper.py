import os
import requests
import streamlit as st
from typing import Optional, Dict, Any, Tuple

def get_api_base_url() -> str:
    """Obtiene la URL base del backend garantizando coherencia local y en Docker."""
    url = os.getenv("API_BASE_URL") or os.getenv("API_URL") or "http://127.0.0.1:8000/api/v1"
    return url.rstrip("/")

def render_auth_sidebar() -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Renderiza el panel de autenticación JWT RBAC en el sidebar de Streamlit.
    Almacena el token y los datos de usuario en st.session_state.
    """
    api_url = get_api_base_url()
    st.sidebar.markdown("### 🔐 Autenticación RBAC")
    st.sidebar.caption(f"Backend: `{api_url}`")

    if "token" not in st.session_state:
        st.session_state["token"] = None
    if "user" not in st.session_state:
        st.session_state["user"] = None

    token = st.session_state["token"]
    user = st.session_state["user"]

    is_dev_env = os.getenv("ENVIRONMENT", "").lower() in ["development", "dev", "local"]

    if token and user:
        st.sidebar.success(f"Conectado como:\n**{user.get('name', 'Usuario')}**")
        st.sidebar.markdown(f"- **Rol**: `{user.get('role', 'N/A')}`\n- **Email**: `{user.get('email', 'N/A')}`")
        if st.sidebar.button("Cerrar Sesión", key="btn_logout"):
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.sidebar.info("Sesión cerrada exitosamente.")
            st.rerun()
        return token, user

    if st.session_state.get("session_expired"):
        st.sidebar.warning("⚠️ Su sesión ha expirado (401). Inicie sesión nuevamente.")
        st.session_state["session_expired"] = False

    st.sidebar.info("Inicie sesión con credenciales reales para operar.")

    # Restringir las ayudas con credenciales demostrativas al modo de desarrollo explícito
    if is_dev_env:
        st.sidebar.caption("🔧 Modo Desarrollo: Credenciales Rápidas")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("Admin", key="btn_fill_admin"):
                st.session_state["login_email"] = "admin@epidemic-twin.ke"
                st.session_state["login_pwd"] = "AdminSecure2026!"
        with col2:
            if st.button("Epidemiólogo", key="btn_fill_epi"):
                st.session_state["login_email"] = "dr.wanjiku@health.go.ke"
                st.session_state["login_pwd"] = "EpiChief2026!"

    default_email = st.session_state.get("login_email", "admin@epidemic-twin.ke" if is_dev_env else "")
    default_pwd = st.session_state.get("login_pwd", "AdminSecure2026!" if is_dev_env else "")

    with st.sidebar.form("login_form"):
        email = st.text_input("Correo Institucional:", value=default_email)
        pwd = st.text_input("Contraseña:", value=default_pwd, type="password")
        submit = st.form_submit_button("Iniciar Sesión (JWT)")

        if submit:
            try:
                # Contrato FastAPI espera JSON {"email": ..., "password": ...}
                login_resp = requests.post(
                    f"{api_url}/auth/login",
                    json={"email": email.strip(), "password": pwd},
                    timeout=5
                )
                if login_resp.status_code == 200:
                    data = login_resp.json()
                    user_role = data.get("role")
                    user_email = data.get("email")
                    user_name = data.get("name")
                    if not user_role or not user_email:
                        st.sidebar.error("Error: la respuesta no incluye rol o identidad válida.")
                    else:
                        st.session_state["token"] = data["access_token"]
                        st.session_state["user"] = {
                            "name": user_name or user_email.split("@")[0].capitalize(),
                            "email": user_email,
                            "role": user_role
                        }
                        st.sidebar.success(f"Autenticado exitosamente como {user_role}.")
                        st.rerun()
                elif login_resp.status_code == 401:
                    st.sidebar.error("Credenciales inválidas (401 Unauthorized).")
                elif login_resp.status_code == 403:
                    st.sidebar.error("Acceso denegado: cuenta de usuario suspendida o inactiva (403).")
                else:
                    st.sidebar.error(f"Error {login_resp.status_code}: {login_resp.text}")
            except requests.exceptions.ConnectionError:
                st.sidebar.error(f"No se pudo conectar con el backend en {api_url}.")
            except Exception as e:
                st.sidebar.error(f"Fallo de autenticación: {e}")

    return None, None

def get_auth_headers() -> Dict[str, str]:
    """Retorna encabezados HTTP con Bearer token si el usuario está autenticado."""
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def api_call(method: str, endpoint: str, json_data: Any = None, params: Any = None, timeout: int = 10) -> requests.Response:
    """Realiza una llamada HTTP autenticada al backend con manejo de errores y expiración."""
    api_url = get_api_base_url()
    url = f"{api_url}{endpoint}" if endpoint.startswith("/") else f"{api_url}/{endpoint}"
    headers = get_auth_headers()

    try:
        if method.upper() == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        elif method.upper() == "POST":
            resp = requests.post(url, headers=headers, json=json_data, params=params, timeout=timeout)
        elif method.upper() == "PUT":
            resp = requests.put(url, headers=headers, json=json_data, params=params, timeout=timeout)
        elif method.upper() == "DELETE":
            resp = requests.delete(url, headers=headers, params=params, timeout=timeout)
        else:
            raise ValueError(f"Método HTTP no soportado: {method}")

        if resp.status_code == 401 and headers:
            # Token expiró o fue revocado
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.session_state["session_expired"] = True

        return resp
    except requests.exceptions.RequestException:
        raise
