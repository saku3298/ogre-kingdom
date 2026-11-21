/* DEMON図鑑・相関図：タップで拡大表示（前後の切替つき） */
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll("a.zoom"));
  if (!links.length) return;
  var box = document.createElement("div");
  box.className = "lb";
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-modal", "true");
  box.innerHTML =
    '<button type="button" class="lb-close" aria-label="閉じる">×</button>' +
    '<button type="button" class="lb-nav lb-prev" aria-label="前へ">‹</button>' +
    '<figure><img alt=""><figcaption></figcaption></figure>' +
    '<button type="button" class="lb-nav lb-next" aria-label="次へ">›</button>';
  document.body.appendChild(box);
  var im = box.querySelector("img"), cap = box.querySelector("figcaption"), cur = 0, opener = null;
  var multi = links.length > 1;
  if (!multi) box.classList.add("single");
  function show(i) {
    cur = (i + links.length) % links.length;
    im.src = links[cur].getAttribute("href");
    im.alt = links[cur].getAttribute("data-alt") || "";
    cap.textContent = links[cur].getAttribute("data-cap") || "";
  }
  function open(i, from) {
    opener = from; show(i);
    box.classList.add("open"); document.body.classList.add("lb-lock");
    box.querySelector(".lb-close").focus();
  }
  function close() {
    box.classList.remove("open"); document.body.classList.remove("lb-lock");
    if (opener) opener.focus();
  }
  links.forEach(function (a, i) {
    a.addEventListener("click", function (ev) { ev.preventDefault(); open(i, a); });
  });
  box.addEventListener("click", function (ev) {
    var t = ev.target;
    if (t.classList.contains("lb-prev")) show(cur - 1);
    else if (t.classList.contains("lb-next")) show(cur + 1);
    else if (t.tagName !== "IMG") close();
  });
  document.addEventListener("keydown", function (ev) {
    if (!box.classList.contains("open")) return;
    if (ev.key === "Escape") close();
    else if (multi && ev.key === "ArrowLeft") show(cur - 1);
    else if (multi && ev.key === "ArrowRight") show(cur + 1);
  });
})();
