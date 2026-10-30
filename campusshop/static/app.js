// Mensajes que llegan en la URL, por ejemplo /perfil?msg=Correo%20actualizado
const params = new URLSearchParams(location.search);
const msg = params.get("msg");
if (msg) {
  const caja = document.getElementById("mensaje");
  caja.innerHTML = msg;
  caja.hidden = false;
}

// Canje de cupones (perfil)
const formCupon = document.getElementById("form-cupon");
if (formCupon) {
  formCupon.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const codigo = new FormData(formCupon).get("codigo");
    const r = await fetch("/api/cupones/canjear", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ codigo }),
    });
    const datos = await r.json();
    document.getElementById("resultado-cupon").textContent = datos.mensaje || datos.detail;
    const s = await (await fetch("/api/saldo")).json();
    document.getElementById("saldo").textContent = "$" + Number(s.saldo).toFixed(2);
  });
}

// Vista previa de enlaces (herramientas)
const formPreview = document.getElementById("form-preview");
if (formPreview) {
  formPreview.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const url = new FormData(formPreview).get("url");
    const salida = document.getElementById("resultado-preview");
    salida.textContent = "Cargando…";
    const r = await fetch("/api/preview?url=" + encodeURIComponent(url));
    const texto = await r.text();
    try {
      const datos = JSON.parse(texto);
      salida.textContent = datos.contenido ?? datos.detail ?? texto;
    } catch {
      salida.textContent = texto;
    }
  });
}
