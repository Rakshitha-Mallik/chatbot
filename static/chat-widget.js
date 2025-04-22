(() => {
  const iframeSrc = "https://23bb-122-173-155-236.ngrok-free.app";  // ← your ngrok URL

  const btn = document.createElement("div");
  btn.id = "chat-toggle";
  btn.innerHTML = "💬";
  document.body.appendChild(btn);

  const wrap = document.createElement("div");
  wrap.id = "chat-wrap";
  wrap.innerHTML = `<iframe src="${iframeSrc}" frameborder="0"></iframe>`;
  document.body.appendChild(wrap);

  btn.onclick = () => wrap.classList.toggle("open");

  const css = document.createElement("style");
  css.innerText = `
    #chat-toggle {
      position: fixed; bottom: 20px; right: 20px;
      width: 60px; height: 60px;
      background: #0073aa; color: #fff; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-size: 24px; cursor: pointer; z-index: 9999;
    }
    #chat-wrap {
      position: fixed; bottom: 100px; right: 20px;
      width: 350px; height: 500px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.3);
      border-radius: 8px; overflow: hidden;
      display: none; z-index: 9998;
    }
    #chat-wrap.open { display: block; }
    #chat-wrap iframe { width: 100%; height: 100%; border: none; }
  `;
  document.head.appendChild(css);
})();
