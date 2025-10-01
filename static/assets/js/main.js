document.addEventListener("DOMContentLoaded", function () {

        // Flag para activar/desactivar modo fake
    const USE_FAKE = true;

    const entrada = document.getElementById("entrada");
    const enviarBtn = document.getElementById("enviar");
    const conversacion = document.getElementById("conversacion");

    // Respuestas fake
    const fakeChatResponses = [
      "Según el contexto... esta es una respuesta simulada breve.",
      "Según el contexto... aquí tienes una explicación más larga y detallada simulada.",
      "Según el contexto... lista de puntos simulada:\n- Punto 1\n- Punto 2\n- Punto 3"
    ];
    const fakeScrapResponse = "Scrapeo completado (12 fragmentos subidos).";

    function scrollAbajo() {
      conversacion.scrollTop = conversacion.scrollHeight;
    }

      function addMessage(text, sender) {
        const msg = document.createElement("span");
        msg.classList.add("msg", sender);
        msg.textContent = text;
        conversacion.appendChild(msg);
        scrollAbajo();
      }

    function enviarPregunta() {
      const pregunta = entrada.value.trim();
      if (!pregunta) return;

      const tono = document.getElementById("tono").value;
      const tipo_respuesta = document.getElementById("tipo_respuesta").value;

      addMessage(`🧑‍💻 Tú: ${pregunta}`, "user");
      entrada.value = "";
      scrollAbajo();

      if (USE_FAKE) {
        // Respuesta fake
        setTimeout(() => {
          const randomResp = fakeChatResponses[Math.floor(Math.random() * fakeChatResponses.length)];
          addMessage(`🤖 IA: ${randomResp}`, "ai");
          scrollAbajo();
        }, 600);
      } else {
        // Llamada real
        fetch("http://127.0.0.1:8001/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ texto: pregunta, tono, tipo_respuesta })
        })
          .then(res => res.json())
          .then(data => {
            addMessage(`🤖 IA: ${data.respuesta}`, "ai");
            scrollAbajo();
          })
          .catch(err => {
            addMessage(`❌ Error: ${err}`, "error");
            scrollAbajo();
          });
      }
    }

    enviarBtn.addEventListener("click", enviarPregunta);
    entrada.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        enviarPregunta();
      }
    });

    function scrapearYSubir() {
      const url = document.getElementById("url").value.trim();
      if (!url) return;

      document.getElementById("estadoScraper").innerText = "⏳ Procesando...";
      document.getElementById("conversacion").innerHTML = "";

      if (USE_FAKE) {
        setTimeout(() => {
          document.getElementById("estadoScraper").innerText = `✅ ${fakeScrapResponse}`;
        }, 1000);
      } else {
        fetch("http://127.0.0.1:8001/scrap", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url })
        })
          .then(res => res.json())
          .then(data => {
            document.getElementById("estadoScraper").innerText = `✅ ${data.resultado}`;
          })
          .catch(err => {
            document.getElementById("estadoScraper").innerText = `❌ Error: ${err}`;
          });
      }
    }

      const topButton = document.querySelector(".top-panel button"); 

    function updateButtonText() {
        if (!topButton) return;
        if (window.innerWidth <= 768) {
        topButton.textContent = "OK";
        } else {
        topButton.textContent = "Scrapear e indexar";
        }
    }

    updateButtonText();

    window.addEventListener("resize", updateButtonText);

});