(function () {
  'use strict';

  const SALT = Uint8Array.from(atob('T2dyZUtpbmdkb20yMDI2IQ=='), c => c.charCodeAt(0));
  const ITERATIONS = 150000;
  const SESSION_KEY = 'ogre-kingdom-volume8-password';
  const objectUrls = [];

  const overlay = document.getElementById('protected-lock');
  const form = document.getElementById('protected-lock-form');
  const input = document.getElementById('protected-password');
  const button = document.getElementById('protected-submit');
  const error = document.getElementById('protected-error');
  const protectedImages = Array.from(document.querySelectorAll('img[data-protected-src]'));

  if (!overlay || !form || !input || !button || !protectedImages.length) return;

  async function deriveKey(password) {
    const material = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(password),
      'PBKDF2',
      false,
      ['deriveKey']
    );

    return crypto.subtle.deriveKey(
      { name: 'PBKDF2', salt: SALT, iterations: ITERATIONS, hash: 'SHA-256' },
      material,
      { name: 'AES-GCM', length: 256 },
      false,
      ['decrypt']
    );
  }

  async function decryptImage(img, key) {
    const encryptedPath = img.dataset.protectedSrc;
    const response = await fetch(encryptedPath, { cache: 'no-store' });
    if (!response.ok) throw new Error('画像データを取得できませんでした。');

    const packed = new Uint8Array(await response.arrayBuffer());
    if (packed.length < 33 || new TextDecoder().decode(packed.slice(0, 4)) !== 'OGK1') {
      throw new Error('画像データの形式が正しくありません。');
    }

    const iv = packed.slice(4, 16);
    const encrypted = packed.slice(16);
    const plain = await crypto.subtle.decrypt(
      {
        name: 'AES-GCM',
        iv,
        additionalData: new TextEncoder().encode(encryptedPath),
        tagLength: 128
      },
      key,
      encrypted
    );

    const url = URL.createObjectURL(new Blob([plain], { type: 'image/jpeg' }));
    objectUrls.push(url);
    img.src = url;
  }

  async function unlock(password, remember) {
    button.disabled = true;
    input.disabled = true;
    button.textContent = '読み込み中…';
    error.textContent = '';

    try {
      const key = await deriveKey(password);
      await decryptImage(protectedImages[0], key);
      await Promise.all(protectedImages.slice(1).map(img => decryptImage(img, key)));

      if (remember) sessionStorage.setItem(SESSION_KEY, password);
      overlay.hidden = true;
      document.body.classList.remove('protected-locked');
      window.dispatchEvent(new Event('resize'));
    } catch (cause) {
      sessionStorage.removeItem(SESSION_KEY);
      error.textContent = cause instanceof DOMException
        ? 'パスワードが違います。'
        : (cause.message || '読み込みに失敗しました。');
      input.disabled = false;
      button.disabled = false;
      button.textContent = '読む';
      input.value = '';
      input.focus();
    }
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    unlock(input.value, true);
  });

  window.addEventListener('pagehide', function () {
    objectUrls.forEach(url => URL.revokeObjectURL(url));
  });

  const remembered = sessionStorage.getItem(SESSION_KEY);
  if (remembered) {
    unlock(remembered, false);
  } else {
    input.focus();
  }
})();
