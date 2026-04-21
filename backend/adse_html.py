"""
ADSE - Agente Director Secundaria de Educacion - Frontend HTML
Plataforma para directores de Escuela Secundaria en Mexico.
7 Obligaciones, 59 Tareas con herramientas integradas.
4 niveles de navegacion: Obligaciones > Tareas > Herramientas > Plantillas
"""

INDEX_HTML = r'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="ADSE">
<title>ADSE - Agente Director Secundaria de Educacion</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0a0a0f;--bg2:#12121a;--bg3:#1a1a2e;--bg4:#22223a;
  --text:#e8e8f0;--text2:#9999aa;
  --accent:#7c3aed;--accent2:#a855f7;
  --green:#10b981;--red:#ef4444;--orange:#f59e0b;--blue:#3b82f6;
  --radius:14px;--shadow:0 4px 24px rgba(0,0,0,.4);
}
body{font-family:'Nunito',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden}
.app{display:flex;height:100vh;width:100%}

/* Panel izquierdo */
.panel-left{
  width:320px;min-width:320px;background:var(--bg2);
  border-right:1px solid rgba(255,255,255,.06);
  display:flex;flex-direction:column;overflow-y:auto;
}
.panel-left-header{
  padding:20px;border-bottom:1px solid rgba(255,255,255,.06);text-align:center;
}
.logo-title{
  font-size:24px;font-weight:800;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  letter-spacing:2px;
}
.logo-subtitle{font-size:11px;color:var(--text2);margin-top:4px}
.panel-left-content{padding:12px;flex:1}
.left-info-card{
  background:var(--bg3);border-radius:var(--radius);padding:16px;margin-bottom:8px;
  border:1px solid rgba(255,255,255,.06);
}
.left-info-card h3{font-size:14px;color:var(--accent2);margin-bottom:6px}
.left-info-card p{font-size:12px;color:var(--text2);line-height:1.5}
.left-info-icon{font-size:32px;text-align:center;margin-bottom:8px}
.back-btn{
  display:flex;align-items:center;gap:8px;padding:10px 16px;margin-bottom:8px;
  background:var(--bg3);border:1px solid rgba(255,255,255,.1);border-radius:var(--radius);
  color:var(--accent2);font-size:13px;font-weight:600;cursor:pointer;transition:all .2s;
}
.back-btn:hover{background:var(--bg4);border-color:var(--accent)}
.nivel-badge{
  display:inline-block;padding:3px 10px;border-radius:20px;font-size:10px;
  font-weight:700;letter-spacing:1px;margin-bottom:8px;
}
.logout-btn{
  display:block;margin:8px auto;padding:8px 20px;background:var(--bg3);
  border:1px solid rgba(255,255,255,.1);border-radius:8px;
  color:var(--red);font-size:12px;font-weight:600;cursor:pointer;transition:all .2s;
}
.logout-btn:hover{background:var(--red);color:#fff}

/* Widget calendario escolar */
.cal-widget{background:var(--bg3);border-radius:var(--radius);padding:12px;margin-bottom:8px;border:1px solid rgba(255,255,255,.06)}
.cal-widget-title{font-size:11px;font-weight:700;color:var(--accent2);text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;display:flex;align-items:center;gap:5px}
.cal-fecha-hoy{font-size:18px;font-weight:800;color:var(--text);margin-bottom:2px}
.cal-semana{font-size:10px;color:var(--text2);margin-bottom:10px}
.cal-evento{display:flex;align-items:flex-start;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.04)}
.cal-evento:last-child{border-bottom:none;padding-bottom:0}
.cal-dias{min-width:32px;text-align:center;border-radius:6px;padding:3px 4px;font-size:11px;font-weight:800;line-height:1.2}
.cal-dias.hoy{background:var(--red);color:#fff}
.cal-dias.urgente{background:var(--red);color:#fff}
.cal-dias.pronto{background:var(--orange);color:#000}
.cal-dias.normal{background:var(--bg4);color:var(--accent2)}
.cal-dias.pasado{background:var(--bg4);color:var(--text2);opacity:.5}
.cal-evento-info{flex:1}
.cal-evento-nombre{font-size:11px;font-weight:600;color:var(--text);line-height:1.3}
.cal-evento-sub{font-size:10px;color:var(--text2)}

/* Panel derecho */
.panel-right{
  flex:1;display:flex;flex-direction:column;overflow-y:auto;background:var(--bg);
}
.panel-right-header{
  padding:20px 24px;border-bottom:1px solid rgba(255,255,255,.06);background:var(--bg2);
}
.panel-right-header h2{font-size:18px;font-weight:700}
.panel-right-header p{font-size:12px;color:var(--text2);margin-top:4px}
.panel-right-content{padding:16px 20px;flex:1}

/* Grid de tarjetas */
.grid-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.card{
  background:var(--bg2);border:1px solid rgba(255,255,255,.06);
  border-radius:var(--radius);padding:16px;cursor:pointer;
  transition:all .25s ease;position:relative;overflow:hidden;
}
.card:hover{
  border-color:var(--accent);transform:translateY(-2px);
  box-shadow:0 8px 32px rgba(124,58,237,.15);
}
.card-icon{font-size:28px;margin-bottom:8px}
.card-title{font-size:14px;font-weight:700;margin-bottom:4px}
.card-desc{font-size:11px;color:var(--text2);line-height:1.5}
.card-badge{
  position:absolute;top:12px;right:12px;
  padding:2px 8px;border-radius:10px;font-size:9px;font-weight:700;
  background:var(--accent);color:#fff;
}
.card-color-bar{position:absolute;top:0;left:0;right:0;height:3px}

/* Formulario interactivo (Nivel 4) */
.form-container{
  background:var(--bg2);border:1px solid rgba(255,255,255,.08);
  border-radius:var(--radius);padding:24px;margin-bottom:12px;
}
.form-container h3{font-size:16px;font-weight:700;color:var(--accent2);margin-bottom:16px}
.form-group{margin-bottom:14px}
.form-group label{display:block;font-size:12px;font-weight:600;color:var(--text);margin-bottom:4px}
.form-group input[type="text"],
.form-group input[type="number"],
.form-group input[type="date"],
.form-group input[type="email"],
.form-group textarea,
.form-group select{
  width:100%;padding:10px 12px;background:var(--bg);
  border:1px solid rgba(255,255,255,.1);border-radius:8px;
  color:var(--text);font-family:'Nunito',sans-serif;font-size:13px;outline:none;
  transition:border-color .2s;
}
.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus{border-color:var(--accent)}
.form-group textarea{min-height:80px;resize:vertical}
.form-group select{cursor:pointer}
.form-group select option{background:var(--bg2);color:var(--text)}
.form-check{
  display:flex;align-items:center;gap:8px;padding:6px 0;
}
.form-check input[type="checkbox"]{
  width:18px;height:18px;accent-color:var(--accent);cursor:pointer;
}
.form-check label{font-size:12px;color:var(--text);cursor:pointer}

/* Tabla editable */
.tabla-editable{
  width:100%;border-collapse:collapse;margin-top:6px;
  background:var(--bg);border-radius:8px;overflow:hidden;
}
.tabla-editable th{
  background:var(--bg3);padding:8px 6px;font-size:10px;font-weight:700;
  color:var(--accent2);text-align:left;border:1px solid rgba(255,255,255,.06);
}
.tabla-editable td{
  padding:2px;border:1px solid rgba(255,255,255,.06);
}
.tabla-editable td input{
  width:100%;padding:6px;background:transparent;border:none;
  color:var(--text);font-size:11px;font-family:'Nunito',sans-serif;outline:none;
}
.tabla-editable td input:focus{background:rgba(124,58,237,.1)}
.btn-add-row{
  margin-top:6px;padding:4px 12px;background:var(--bg3);border:1px solid rgba(255,255,255,.1);
  border-radius:6px;color:var(--accent2);font-size:11px;cursor:pointer;
}

/* Botones de accion */
.action-buttons{display:flex;gap:10px;margin-top:20px;flex-wrap:wrap}
.btn-action{
  display:inline-flex;align-items:center;gap:6px;
  padding:10px 20px;border:none;border-radius:8px;
  font-size:13px;font-weight:600;cursor:pointer;transition:all .2s;
  font-family:'Nunito',sans-serif;
}
.btn-guardar{background:var(--accent);color:#fff}
.btn-guardar:hover{background:var(--accent2)}
.btn-whatsapp{background:#25d366;color:#fff}
.btn-whatsapp:hover{background:#1ebe57}
.btn-correo{background:var(--blue);color:#fff}
.btn-correo:hover{background:#2563eb}

/* Chat flotante */
.chat-float{position:fixed;bottom:20px;right:20px;z-index:1000}
.chat-float-btn{
  width:56px;height:56px;border-radius:50%;background:var(--accent);border:none;
  color:#fff;font-size:24px;cursor:pointer;box-shadow:var(--shadow);transition:all .2s;
}
.chat-float-btn:hover{transform:scale(1.1);background:var(--accent2)}
.chat-panel{
  position:fixed;bottom:80px;right:20px;width:380px;max-height:500px;
  background:var(--bg2);border:1px solid rgba(255,255,255,.1);
  border-radius:var(--radius);box-shadow:var(--shadow);
  display:none;flex-direction:column;z-index:1001;overflow:hidden;
}
.chat-panel.open{display:flex}
.chat-header{
  padding:14px 16px;background:var(--bg3);border-bottom:1px solid rgba(255,255,255,.06);
  display:flex;justify-content:space-between;align-items:center;
}
.chat-header h3{font-size:14px;font-weight:700}
.chat-close{background:none;border:none;color:var(--text2);font-size:18px;cursor:pointer}
.chat-messages{flex:1;overflow-y:auto;padding:12px;max-height:340px}
.chat-msg{margin-bottom:10px;padding:10px 12px;border-radius:10px;font-size:12px;line-height:1.6;word-wrap:break-word}
.chat-msg.user{background:var(--accent);color:#fff;margin-left:40px}
.chat-msg.bot{background:var(--bg3);color:var(--text);margin-right:40px}
.chat-input-area{display:flex;gap:8px;padding:12px;border-top:1px solid rgba(255,255,255,.06)}
.chat-input{
  flex:1;background:var(--bg);border:1px solid rgba(255,255,255,.1);
  border-radius:8px;padding:10px;color:var(--text);font-size:12px;
  font-family:'Nunito',sans-serif;outline:none;
}
.chat-input:focus{border-color:var(--accent)}
.chat-send{
  padding:10px 16px;background:var(--accent);border:none;border-radius:8px;
  color:#fff;font-weight:700;cursor:pointer;font-size:12px;
}

/* Login */
.login-overlay{
  position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:2000;
  display:flex;align-items:center;justify-content:center;
}
.login-box{
  background:var(--bg2);border:1px solid rgba(255,255,255,.1);
  border-radius:var(--radius);padding:32px;width:360px;text-align:center;
}
.login-box h2{font-size:22px;font-weight:800;color:var(--accent2);margin-bottom:4px}
.login-box p{font-size:11px;color:var(--text2);margin-bottom:20px}
.login-input{
  width:100%;padding:12px;margin-bottom:10px;background:var(--bg);
  border:1px solid rgba(255,255,255,.1);border-radius:8px;color:var(--text);
  font-family:'Nunito',sans-serif;font-size:13px;outline:none;
}
.login-input:focus{border-color:var(--accent)}
.login-btn{
  width:100%;padding:12px;background:var(--accent);border:none;border-radius:8px;
  color:#fff;font-weight:700;font-size:14px;cursor:pointer;margin-top:6px;
}
.login-btn:hover{background:var(--accent2)}
.login-toggle{margin-top:12px;font-size:12px;color:var(--text2);cursor:pointer}
.login-toggle span{color:var(--accent2);font-weight:600}
.login-error{color:var(--red);font-size:11px;margin-top:8px;display:none}

/* Transiciones suaves */
.fade-in{animation:fadeIn .3s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}

/* Toast notificacion */
.toast{
  position:fixed;top:20px;right:20px;padding:12px 20px;border-radius:8px;
  font-size:13px;font-weight:600;z-index:3000;transition:all .3s;
  box-shadow:var(--shadow);
}
.toast.success{background:var(--green);color:#fff}
.toast.error{background:var(--red);color:#fff}

/* Directorio de Contactos Modal */
.contactos-overlay{
  position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:2500;
  display:none;align-items:center;justify-content:center;
}
.contactos-overlay.open{display:flex}
.contactos-modal{
  background:var(--bg2);border:1px solid rgba(255,255,255,.1);
  border-radius:var(--radius);width:520px;max-width:95vw;max-height:85vh;
  display:flex;flex-direction:column;overflow:hidden;
}
.contactos-header{
  padding:16px 20px;background:var(--bg3);border-bottom:1px solid rgba(255,255,255,.06);
  display:flex;justify-content:space-between;align-items:center;
}
.contactos-header h3{font-size:16px;font-weight:700}
.contactos-close{background:none;border:none;color:var(--text2);font-size:22px;cursor:pointer}
.contactos-close:hover{color:var(--red)}
.contactos-toolbar{
  padding:12px 20px;display:flex;flex-wrap:wrap;gap:8px;
  border-bottom:1px solid rgba(255,255,255,.06);
}
.contactos-search{
  flex:1;min-width:180px;padding:8px 12px;background:var(--bg);
  border:1px solid rgba(255,255,255,.1);border-radius:8px;
  color:var(--text);font-family:'Nunito',sans-serif;font-size:12px;outline:none;
}
.contactos-search:focus{border-color:var(--accent)}
.btn-import{
  display:inline-flex;align-items:center;gap:4px;
  padding:7px 12px;border:1px solid rgba(255,255,255,.1);border-radius:8px;
  background:var(--bg3);color:var(--text);font-size:11px;font-weight:600;
  cursor:pointer;transition:all .2s;font-family:'Nunito',sans-serif;
}
.btn-import:hover{background:var(--bg4);border-color:var(--accent)}
.contactos-list{
  flex:1;overflow-y:auto;padding:12px 20px;
}
.contacto-card{
  display:flex;align-items:center;gap:12px;padding:10px 12px;margin-bottom:6px;
  background:var(--bg3);border:1px solid rgba(255,255,255,.06);border-radius:10px;
  transition:all .2s;
}
.contacto-card:hover{border-color:var(--accent);background:var(--bg4)}
.contacto-avatar{
  width:38px;height:38px;border-radius:50%;background:var(--accent);
  display:flex;align-items:center;justify-content:center;
  font-size:16px;font-weight:700;color:#fff;flex-shrink:0;
}
.contacto-info{flex:1;min-width:0}
.contacto-nombre{font-size:13px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.contacto-detalle{font-size:11px;color:var(--text2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.contacto-cargo{font-size:10px;color:var(--accent2);margin-top:2px}
.contacto-delete{
  background:none;border:none;color:var(--text2);font-size:16px;cursor:pointer;
  padding:4px 8px;border-radius:6px;transition:all .2s;flex-shrink:0;
}
.contacto-delete:hover{color:var(--red);background:rgba(239,68,68,.15)}
.contactos-empty{text-align:center;padding:40px 20px;color:var(--text2);font-size:13px}
.contactos-empty span{font-size:40px;display:block;margin-bottom:12px}

/* Formulario agregar contacto */
.contacto-form{
  padding:16px 20px;border-top:1px solid rgba(255,255,255,.06);
  display:none;
}
.contacto-form.open{display:block}
.contacto-form-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px}
.contacto-form-grid input{
  padding:8px 10px;background:var(--bg);border:1px solid rgba(255,255,255,.1);
  border-radius:6px;color:var(--text);font-family:'Nunito',sans-serif;font-size:12px;outline:none;
}
.contacto-form-grid input:focus{border-color:var(--accent)}
.contacto-form-actions{display:flex;gap:8px;justify-content:flex-end}
.contacto-form-actions button{
  padding:7px 16px;border:none;border-radius:6px;font-size:12px;font-weight:600;
  cursor:pointer;font-family:'Nunito',sans-serif;
}
.btn-contacto-save{background:var(--accent);color:#fff}
.btn-contacto-save:hover{background:var(--accent2)}
.btn-contacto-cancel{background:var(--bg3);color:var(--text2);border:1px solid rgba(255,255,255,.1) !important}

/* Boton contactos en panel izquierdo */
.btn-contactos{
  display:flex;align-items:center;gap:8px;width:100%;padding:10px 16px;margin-bottom:8px;
  background:var(--bg3);border:1px solid rgba(255,255,255,.1);border-radius:var(--radius);
  color:var(--accent2);font-size:13px;font-weight:600;cursor:pointer;transition:all .2s;
  font-family:'Nunito',sans-serif;
}
.btn-contactos:hover{background:var(--bg4);border-color:var(--accent)}

/* Contact Selector (mini overlay para WhatsApp/Correo) */
.contact-selector-overlay{
  position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:2600;
  display:none;align-items:center;justify-content:center;
}
.contact-selector-overlay.open{display:flex}
.contact-selector{
  background:var(--bg2);border:1px solid rgba(255,255,255,.1);
  border-radius:var(--radius);width:400px;max-width:95vw;max-height:70vh;
  display:flex;flex-direction:column;overflow:hidden;
}
.contact-selector-header{
  padding:14px 16px;background:var(--bg3);border-bottom:1px solid rgba(255,255,255,.06);
  display:flex;justify-content:space-between;align-items:center;
}
.contact-selector-header h3{font-size:14px;font-weight:700}
.contact-selector-list{flex:1;overflow-y:auto;padding:10px}
.contact-selector-item{
  display:flex;align-items:center;gap:10px;padding:10px;margin-bottom:4px;
  background:var(--bg3);border:1px solid rgba(255,255,255,.06);border-radius:8px;
  cursor:pointer;transition:all .2s;
}
.contact-selector-item:hover{border-color:var(--accent);background:var(--bg4)}
.contact-selector-general{
  display:block;text-align:center;padding:10px;margin:8px 10px;
  background:var(--bg3);border:1px solid rgba(255,255,255,.1);border-radius:8px;
  color:var(--accent2);font-size:12px;font-weight:600;cursor:pointer;transition:all .2s;
  text-decoration:none;
}
.contact-selector-general:hover{background:var(--bg4);border-color:var(--accent)}

/* Responsive */
@media(max-width:768px){
  .app{flex-direction:column}
  .panel-left{width:100%;min-width:100%;max-height:35vh}
  .grid-cards{grid-template-columns:1fr}
  .chat-panel{width:calc(100% - 20px);right:10px}
  .action-buttons{flex-direction:column}
  .btn-action{width:100%;justify-content:center}
  .contactos-modal{width:100%;max-width:100%;max-height:100vh;border-radius:0}
  .contacto-form-grid{grid-template-columns:1fr}
  .contact-selector{width:100%;max-width:100%;border-radius:0}
}
</style>
</head>
<body>

<!-- LOGIN -->
<div class="login-overlay" id="loginOverlay">
  <div class="login-box">
    <div style="font-size:40px;margin-bottom:8px">&#127891;</div>
    <h2>ADSE</h2>
    <p>Agente Director Secundaria de Educaci&oacute;n &#127474;&#127485;</p>
    <div id="loginForm">
      <input class="login-input" id="loginUser" placeholder="Usuario">
      <input class="login-input" id="loginPass" type="password" placeholder="Contrase&ntilde;a">
      <button class="login-btn" onclick="doLogin()">Entrar</button>
      <div class="login-toggle" onclick="toggleRegister()">&iquest;No tienes cuenta? <span>Crear cuenta</span></div>
    </div>
    <div id="registerForm" style="display:none">
      <input class="login-input" id="regUser" placeholder="Usuario">
      <input class="login-input" id="regName" placeholder="Nombre completo">
      <input class="login-input" id="regEmail" placeholder="Correo electr&oacute;nico" type="email">
      <input class="login-input" id="regPass" type="password" placeholder="Contrase&ntilde;a (m&iacute;n. 6 caracteres)">
      <button class="login-btn" onclick="doRegister()">Crear cuenta</button>
      <div class="login-toggle" onclick="toggleRegister()">&iquest;Ya tienes cuenta? <span>Iniciar sesi&oacute;n</span></div>
    </div>
    <div class="login-error" id="loginError"></div>
  </div>
</div>

<!-- APP PRINCIPAL -->
<div class="app" id="mainApp" style="display:none">
  <div class="panel-left">
    <div class="panel-left-header">
      <div class="logo-title">ADSE</div>
      <div class="logo-subtitle">Agente Director Secundaria de Educaci&oacute;n &#127474;&#127485;</div>
    </div>
    <div id="panelLeftContent" class="panel-left-content"></div>
  </div>
  <div class="panel-right">
    <div class="panel-right-header" id="panelRightHeader">
      <h2 id="rightTitle">7 Obligaciones del Director</h2>
      <p id="rightSubtitle">Selecciona una obligaci&oacute;n para ver sus tareas</p>
    </div>
    <div class="panel-right-content" id="panelRightContent"></div>
  </div>
</div>

<!-- CHAT FLOTANTE -->
<div class="chat-float" id="chatFloat" style="display:none">
  <button class="chat-float-btn" onclick="toggleChat()">&#128172;</button>
</div>
<div class="chat-panel" id="chatPanel">
  <div class="chat-header">
    <h3>&#128172; Chat ADSE</h3>
    <button class="chat-close" onclick="toggleChat()">&times;</button>
  </div>
  <div class="chat-messages" id="chatMessages">
    <div class="chat-msg bot">Hola! Soy el Agente ADSE. Preguntame sobre cualquier obligacion, tarea o herramienta.</div>
  </div>
  <div class="chat-input-area">
    <input class="chat-input" id="chatInput" placeholder="Escribe tu consulta..." onkeydown="if(event.key==='Enter')sendChat()">
    <button class="chat-send" onclick="sendChat()">Enviar</button>
  </div>
</div>

<!-- DIRECTORIO DE CONTACTOS MODAL -->
<div class="contactos-overlay" id="contactosOverlay">
  <div class="contactos-modal">
    <div class="contactos-header">
      <h3>&#128199; Mis Contactos</h3>
      <button class="contactos-close" onclick="cerrarContactos()">&times;</button>
    </div>
    <div class="contactos-toolbar">
      <input class="contactos-search" id="contactosSearch" placeholder="Buscar contacto..." oninput="filtrarContactos()">
      <button class="btn-import" id="btnImportPhone" style="display:none" onclick="importFromPhone()">&#128241; Tel&eacute;fono</button>
      <button class="btn-import" onclick="document.getElementById('fileImportInput').click()">&#128193; CSV/VCF</button>
      <button class="btn-import" onclick="toggleContactForm()">&#10133; Manual</button>
      <input type="file" id="fileImportInput" accept=".vcf,.csv" style="display:none" onchange="handleFileImport(this)">
    </div>
    <div class="contactos-list" id="contactosList"></div>
    <div class="contacto-form" id="contactoForm">
      <div class="contacto-form-grid">
        <input type="text" id="cfNombre" placeholder="Nombre completo">
        <input type="text" id="cfTelefono" placeholder="Tel&eacute;fono">
        <input type="email" id="cfCorreo" placeholder="Correo electr&oacute;nico">
        <input type="text" id="cfCargo" placeholder="Cargo / Rol">
      </div>
      <div class="contacto-form-actions">
        <button class="btn-contacto-cancel" onclick="toggleContactForm()">Cancelar</button>
        <button class="btn-contacto-save" onclick="guardarContactoManual()">Guardar contacto</button>
      </div>
    </div>
  </div>
</div>

<!-- SELECTOR DE CONTACTOS (para WhatsApp/Correo) -->
<div class="contact-selector-overlay" id="contactSelectorOverlay">
  <div class="contact-selector">
    <div class="contact-selector-header">
      <h3 id="contactSelectorTitle">Seleccionar contacto</h3>
      <button class="contactos-close" onclick="cerrarContactSelector()">&times;</button>
    </div>
    <div class="contact-selector-list" id="contactSelectorList"></div>
  </div>
</div>

<!-- Cargar datos de plantillas desde archivos separados -->
<script src="/static/datos_plantillas_1_3.js"></script>
<script src="/static/datos_plantillas_4_7.js"></script>

<script>
// ============================================================
// FUSIONAR PLANTILLAS
// ============================================================
if(typeof PLANTILLAS_DATA === 'undefined') var PLANTILLAS_DATA = {};
if(typeof PLANTILLAS_DATA_2 !== 'undefined'){
  for(var k in PLANTILLAS_DATA_2) PLANTILLAS_DATA[k] = PLANTILLAS_DATA_2[k];
}

// ============================================================
// DATOS DE OBLIGACIONES (7)
// ============================================================
// ============================================================
// CALENDARIO ESCOLAR 2025-2026
// ============================================================
var EVENTOS_CICLO = [
  {fecha:'2025-08-11', nombre:'TIFC Intensivo', sub:'5 días de trabajo colegiado', icono:'🎓'},
  {fecha:'2025-08-18', nombre:'Inicio de clases', sub:'1ro, 2do y 3ro de secundaria', icono:'🏫'},
  {fecha:'2025-09-01', nombre:'1a Sesión CTE', sub:'Ordinaria — productos y acuerdos', icono:'📋'},
  {fecha:'2025-09-15', nombre:'Acto cívico 15 de sept.', sub:'Organización y logística del plantel', icono:'🇲🇽'},
  {fecha:'2025-09-19', nombre:'Simulacro Nacional', sub:'Sismo — bitácora obligatoria', icono:'🚨'},
  {fecha:'2025-10-01', nombre:'2a Sesión CTE', sub:'Ordinaria — seguimiento PMC', icono:'📋'},
  {fecha:'2025-10-31', nombre:'Cierre 1er periodo evaluación', sub:'Captura de calificaciones', icono:'📊'},
  {fecha:'2025-11-03', nombre:'Entrega boletas 1er trim.', sub:'Reunión con padres de familia', icono:'📄'},
  {fecha:'2025-11-03', nombre:'3a Sesión CTE', sub:'Ordinaria — análisis de resultados', icono:'📋'},
  {fecha:'2025-11-21', nombre:'Simulacro 2', sub:'Incendio — bitácora obligatoria', icono:'🚨'},
  {fecha:'2025-12-01', nombre:'4a Sesión CTE', sub:'Ordinaria', icono:'📋'},
  {fecha:'2025-12-20', nombre:'Vacaciones invierno', sub:'Fin de clases — regreso 7 enero', icono:'❄️'},
  {fecha:'2026-01-07', nombre:'Regreso clases enero', sub:'2do periodo del ciclo', icono:'🏫'},
  {fecha:'2026-02-02', nombre:'6a Sesión CTE', sub:'Ordinaria', icono:'📋'},
  {fecha:'2026-02-28', nombre:'Cierre 2do periodo evaluación', sub:'Captura de calificaciones', icono:'📊'},
  {fecha:'2026-03-02', nombre:'Entrega boletas 2do trim.', sub:'Reunión con padres de familia', icono:'📄'},
  {fecha:'2026-03-16', nombre:'7a Sesión CTE', sub:'Ordinaria', icono:'📋'},
  {fecha:'2026-03-23', nombre:'Vacaciones Semana Santa', sub:'Regreso 7 abril', icono:'🌿'},
  {fecha:'2026-04-07', nombre:'Regreso clases abril', sub:'3er periodo del ciclo', icono:'🏫'},
  {fecha:'2026-04-20', nombre:'Simulacro 3', sub:'Evacuación general', icono:'🚨'},
  {fecha:'2026-05-04', nombre:'9a Sesión CTE', sub:'Ordinaria', icono:'📋'},
  {fecha:'2026-05-15', nombre:'Día del Maestro', sub:'Sin clases — acto de reconocimiento', icono:'🏅'},
  {fecha:'2026-06-01', nombre:'10a Sesión CTE', sub:'Ordinaria — evaluación del PMC', icono:'📋'},
  {fecha:'2026-06-26', nombre:'Cierre 3er periodo evaluación', sub:'Calificaciones finales', icono:'📊'},
  {fecha:'2026-06-30', nombre:'Fin de ciclo escolar', sub:'Acto de clausura 3er grado', icono:'🎓'},
  {fecha:'2026-07-06', nombre:'TIFC Cierre', sub:'5 días — evaluación del ciclo', icono:'🎓'},
  {fecha:'2026-07-10', nombre:'Simulacro 4', sub:'Riesgo externo — cierre de ciclo', icono:'🚨'}
];

function renderCalendarioWidget(){
  var hoy = new Date();
  hoy.setHours(0,0,0,0);
  var diasSemana = ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb'];
  var meses = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
  var mesesL = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];

  // calcular semana del ciclo
  var inicioCiclo = new Date('2025-08-18');
  var diffMs = hoy - inicioCiclo;
  var semana = diffMs > 0 ? Math.ceil(diffMs / (7*24*60*60*1000)) : 0;
  var semanaStr = semana > 0 && semana <= 46 ? 'Semana ' + semana + ' del ciclo' : 'Ciclo 2025-2026';

  var fechaHoyStr = diasSemana[hoy.getDay()] + ' ' + hoy.getDate() + ' ' + mesesL[hoy.getMonth()] + ' ' + hoy.getFullYear();

  // próximos eventos (máx 5, incluyendo pasados recientes ≤3 días)
  var eventos = EVENTOS_CICLO.map(function(e){
    var fe = new Date(e.fecha + 'T00:00:00');
    var diff = Math.round((fe - hoy) / (24*60*60*1000));
    return Object.assign({}, e, {diff: diff, fe: fe});
  }).filter(function(e){ return e.diff >= -3; })
    .sort(function(a,b){ return a.diff - b.diff; })
    .slice(0, 5);

  var html = '<div class="cal-widget">';
  html += '<div class="cal-widget-title">📅 Calendario escolar</div>';
  html += '<div class="cal-fecha-hoy">' + fechaHoyStr + '</div>';
  html += '<div class="cal-semana">' + semanaStr + '</div>';

  eventos.forEach(function(e){
    var cls, label;
    if(e.diff < 0){ cls='pasado'; label= (e.diff===-1?'Ayer':(Math.abs(e.diff)+'d')); }
    else if(e.diff === 0){ cls='hoy'; label='HOY'; }
    else if(e.diff <= 7){ cls='urgente'; label= e.diff+'d'; }
    else if(e.diff <= 21){ cls='pronto'; label= e.diff+'d'; }
    else{ cls='normal'; label= e.diff+'d'; }
    var fechaStr = e.fe.getDate() + ' ' + meses[e.fe.getMonth()];
    html += '<div class="cal-evento">';
    html += '<div class="cal-dias ' + cls + '">' + label + '</div>';
    html += '<div class="cal-evento-info">';
    html += '<div class="cal-evento-nombre">' + e.icono + ' ' + e.nombre + '</div>';
    html += '<div class="cal-evento-sub">' + fechaStr + ' — ' + e.sub + '</div>';
    html += '</div></div>';
  });
  html += '</div>';
  return html;
}

var OBLIGACIONES = [
  {id:'OBL1', nombre:'Gestion Academico-Pedagogica', icono:'\ud83d\udcda', color:'#4A148C',
   desc:'Programa Analitico, PMC, acompanamiento, evaluacion, materiales, inclusion',
   tareas:['O1A','O1B','O1C','O1D','O1E','O1F']},
  {id:'OBL2', nombre:'Consejo Tecnico Escolar (CTE)', icono:'\ud83c\udfeb', color:'#1565C0',
   desc:'Instalacion del CTE, Fase Intensiva, sesiones ordinarias, actas y evidencias',
   tareas:['O2A','O2B','O2C','O2D','O2E','O2F']},
  {id:'OBL3', nombre:'Control Escolar', icono:'\ud83d\udcdd', color:'#2E7D32',
   desc:'Inscripciones, boletas, certificacion, estadistica 911, SIIE Web, expedientes',
   tareas:['O3A','O3B','O3C','O3D','O3E','O3F','O3G','O3H','O3I','O3J']},
  {id:'OBL4', nombre:'Gestion Administrativa', icono:'\ud83c\udfe2', color:'#E65100',
   desc:'Inventario, archivo, correspondencia, personal, La Escuela es Nuestra',
   tareas:['O4A','O4B','O4C','O4D','O4E','O4F','O4G','O4H','O4I']},
  {id:'OBL5', nombre:'Participacion Social', icono:'\ud83e\udd1d', color:'#6A1B9A',
   desc:'CEAP, asambleas con padres, rendicion de cuentas, APF, contraloria social',
   tareas:['O5A','O5B','O5C','O5D','O5E','O5F']},
  {id:'OBL6', nombre:'Seguridad, Salud e Higiene', icono:'\ud83d\udee1\ufe0f', color:'#C62828',
   desc:'Proteccion civil, simulacros, botiquin, senalizacion, filtro de salud',
   tareas:['O6A','O6B','O6C','O6D','O6E','O6F','O6G','O6H','O6I','O6J','O6K']},
  {id:'OBL7', nombre:'Formacion Continua', icono:'\ud83c\udf93', color:'#00695C',
   desc:'TIFC, diagnostico de necesidades, plan de formacion, USICAMM, cursos',
   tareas:['O7A','O7B','O7C','O7D','O7E','O7F','O7G','O7H','O7I','O7J','O7K']}
];

// ============================================================
// DATOS DE TAREAS (59)
// ============================================================
var TAREAS = {
  'O1A':{nombre:'Programa Analitico (PA)',icono:'\ud83d\udccb',grupo:'OBL1',descripcion:'Codiseno del PA en CTE, lectura de la realidad, organizacion de contenidos por campo formativo, firmas del colectivo'},
  'O1B':{nombre:'Programa de Mejora Continua (PMC)',icono:'\ud83d\udcca',grupo:'OBL1',descripcion:'Diagnostico 8 ambitos, objetivos, metas, matriz de acciones, seguimiento, semaforo de avance'},
  'O1C':{nombre:'Acompanamiento Pedagogico',icono:'\ud83d\udc41\ufe0f',grupo:'OBL1',descripcion:'Visitas a aula, guia de 15 indicadores, retroalimentacion docente, bitacora, calendario de visitas'},
  'O1D':{nombre:'Evaluacion Formativa',icono:'\ud83d\udcdd',grupo:'OBL1',descripcion:'Informe de evaluacion con comentarios, concentrado grupal, calendario de periodos, boletas'},
  'O1E':{nombre:'Materiales y LTG',icono:'\ud83d\udcda',grupo:'OBL1',descripcion:'Acta de recepcion de libros, inventario, oficio de solicitud, checklist de uso, distribucion'},
  'O1F':{nombre:'Inclusion y NEE',icono:'\u267f',grupo:'OBL1',descripcion:'Reporte de deteccion, oficio USAER, registro de seguimiento, checklist de inclusion, BAP'},

  'O2A':{nombre:'Instalacion del CTE',icono:'\ud83c\udfeb',grupo:'OBL2',descripcion:'Acta constitutiva del CTE, convocatoria, condiciones logisticas, Acuerdo 05/04/24'},
  'O2B':{nombre:'Fase Intensiva CTE',icono:'\ud83d\udcc5',grupo:'OBL2',descripcion:'5 dias agosto, diagnostico socioeducativo, lectura de la realidad, PA, PMC, itinerario del CTE'},
  'O2C':{nombre:'Sesiones Ordinarias CTE',icono:'\ud83d\udcc6',grupo:'OBL2',descripcion:'8 sesiones mensuales, temas del itinerario, seguimiento PMC, acuerdos, productos'},
  'O2D':{nombre:'Comite de Planeacion y Evaluacion',icono:'\ud83d\udccb',grupo:'OBL2',descripcion:'Conformar comite, coordinar formulacion y evaluacion del PMC, sistematizar informacion'},
  'O2E':{nombre:'Seguimiento al PMC en CTE',icono:'\ud83d\udcc8',grupo:'OBL2',descripcion:'Revision de avances en cada sesion, ajustes, reorientacion de acciones'},
  'O2F':{nombre:'Actas y Evidencias CTE',icono:'\ud83d\udcc1',grupo:'OBL2',descripcion:'Actas de sesion, listas de asistencia, portafolio de evidencias, registro fotografico'},

  'O3A':{nombre:'Inscripciones',icono:'\ud83d\udcdd',grupo:'OBL3',descripcion:'Documentacion de nuevo ingreso, verificacion de edades, expedientes, captura en SIIE Web'},
  'O3B':{nombre:'Reinscripciones',icono:'\ud83d\udd04',grupo:'OBL3',descripcion:'Registro de alumnos que continuan, actualizacion de datos, cierre septiembre'},
  'O3C':{nombre:'Preinscripciones',icono:'\ud83d\udccb',grupo:'OBL3',descripcion:'Proceso enero-febrero para siguiente ciclo, difusion de convocatoria'},
  'O3D':{nombre:'Acreditacion y Promocion',icono:'\u2705',grupo:'OBL3',descripcion:'Acreditacion automatica en secundaria, evaluacion formativa, promocion de grado'},
  'O3E':{nombre:'Certificacion 3er Grado',icono:'\ud83c\udf93',grupo:'OBL3',descripcion:'Certificado de educacion secundaria, gestion ante control escolar, Acuerdo 12/10/17'},
  'O3F':{nombre:'Boletas de Evaluacion',icono:'\ud83d\udcc4',grupo:'OBL3',descripcion:'3 momentos de entrega, observaciones por campo formativo, entrega a padres'},
  'O3G':{nombre:'Estadistica 911',icono:'\ud83d\udcca',grupo:'OBL3',descripcion:'Formato 911.1, matricula por grado/genero, inicio y fin de cursos, plataforma f911.sep.gob.mx'},
  'O3H':{nombre:'SIIE Web',icono:'\ud83d\udcbb',grupo:'OBL3',descripcion:'Sistema Integral de Informacion Escolar, captura de datos, organizacion escolar, CCT'},
  'O3I':{nombre:'Altas, Bajas y Traslados',icono:'\ud83d\udd00',grupo:'OBL3',descripcion:'Gestion de movimientos de alumnos, constancias para traslado, registro en sistema'},
  'O3J':{nombre:'Expedientes de Alumnos',icono:'\ud83d\udcc2',grupo:'OBL3',descripcion:'Acta de nacimiento, CURP, cartilla de vacunacion, boletas, documentacion completa'},

  'O4A':{nombre:'Inventario de Bienes',icono:'\ud83d\udce6',grupo:'OBL4',descripcion:'Inventario muebles e inmuebles, altas/bajas de bienes, activo fijo, sello oficial'},
  'O4B':{nombre:'Resguardo Documental',icono:'\ud83d\udd12',grupo:'OBL4',descripcion:'Custodia de documentacion oficial, archivo actualizado, control de documentos'},
  'O4C':{nombre:'Recursos Materiales',icono:'\ud83e\uddf1',grupo:'OBL4',descripcion:'Administracion de activo fijo, mecanismos de control, materiales didacticos'},
  'O4D':{nombre:'Mantenimiento del Plantel',icono:'\ud83d\udd27',grupo:'OBL4',descripcion:'Conservacion del inmueble, coordinacion con APF, condiciones de seguridad e higiene'},
  'O4E':{nombre:'Archivo Escolar',icono:'\ud83d\uddc4\ufe0f',grupo:'OBL4',descripcion:'Archivo de tramite, inventario de transferencia, organizacion documental'},
  'O4F':{nombre:'Correspondencia Oficial',icono:'\u2709\ufe0f',grupo:'OBL4',descripcion:'Oficios, memorandums, circulares, registro y distribucion de documentos'},
  'O4G':{nombre:'Informes a Supervision',icono:'\ud83d\udce4',grupo:'OBL4',descripcion:'Datos estadisticos, reportes a supervision, informacion para autoridades educativas'},
  'O4H':{nombre:'Gestion de Personal',icono:'\ud83d\udc65',grupo:'OBL4',descripcion:'Control asistencia, incidencias, permisos, licencias, puntualidad, plantilla de personal'},
  'O4I':{nombre:'Programa La Escuela es Nuestra',icono:'\ud83c\udfdb\ufe0f',grupo:'OBL4',descripcion:'PLEEN, recursos federales, acompanamiento al CEAP, rendicion de cuentas'},

  'O5A':{nombre:'Conformacion del CEAP',icono:'\ud83e\udd1d',grupo:'OBL5',descripcion:'Comite Escolar de Administracion Participativa, asamblea escolar, eleccion de integrantes'},
  'O5B':{nombre:'Asambleas con Padres',icono:'\ud83d\udc68\u200d\ud83d\udc69\u200d\ud83d\udc67',grupo:'OBL5',descripcion:'Asambleas bimestrales, convocatoria, informar avances, participacion comunitaria'},
  'O5C':{nombre:'Rendicion de Cuentas',icono:'\ud83d\udcb0',grupo:'OBL5',descripcion:'Informe bimestral, control de gastos, periodico mural, fotografias antes/despues'},
  'O5D':{nombre:'Asociacion de Padres de Familia',icono:'\ud83d\udc6a',grupo:'OBL5',descripcion:'Constitucion de APF en primeros 15 dias, acta constitutiva, mesa directiva'},
  'O5E':{nombre:'Vinculacion Comunitaria',icono:'\ud83c\udf10',grupo:'OBL5',descripcion:'Coordinacion con autoridades municipales, programas de bienestar, actividades culturales'},
  'O5F':{nombre:'Contraloria Social',icono:'\ud83d\udd0d',grupo:'OBL5',descripcion:'Comite de Contraloria Social, vocales de transparencia, vigilancia de recursos'},

  'O6A':{nombre:'Comite de Proteccion Civil',icono:'\ud83d\udee1\ufe0f',grupo:'OBL6',descripcion:'Comite de Proteccion Civil y Seguridad Escolar, acta constitutiva, formato EX-01'},
  'O6B':{nombre:'Programa Interno Proteccion Civil',icono:'\ud83d\udcd5',grupo:'OBL6',descripcion:'PIPCE, 24 formatos, plan de emergencia, directorio de emergencias'},
  'O6C':{nombre:'Simulacros',icono:'\ud83d\udea8',grupo:'OBL6',descripcion:'Minimo 4 por ciclo, calendario, bitacora, evaluacion post-simulacro'},
  'O6D':{nombre:'Botiquin de Primeros Auxilios',icono:'\ud83c\udfe5',grupo:'OBL6',descripcion:'Contenido vigente, inventario actualizado, manual de primeros auxilios'},
  'O6E':{nombre:'Senalizacion',icono:'\ud83e\udea7',grupo:'OBL6',descripcion:'NOM-026-STPS, rutas evacuacion, puntos reunion, salidas emergencia, croquis'},
  'O6F':{nombre:'Protocolo Entrega de Ninos',icono:'\ud83d\udc76',grupo:'OBL6',descripcion:'Credencial de persona autorizada, maximo 3 autorizados, verificacion, salida anticipada'},
  'O6G':{nombre:'Revision de Instalaciones',icono:'\ud83c\udfd7\ufe0f',grupo:'OBL6',descripcion:'Diagnostico de seguridad, riesgos internos y externos, mapa de riesgos'},
  'O6H':{nombre:'Extintores',icono:'\ud83e\uddef',grupo:'OBL6',descripcion:'NOM-002-STPS, certificados vigentes, recarga, mantenimiento, senalizacion'},
  'O6I':{nombre:'Brigadas',icono:'\ud83e\uddba',grupo:'OBL6',descripcion:'4 brigadas basicas: evacuacion, primeros auxilios, incendios, comunicacion'},
  'O6J':{nombre:'Comite de Salud Escolar',icono:'\u2764\ufe0f',grupo:'OBL6',descripcion:'Acta de instalacion, REPASE, higiene, nutricion, jornadas de limpieza'},
  'O6K':{nombre:'Filtro de Salud',icono:'\ud83c\udf21\ufe0f',grupo:'OBL6',descripcion:'3 filtros: casa, entrada escuela, salon. Auto-manifestacion, bitacora'},

  'O7A':{nombre:'TIFC (Taller Intensivo)',icono:'\ud83c\udf93',grupo:'OBL7',descripcion:'Talleres intensivos de formacion continua, agosto y julio, sesiones para directivos'},
  'O7B':{nombre:'Diagnostico de Necesidades Formativas',icono:'\ud83d\udd0e',grupo:'OBL7',descripcion:'Encuestas, observaciones, matrices, areas de fortalecimiento del colectivo docente'},
  'O7C':{nombre:'Plan de Formacion del Colectivo',icono:'\ud83d\udcd6',grupo:'OBL7',descripcion:'Acciones formativas alineadas al diagnostico, cronograma, Estrategia Estatal de Formacion'},
  'O7D':{nombre:'Procesos USICAMM',icono:'\ud83c\udfc5',grupo:'OBL7',descripcion:'Convocatorias admision, promocion vertical y horizontal, reconocimiento'},
  'O7E':{nombre:'Cursos DGFCDD',icono:'\ud83d\udcbb',grupo:'OBL7',descripcion:'Catalogo de formacion continua, inscripcion del personal, cursos oficiales'},
  'O7F':{nombre:'Formacion de Directivos',icono:'\ud83d\udc54',grupo:'OBL7',descripcion:'Programa de Formacion de Directivos en Servicio 2022-2026, Mejoredu, liderazgo pedagogico'},
  'O7G':{nombre:'CTE como Espacio Formativo',icono:'\ud83d\udd04',grupo:'OBL7',descripcion:'Reflexion sobre la practica en CTE, intercambio de experiencias, formacion situada'},
  'O7H':{nombre:'Acompanamiento Pedagogico (Formacion)',icono:'\ud83e\udd32',grupo:'OBL7',descripcion:'Visitas de observacion, retroalimentacion para desarrollo profesional'},
  'O7I':{nombre:'Constancias y Acreditaciones',icono:'\ud83d\udcdc',grupo:'OBL7',descripcion:'Gestion, resguardo y entrega de constancias de participacion en actividades formativas'},
  'O7J':{nombre:'Expediente del Personal',icono:'\ud83d\udcc2',grupo:'OBL7',descripcion:'Trayectoria formativa de cada docente, evidencias, nombramiento, documentacion'},
  'O7K':{nombre:'Evaluacion del Impacto Formativo',icono:'\ud83d\udcc9',grupo:'OBL7',descripcion:'Valorar si las acciones formativas mejoran la practica docente y aprendizajes'}
};

// ============================================================
// VARIABLES GLOBALES
// ============================================================
var TOKEN = localStorage.getItem('adse_token') || '';
var USUARIO = null;
var nivelActual = 1;
var oblActual = null;
var tareaActual = null;
var herramientaActual = null;
var chatOpen = false;
var MIS_CONTACTOS = [];

// ============================================================
// FUNCIONES DE AUTENTICACION
// ============================================================
function showError(m){
  var e = document.getElementById('loginError');
  e.textContent = m; e.style.display = 'block';
  setTimeout(function(){ e.style.display = 'none'; }, 3000);
}

function toggleRegister(){
  var a = document.getElementById('loginForm');
  var b = document.getElementById('registerForm');
  a.style.display = a.style.display === 'none' ? 'block' : 'none';
  b.style.display = b.style.display === 'none' ? 'block' : 'none';
}

function doLogin(){
  var u = document.getElementById('loginUser').value.trim();
  var p = document.getElementById('loginPass').value;
  if(!u || !p){ showError('Completa todos los campos'); return; }
  fetch('/api/login', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({username:u, password:p})
  }).then(function(r){ return r.json(); }).then(function(d){
    if(d.exito){
      TOKEN = d.token; USUARIO = d.usuario;
      localStorage.setItem('adse_token', TOKEN);
      document.getElementById('loginOverlay').style.display = 'none';
      initApp();
    } else { showError(d.mensaje || 'Error'); }
  }).catch(function(){ showError('Error de conexion'); });
}

function doRegister(){
  var u = document.getElementById('regUser').value.trim();
  var n = document.getElementById('regName').value.trim();
  var e = document.getElementById('regEmail').value.trim();
  var p = document.getElementById('regPass').value;
  if(!u || !p || !n){ showError('Completa todos los campos'); return; }
  if(p.length < 6){ showError('Minimo 6 caracteres'); return; }
  fetch('/api/registro', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({username:u, password:p, nombre:n, email:e})
  }).then(function(r){ return r.json(); }).then(function(d){
    if(d.exito){
      TOKEN = d.token; USUARIO = d.usuario;
      localStorage.setItem('adse_token', TOKEN);
      document.getElementById('loginOverlay').style.display = 'none';
      initApp();
    } else { showError(d.mensaje || 'Error'); }
  }).catch(function(){ showError('Error de conexion'); });
}

function checkAuth(){
  if(!TOKEN) return;
  fetch('/api/usuario', {headers:{'Authorization':'Bearer '+TOKEN}})
  .then(function(r){ return r.json(); }).then(function(d){
    if(d.autenticado){
      USUARIO = d.usuario;
      document.getElementById('loginOverlay').style.display = 'none';
      initApp();
    }
  }).catch(function(){});
}

function doLogout(){
  TOKEN = '';
  USUARIO = null;
  localStorage.removeItem('adse_token');
  document.getElementById('loginOverlay').style.display = 'flex';
  document.getElementById('mainApp').style.display = 'none';
  document.getElementById('chatFloat').style.display = 'none';
}

// ============================================================
// TOAST NOTIFICACIONES
// ============================================================
function showToast(msg, tipo){
  var t = document.createElement('div');
  t.className = 'toast ' + (tipo || 'success');
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(function(){ t.remove(); }, 3000);
}

// ============================================================
// INICIALIZACION
// ============================================================
function initApp(){
  document.getElementById('mainApp').style.display = 'flex';
  document.getElementById('chatFloat').style.display = 'block';
  loadContacts();
  renderNivel1();
}

// ============================================================
// NIVEL 1 — OBLIGACIONES
// ============================================================
function renderNivel1(){
  nivelActual = 1; oblActual = null; tareaActual = null; herramientaActual = null;
  document.getElementById('rightTitle').textContent = '7 Obligaciones del Director de Secundaria';
  document.getElementById('rightSubtitle').textContent = 'Selecciona una obligacion para ver sus tareas';

  var left = '<div class="left-info-card"><div class="left-info-icon">\ud83c\udf93</div>';
  left += '<h3>Bienvenido' + (USUARIO ? ' ' + USUARIO.nombre : '') + '</h3>';
  left += '<p>Plataforma ADSE para directores de Escuela Secundaria. 7 obligaciones, herramientas interactivas con ahorro del 80-90% de trabajo.</p></div>';
  left += '<div class="left-info-card"><h3>Nivel Secundaria — Fase 6</h3>';
  left += '<p>\u2022 1ro, 2do y 3ro de secundaria<br>\u2022 11 asignaturas (NEM)<br>\u2022 Evaluaci\u00f3n trimestral 5-10<br>\u2022 Ciclo 2025-2026</p></div>';
  left += renderCalendarioWidget();
  left += '<button class="btn-contactos" onclick="abrirContactos()">&#128199; Mis Contactos</button>';
  left += '<button class="logout-btn" onclick="doLogout()">\u274c Cerrar sesi\u00f3n</button>';
  document.getElementById('panelLeftContent').innerHTML = left;

  var html = '<div class="grid-cards fade-in">';
  OBLIGACIONES.forEach(function(o){
    html += '<div class="card" onclick="renderNivel2(\'' + o.id + '\')">';
    html += '<div class="card-color-bar" style="background:' + o.color + '"></div>';
    html += '<div class="card-badge">' + o.tareas.length + ' tareas</div>';
    html += '<div class="card-icon">' + o.icono + '</div>';
    html += '<div class="card-title">' + o.nombre + '</div>';
    html += '<div class="card-desc">' + o.desc + '</div></div>';
  });
  html += '</div>';
  document.getElementById('panelRightContent').innerHTML = html;
}

// ============================================================
// NIVEL 2 — TAREAS DE UNA OBLIGACION
// ============================================================
function renderNivel2(oblId){
  nivelActual = 2; oblActual = oblId; tareaActual = null; herramientaActual = null;
  var obl = OBLIGACIONES.find(function(o){ return o.id === oblId; });

  document.getElementById('rightTitle').textContent = obl.icono + ' ' + obl.nombre;
  document.getElementById('rightSubtitle').textContent = 'Selecciona una tarea para ver sus herramientas';

  var left = '<div class="back-btn" onclick="renderNivel1()">\u2190 Volver a Obligaciones</div>';
  left += '<div class="left-info-card"><span class="nivel-badge" style="background:' + obl.color + ';color:#fff">OBLIGACION</span>';
  left += '<div class="left-info-icon">' + obl.icono + '</div>';
  left += '<h3>' + obl.nombre + '</h3><p>' + obl.desc + '</p>';
  left += '<p style="margin-top:8px;color:var(--accent2);font-weight:700">' + obl.tareas.length + ' tareas</p></div>';
  document.getElementById('panelLeftContent').innerHTML = left;

  var html = '<div class="grid-cards fade-in">';
  obl.tareas.forEach(function(tId){
    var t = TAREAS[tId];
    if(!t) return;
    var numHerr = 0;
    if(PLANTILLAS_DATA[tId] && PLANTILLAS_DATA[tId].herramientas){
      numHerr = PLANTILLAS_DATA[tId].herramientas.length;
    }
    html += '<div class="card" onclick="renderNivel3(\'' + tId + '\')">';
    html += '<div class="card-color-bar" style="background:' + obl.color + '"></div>';
    if(numHerr > 0) html += '<div class="card-badge">' + numHerr + ' herr.</div>';
    html += '<div class="card-icon">' + t.icono + '</div>';
    html += '<div class="card-title">' + t.nombre + '</div>';
    html += '<div class="card-desc">' + t.descripcion + '</div></div>';
  });
  html += '</div>';
  document.getElementById('panelRightContent').innerHTML = html;
}

// ============================================================
// NIVEL 3 — HERRAMIENTAS DE UNA TAREA
// ============================================================
function renderNivel3(tId){
  nivelActual = 3; tareaActual = tId; herramientaActual = null;
  var t = TAREAS[tId];
  if(!t){ renderNivel1(); return; }
  var obl = OBLIGACIONES.find(function(o){ return o.id === t.grupo; });

  document.getElementById('rightTitle').textContent = t.icono + ' ' + t.nombre;
  document.getElementById('rightSubtitle').textContent = 'Herramientas disponibles para esta tarea';

  var left = '<div class="back-btn" onclick="renderNivel2(\'' + t.grupo + '\')">\u2190 Volver a ' + obl.nombre + '</div>';
  left += '<div class="left-info-card"><span class="nivel-badge" style="background:' + obl.color + ';color:#fff">TAREA</span>';
  left += '<div class="left-info-icon">' + t.icono + '</div>';
  left += '<h3>' + t.nombre + '</h3><p>' + t.descripcion + '</p></div>';
  document.getElementById('panelLeftContent').innerHTML = left;

  var herramientas = [];
  if(PLANTILLAS_DATA[tId] && PLANTILLAS_DATA[tId].herramientas){
    herramientas = PLANTILLAS_DATA[tId].herramientas;
  }

  var html = '<div class="grid-cards fade-in">';
  if(herramientas.length > 0){
    herramientas.forEach(function(h, idx){
      html += '<div class="card" onclick="renderNivel4(\'' + tId + '\',' + idx + ')">';
      html += '<div class="card-color-bar" style="background:' + obl.color + '"></div>';
      html += '<div class="card-icon">\ud83d\udcdd</div>';
      html += '<div class="card-title">' + h.nombre + '</div>';
      if(h.campos) html += '<div class="card-desc">' + h.campos.length + ' campos interactivos</div>';
      html += '</div>';
    });
  } else {
    html += '<div class="left-info-card"><p>Usa el chat para generar documentos de esta tarea. Las plantillas interactivas se estan agregando.</p></div>';
  }
  html += '</div>';
  html += '<div style="margin-top:16px"><button class="btn-action btn-guardar" onclick="askAI(\'' + tId + '\')">\ud83d\udcac Consultar al Agente sobre esta tarea</button></div>';
  document.getElementById('panelRightContent').innerHTML = html;
}

// ============================================================
// NIVEL 4 — PLANTILLA/FORMULARIO INTERACTIVO
// ============================================================
function renderNivel4(tId, idx){
  nivelActual = 4; tareaActual = tId;
  var t = TAREAS[tId];
  if(!t){ renderNivel1(); return; }
  var obl = OBLIGACIONES.find(function(o){ return o.id === t.grupo; });
  var plantillaData = PLANTILLAS_DATA[tId];
  if(!plantillaData || !plantillaData.herramientas || !plantillaData.herramientas[idx]){
    showToast('Herramienta no disponible', 'error');
    return;
  }
  var herr = plantillaData.herramientas[idx];
  herramientaActual = herr;

  document.getElementById('rightTitle').textContent = '\ud83d\udcdd ' + herr.nombre;
  document.getElementById('rightSubtitle').textContent = 'Formulario interactivo — llena los campos y genera tu documento';

  var left = '<div class="back-btn" onclick="renderNivel3(\'' + tId + '\')">\u2190 Volver a ' + t.nombre + '</div>';
  left += '<div class="left-info-card"><span class="nivel-badge" style="background:var(--green);color:#fff">HERRAMIENTA</span>';
  left += '<div class="left-info-icon">\ud83d\udcdd</div>';
  left += '<h3>' + herr.nombre + '</h3>';
  if(herr.descripcion) left += '<p>' + herr.descripcion + '</p>';
  left += '</div>';
  left += '<div class="left-info-card"><h3>Instrucciones</h3>';
  left += '<p>\u2022 Llena todos los campos del formulario<br>\u2022 Los campos con * son importantes<br>\u2022 Usa Guardar para almacenar en tu cuenta<br>\u2022 Usa WhatsApp o Correo para compartir</p></div>';
  document.getElementById('panelLeftContent').innerHTML = left;

  var html = '<div class="form-container fade-in">';
  html += '<h3>' + herr.nombre + '</h3>';

  if(herr.campos && herr.campos.length > 0){
    herr.campos.forEach(function(campo){
      html += renderCampo(campo, herr.id);
    });
  }

  html += '<div class="action-buttons">';
  html += '<button class="btn-action btn-guardar" onclick="guardarFormulario(\'' + tId + '\',\'' + herr.id + '\')">\ud83d\udcbe Guardar</button>';
  html += '<button class="btn-action btn-whatsapp" onclick="enviarWhatsApp(\'' + herr.id + '\')">\ud83d\udcf1 WhatsApp</button>';
  html += '<button class="btn-action btn-correo" onclick="enviarCorreo(\'' + herr.id + '\')">\ud83d\udce7 Correo</button>';
  html += '</div>';
  html += '</div>';

  document.getElementById('panelRightContent').innerHTML = html;

  // Cargar datos guardados si existen
  cargarDatosGuardados(tId, herr.id);
}

// ============================================================
// RENDERIZAR UN CAMPO SEGUN SU TIPO
// ============================================================
function renderCampo(campo, herrId){
  var fieldId = 'field_' + herrId + '_' + campo.id;
  var html = '';

  if(campo.tipo === 'checkbox'){
    html += '<div class="form-check">';
    html += '<input type="checkbox" id="' + fieldId + '" data-campo="' + campo.id + '">';
    html += '<label for="' + fieldId + '">' + campo.label + '</label>';
    html += '</div>';
    return html;
  }

  if(campo.tipo === 'tabla'){
    html += '<div class="form-group">';
    html += '<label>' + campo.label + '</label>';
    html += renderTabla(campo, herrId);
    html += '</div>';
    return html;
  }

  html += '<div class="form-group">';
  html += '<label for="' + fieldId + '">' + campo.label + '</label>';

  if(campo.tipo === 'text' || campo.tipo === 'number' || campo.tipo === 'date' || campo.tipo === 'email'){
    html += '<input type="' + campo.tipo + '" id="' + fieldId + '" data-campo="' + campo.id + '"';
    if(campo.placeholder) html += ' placeholder="' + campo.placeholder + '"';
    html += '>';
  } else if(campo.tipo === 'textarea'){
    html += '<textarea id="' + fieldId + '" data-campo="' + campo.id + '"';
    if(campo.placeholder) html += ' placeholder="' + campo.placeholder + '"';
    html += '></textarea>';
  } else if(campo.tipo === 'select'){
    html += '<select id="' + fieldId + '" data-campo="' + campo.id + '">';
    html += '<option value="">-- Seleccionar --</option>';
    if(campo.opciones){
      campo.opciones.forEach(function(op){
        html += '<option value="' + op + '">' + op + '</option>';
      });
    }
    html += '</select>';
  } else {
    // Fallback a text
    html += '<input type="text" id="' + fieldId + '" data-campo="' + campo.id + '"';
    if(campo.placeholder) html += ' placeholder="' + campo.placeholder + '"';
    html += '>';
  }

  html += '</div>';
  return html;
}

// ============================================================
// RENDERIZAR TABLA EDITABLE
// ============================================================
function renderTabla(campo, herrId){
  var tableId = 'tabla_' + herrId + '_' + campo.id;
  var numFilas = campo.filas || 3;
  var columnas = campo.columnas || [];
  var defaults = campo.valoresPredeterminados || [];

  var html = '<div style="overflow-x:auto">';
  html += '<table class="tabla-editable" id="' + tableId + '" data-campo="' + campo.id + '" data-tipo="tabla">';
  html += '<thead><tr>';
  columnas.forEach(function(col){
    html += '<th>' + col + '</th>';
  });
  html += '</tr></thead><tbody>';

  for(var i = 0; i < numFilas; i++){
    html += '<tr>';
    for(var j = 0; j < columnas.length; j++){
      var val = '';
      if(defaults[i] && defaults[i][j]) val = defaults[i][j];
      html += '<td><input type="text" value="' + escapeHtml(val) + '" data-row="' + i + '" data-col="' + j + '"></td>';
    }
    html += '</tr>';
  }

  html += '</tbody></table>';
  html += '<button class="btn-add-row" onclick="agregarFila(\'' + tableId + '\',' + columnas.length + ')">+ Agregar fila</button>';
  html += '</div>';
  return html;
}

function escapeHtml(text){
  if(!text) return '';
  return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function agregarFila(tableId, numCols){
  var tabla = document.getElementById(tableId);
  if(!tabla) return;
  var tbody = tabla.querySelector('tbody');
  var rowCount = tbody.rows.length;
  var tr = document.createElement('tr');
  for(var j = 0; j < numCols; j++){
    var td = document.createElement('td');
    var input = document.createElement('input');
    input.type = 'text';
    input.setAttribute('data-row', rowCount);
    input.setAttribute('data-col', j);
    td.appendChild(input);
    tr.appendChild(td);
  }
  tbody.appendChild(tr);
}

// ============================================================
// RECOPILAR DATOS DEL FORMULARIO
// ============================================================
function recopilarDatos(herrId){
  var datos = {};
  // Campos simples (input, textarea, select)
  var campos = document.querySelectorAll('[data-campo]');
  campos.forEach(function(el){
    if(el.tagName === 'TABLE') return; // tablas se manejan aparte
    var campoId = el.getAttribute('data-campo');
    if(el.type === 'checkbox'){
      datos[campoId] = el.checked;
    } else {
      datos[campoId] = el.value;
    }
  });

  // Tablas editables
  var tablas = document.querySelectorAll('table[data-tipo="tabla"]');
  tablas.forEach(function(tabla){
    var campoId = tabla.getAttribute('data-campo');
    var filas = [];
    var rows = tabla.querySelectorAll('tbody tr');
    rows.forEach(function(row){
      var celdas = [];
      var inputs = row.querySelectorAll('input');
      inputs.forEach(function(inp){
        celdas.push(inp.value);
      });
      filas.push(celdas);
    });
    datos[campoId] = filas;
  });

  return datos;
}

// ============================================================
// GENERAR TEXTO DEL DOCUMENTO
// ============================================================
function generarTextoDocumento(herrId){
  if(!herramientaActual || !herramientaActual.textoBase) return 'Sin plantilla de texto';
  var datos = recopilarDatos(herrId);
  var texto = herramientaActual.textoBase;

  // Reemplazar placeholders simples {campo}
  for(var key in datos){
    var val = datos[key];
    if(Array.isArray(val)){
      // Es una tabla — formatear
      var tablaTexto = '';
      val.forEach(function(fila, idx){
        tablaTexto += (idx + 1) + '. ' + fila.join(' | ') + '\n';
      });
      val = tablaTexto;
    } else if(typeof val === 'boolean'){
      val = val ? 'SI' : 'NO';
    }
    texto = texto.split('{' + key + '}').join(val || '___');
  }

  return texto;
}

// ============================================================
// GUARDAR DATOS EN EL SERVIDOR
// ============================================================
function guardarFormulario(tareaId, herrId){
  var datos = recopilarDatos(herrId);
  fetch('/api/datos/' + tareaId, {
    method: 'POST',
    headers: {'Content-Type':'application/json', 'Authorization':'Bearer ' + TOKEN},
    body: JSON.stringify({herramienta: herrId, datos: datos})
  }).then(function(r){ return r.json(); }).then(function(d){
    if(d.exito){
      showToast('Datos guardados correctamente');
    } else {
      showToast(d.mensaje || 'Error al guardar', 'error');
    }
  }).catch(function(){
    showToast('Error de conexion', 'error');
  });
}

// ============================================================
// CARGAR DATOS GUARDADOS
// ============================================================
function cargarDatosGuardados(tareaId, herrId){
  fetch('/api/datos/' + tareaId, {
    headers: {'Authorization':'Bearer ' + TOKEN}
  }).then(function(r){ return r.json(); }).then(function(d){
    if(d.exito && d.datos && d.datos.herramienta === herrId && d.datos.datos){
      var datos = d.datos.datos;
      for(var key in datos){
        var val = datos[key];
        if(Array.isArray(val)){
          // Tabla
          var tabla = document.querySelector('table[data-campo="' + key + '"]');
          if(tabla){
            var rows = tabla.querySelectorAll('tbody tr');
            val.forEach(function(fila, i){
              if(rows[i]){
                var inputs = rows[i].querySelectorAll('input');
                fila.forEach(function(celda, j){
                  if(inputs[j]) inputs[j].value = celda;
                });
              }
            });
          }
        } else {
          var el = document.querySelector('[data-campo="' + key + '"]');
          if(el){
            if(el.type === 'checkbox'){
              el.checked = !!val;
            } else {
              el.value = val;
            }
          }
        }
      }
    }
  }).catch(function(){});
}

// ============================================================
// ENVIAR POR WHATSAPP (con selector de contactos)
// ============================================================
function enviarWhatsApp(herrId){
  var texto = generarTextoDocumento(herrId);
  var contactosConTel = MIS_CONTACTOS.filter(function(c){ return c.telefono; });
  if(contactosConTel.length === 0){
    window.open('https://wa.me/?text=' + encodeURIComponent(texto));
    return;
  }
  showContactSelector(contactosConTel, 'whatsapp', texto, '');
}

// ============================================================
// ENVIAR POR CORREO (con selector de contactos)
// ============================================================
function enviarCorreo(herrId){
  var texto = generarTextoDocumento(herrId);
  var asunto = herramientaActual ? herramientaActual.nombre : 'Documento ADSE';
  var contactosConEmail = MIS_CONTACTOS.filter(function(c){ return c.correo; });
  if(contactosConEmail.length === 0){
    window.open('mailto:?subject=' + encodeURIComponent(asunto) + '&body=' + encodeURIComponent(texto));
    return;
  }
  showContactSelector(contactosConEmail, 'correo', texto, asunto);
}

// ============================================================
// SELECTOR DE CONTACTOS (mini overlay)
// ============================================================
function showContactSelector(contactos, tipo, texto, asunto){
  var title = tipo === 'whatsapp' ? '&#128241; Enviar por WhatsApp' : '&#128231; Enviar por Correo';
  document.getElementById('contactSelectorTitle').innerHTML = title;
  var html = '';
  html += '<div class="contact-selector-general" onclick="enviarSinContacto(\'' + tipo + '\')">';
  html += tipo === 'whatsapp' ? 'Enviar sin seleccionar contacto' : 'Enviar sin seleccionar contacto';
  html += '</div>';
  contactos.forEach(function(c, idx){
    var inicial = c.nombre ? c.nombre.charAt(0).toUpperCase() : '?';
    var detalle = tipo === 'whatsapp' ? (c.telefono || '') : (c.correo || '');
    html += '<div class="contact-selector-item" onclick="enviarAContacto(' + idx + ',\'' + tipo + '\')">';
    html += '<div class="contacto-avatar">' + inicial + '</div>';
    html += '<div class="contacto-info">';
    html += '<div class="contacto-nombre">' + escapeHtml(c.nombre || 'Sin nombre') + '</div>';
    html += '<div class="contacto-detalle">' + escapeHtml(detalle) + '</div>';
    html += '</div></div>';
  });
  document.getElementById('contactSelectorList').innerHTML = html;
  document.getElementById('contactSelectorOverlay').classList.add('open');
  // Store temp data for sending
  window._selectorTexto = texto;
  window._selectorAsunto = asunto || '';
  window._selectorTipo = tipo;
  window._selectorContactos = contactos;
}

function enviarSinContacto(tipo){
  cerrarContactSelector();
  var texto = window._selectorTexto || '';
  var asunto = window._selectorAsunto || '';
  if(tipo === 'whatsapp'){
    window.open('https://wa.me/?text=' + encodeURIComponent(texto));
  } else {
    window.open('mailto:?subject=' + encodeURIComponent(asunto) + '&body=' + encodeURIComponent(texto));
  }
}

function enviarAContacto(idx, tipo){
  cerrarContactSelector();
  var contactos = window._selectorContactos || [];
  var c = contactos[idx];
  if(!c) return;
  var texto = window._selectorTexto || '';
  var asunto = window._selectorAsunto || '';
  if(tipo === 'whatsapp'){
    var tel = c.telefono.replace(/[^0-9+]/g, '');
    if(tel.indexOf('+') === -1 && tel.length === 10) tel = '52' + tel;
    tel = tel.replace(/\+/g, '');
    window.open('https://wa.me/' + tel + '?text=' + encodeURIComponent(texto));
  } else {
    window.open('mailto:' + encodeURIComponent(c.correo) + '?subject=' + encodeURIComponent(asunto) + '&body=' + encodeURIComponent(texto));
  }
}

function cerrarContactSelector(){
  document.getElementById('contactSelectorOverlay').classList.remove('open');
}

// ============================================================
// DIRECTORIO DE CONTACTOS
// ============================================================
function abrirContactos(){
  document.getElementById('contactosOverlay').classList.add('open');
  if('contacts' in navigator && 'ContactsManager' in window){
    document.getElementById('btnImportPhone').style.display = 'inline-flex';
  }
  renderContacts();
}

function cerrarContactos(){
  document.getElementById('contactosOverlay').classList.remove('open');
  document.getElementById('contactoForm').classList.remove('open');
}

function toggleContactForm(){
  var form = document.getElementById('contactoForm');
  form.classList.toggle('open');
  if(form.classList.contains('open')){
    document.getElementById('cfNombre').value = '';
    document.getElementById('cfTelefono').value = '';
    document.getElementById('cfCorreo').value = '';
    document.getElementById('cfCargo').value = '';
    document.getElementById('cfNombre').focus();
  }
}

function addContact(c){
  MIS_CONTACTOS.push({
    id: Date.now() + '_' + Math.random().toString(36).substr(2,5),
    nombre: c.nombre || '',
    telefono: c.telefono || '',
    correo: c.correo || '',
    cargo: c.cargo || ''
  });
}

function removeContact(id){
  MIS_CONTACTOS = MIS_CONTACTOS.filter(function(c){ return c.id !== id; });
  saveContacts();
  renderContacts();
}

function guardarContactoManual(){
  var nombre = document.getElementById('cfNombre').value.trim();
  var telefono = document.getElementById('cfTelefono').value.trim();
  var correo = document.getElementById('cfCorreo').value.trim();
  var cargo = document.getElementById('cfCargo').value.trim();
  if(!nombre && !telefono && !correo){
    showToast('Ingresa al menos nombre, telefono o correo', 'error');
    return;
  }
  addContact({nombre:nombre, telefono:telefono, correo:correo, cargo:cargo});
  saveContacts();
  renderContacts();
  toggleContactForm();
  showToast('Contacto agregado');
}

function renderContacts(){
  var container = document.getElementById('contactosList');
  if(!container) return;
  var filtro = '';
  var searchEl = document.getElementById('contactosSearch');
  if(searchEl) filtro = searchEl.value.toLowerCase().trim();
  var filtrados = MIS_CONTACTOS;
  if(filtro){
    filtrados = MIS_CONTACTOS.filter(function(c){
      return (c.nombre && c.nombre.toLowerCase().indexOf(filtro) > -1) ||
             (c.telefono && c.telefono.indexOf(filtro) > -1) ||
             (c.correo && c.correo.toLowerCase().indexOf(filtro) > -1) ||
             (c.cargo && c.cargo.toLowerCase().indexOf(filtro) > -1);
    });
  }
  if(filtrados.length === 0){
    container.innerHTML = '<div class="contactos-empty"><span>&#128199;</span>' +
      (MIS_CONTACTOS.length === 0 ? 'No tienes contactos guardados.<br>Usa los botones de arriba para importar o agregar.' : 'No se encontraron contactos con ese filtro.') +
      '</div>';
    return;
  }
  var html = '';
  filtrados.forEach(function(c){
    var inicial = c.nombre ? c.nombre.charAt(0).toUpperCase() : '?';
    html += '<div class="contacto-card">';
    html += '<div class="contacto-avatar">' + inicial + '</div>';
    html += '<div class="contacto-info">';
    html += '<div class="contacto-nombre">' + escapeHtml(c.nombre || 'Sin nombre') + '</div>';
    var detalles = [];
    if(c.telefono) detalles.push(escapeHtml(c.telefono));
    if(c.correo) detalles.push(escapeHtml(c.correo));
    html += '<div class="contacto-detalle">' + detalles.join(' &bull; ') + '</div>';
    if(c.cargo) html += '<div class="contacto-cargo">' + escapeHtml(c.cargo) + '</div>';
    html += '</div>';
    html += '<button class="contacto-delete" onclick="removeContact(\'' + c.id + '\')" title="Eliminar">&times;</button>';
    html += '</div>';
  });
  container.innerHTML = html;
}

function filtrarContactos(){
  renderContacts();
}

// ============================================================
// IMPORTAR CONTACTOS
// ============================================================
function importFromPhone(){
  if(!('contacts' in navigator)){
    showToast('No disponible en este navegador. Usa Importar CSV/VCF', 'error');
    return;
  }
  navigator.contacts.select(['name','email','tel'], {multiple:true}).then(function(contacts){
    contacts.forEach(function(c){
      addContact({
        nombre: c.name ? c.name[0] : '',
        telefono: c.tel ? c.tel[0] : '',
        correo: c.email ? c.email[0] : '',
        cargo: ''
      });
    });
    showToast(contacts.length + ' contactos importados');
    saveContacts();
    renderContacts();
  }).catch(function(){
    showToast('Importacion cancelada', 'error');
  });
}

function handleFileImport(input){
  if(!input.files || !input.files[0]) return;
  importFile(input.files[0]);
  input.value = '';
}

function importFile(file){
  var reader = new FileReader();
  reader.onload = function(e){
    var text = e.target.result;
    var contacts = [];
    if(file.name.toLowerCase().indexOf('.vcf') > -1){
      contacts = parseVCF(text);
    } else if(file.name.toLowerCase().indexOf('.csv') > -1){
      contacts = parseCSV(text);
    }
    contacts.forEach(function(c){ addContact(c); });
    showToast(contacts.length + ' contactos importados');
    saveContacts();
    renderContacts();
  };
  reader.readAsText(file);
}

function parseVCF(text){
  var contacts = [];
  var entries = text.split('END:VCARD');
  entries.forEach(function(entry){
    if(entry.indexOf('BEGIN:VCARD') === -1) return;
    var c = {nombre:'', telefono:'', correo:'', cargo:''};
    var lines = entry.split('\n');
    lines.forEach(function(line){
      line = line.trim();
      if(line.indexOf('FN:') === 0 || line.indexOf('FN;') === 0) c.nombre = line.split(':').slice(1).join(':').trim();
      if(line.indexOf('TEL') === 0 && !c.telefono) c.telefono = line.split(':').slice(1).join(':').trim();
      if(line.indexOf('EMAIL') === 0 && !c.correo) c.correo = line.split(':').slice(1).join(':').trim();
      if(line.indexOf('TITLE:') === 0) c.cargo = line.split(':').slice(1).join(':').trim();
      if(line.indexOf('ORG:') === 0 && !c.cargo) c.cargo = line.split(':').slice(1).join(':').trim();
    });
    if(c.nombre || c.telefono || c.correo) contacts.push(c);
  });
  return contacts;
}

function parseCSV(text){
  var contacts = [];
  var lines = text.split('\n');
  if(lines.length < 2) return contacts;
  var headers = lines[0].toLowerCase().split(',').map(function(h){ return h.trim().replace(/"/g,''); });
  var nameIdx = -1, phoneIdx = -1, emailIdx = -1, orgIdx = -1;
  for(var hi = 0; hi < headers.length; hi++){
    var h = headers[hi];
    if(nameIdx === -1 && (h.indexOf('name') > -1 || h.indexOf('nombre') > -1)) nameIdx = hi;
    if(phoneIdx === -1 && (h.indexOf('phone') > -1 || h.indexOf('tel') > -1 || h.indexOf('movil') > -1 || h.indexOf('celular') > -1)) phoneIdx = hi;
    if(emailIdx === -1 && (h.indexOf('email') > -1 || h.indexOf('correo') > -1 || h.indexOf('mail') > -1)) emailIdx = hi;
    if(orgIdx === -1 && (h.indexOf('org') > -1 || h.indexOf('company') > -1 || h.indexOf('cargo') > -1)) orgIdx = hi;
  }
  for(var i = 1; i < lines.length; i++){
    if(!lines[i].trim()) continue;
    var vals = lines[i].split(',').map(function(v){ return v.trim().replace(/"/g,''); });
    var c = {
      nombre: nameIdx > -1 ? (vals[nameIdx] || '') : '',
      telefono: phoneIdx > -1 ? (vals[phoneIdx] || '') : '',
      correo: emailIdx > -1 ? (vals[emailIdx] || '') : '',
      cargo: orgIdx > -1 ? (vals[orgIdx] || '') : ''
    };
    if(c.nombre || c.telefono || c.correo) contacts.push(c);
  }
  return contacts;
}

// ============================================================
// ALMACENAMIENTO DE CONTACTOS (servidor)
// ============================================================
function saveContacts(){
  if(!TOKEN) return;
  fetch('/api/datos/contactos', {
    method: 'POST',
    headers: {'Content-Type':'application/json', 'Authorization':'Bearer ' + TOKEN},
    body: JSON.stringify({contactos: MIS_CONTACTOS})
  }).catch(function(){});
}

function loadContacts(){
  if(!TOKEN) return;
  fetch('/api/datos/contactos', {
    headers: {'Authorization':'Bearer ' + TOKEN}
  }).then(function(r){ return r.json(); }).then(function(d){
    if(d.datos && d.datos.contactos){
      MIS_CONTACTOS = d.datos.contactos;
    } else if(d.exito && d.datos && Array.isArray(d.datos)){
      MIS_CONTACTOS = d.datos;
    }
  }).catch(function(){});
}

// ============================================================
// CHAT FLOTANTE
// ============================================================
function toggleChat(){
  chatOpen = !chatOpen;
  document.getElementById('chatPanel').classList.toggle('open', chatOpen);
}

function askAI(tareaId){
  var t = TAREAS[tareaId];
  if(!chatOpen) toggleChat();
  var input = document.getElementById('chatInput');
  input.value = 'Necesito ayuda con: ' + t.nombre + '. Dame la plantilla completa con toda la normativa SEP.';
  input.focus();
}

function sendChat(){
  var input = document.getElementById('chatInput');
  var msg = input.value.trim();
  if(!msg) return;
  input.value = '';
  var msgs = document.getElementById('chatMessages');
  msgs.innerHTML += '<div class="chat-msg user">' + msg.replace(/</g,'&lt;') + '</div>';
  msgs.innerHTML += '<div class="chat-msg bot" id="chatLoading">Procesando...</div>';
  msgs.scrollTop = msgs.scrollHeight;

  fetch('/api/consulta', {
    method: 'POST',
    headers: {'Content-Type':'application/json', 'Authorization':'Bearer ' + TOKEN},
    body: JSON.stringify({consulta: msg, funcion_id: tareaActual || ''})
  }).then(function(r){ return r.json(); }).then(function(d){
    var el = document.getElementById('chatLoading');
    if(el) el.remove();
    var resp = d.respuesta || d.error || 'Sin respuesta';
    msgs.innerHTML += '<div class="chat-msg bot">' + resp.replace(/\n/g,'<br>') + '</div>';
    msgs.scrollTop = msgs.scrollHeight;
  }).catch(function(){
    var el = document.getElementById('chatLoading');
    if(el) el.innerHTML = 'Error de conexion.';
  });
}

// ============================================================
// INICIAR
// ============================================================
checkAuth();
</script>
</body>
</html>'''
