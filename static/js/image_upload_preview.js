(function () {

  function initImageUpload(config) {
    const {
      inputId,
      stripId,
      dropZoneId = null,
      countBadgeId = null,
      existingContainerId = null, // 🔹 new
      thumbSize = 64,
    } = config;

    const input = document.getElementById(inputId);
    const strip = document.getElementById(stripId);
    const dropZone = dropZoneId ? document.getElementById(dropZoneId) : null;
    const badge = countBadgeId ? document.getElementById(countBadgeId) : null;
    const existingContainer = existingContainerId
      ? document.getElementById(existingContainerId)
      : null;

    if (!input || !strip) {
      console.warn('initImageUpload: inputId or stripId not found.');
      return;
    }

    let selectedFiles = [];

    // =========================
    // 🔹 NEW FILE HANDLING
    // =========================
    function handleFiles(newFiles) {
      Array.from(newFiles).forEach(f => {
        if (!f.type.startsWith('image/')) return;

        const id = Date.now() + Math.random();
        selectedFiles.push({ id, file: f });
        renderThumb(f, id);
      });

      updateCount();
      syncInput();
    }

    function renderThumb(file, id) {
      const reader = new FileReader();

      reader.onload = e => {
        const wrap = document.createElement('div');
        wrap.dataset.id = id;

        wrap.style.cssText = `
          position:relative;
          width:${thumbSize}px;
          height:${thumbSize}px;
          flex-shrink:0;
        `;

        wrap.innerHTML = `
          <img src="${e.target.result}" alt="${file.name}"
               style="width:${thumbSize}px;height:${thumbSize}px;object-fit:cover;
                      border-radius:8px;border:1px solid #e5e7eb;">
          <button type="button"
                  style="position:absolute;top:-6px;right:-6px;width:18px;height:18px;
                         border-radius:50%;background:#fff;border:1px solid #d1d5db;
                         cursor:pointer;font-size:10px;display:flex;
                         align-items:center;justify-content:center;">✕</button>
        `;

        wrap.querySelector('button')
            .addEventListener('click', () => removeFile(id));

        strip.appendChild(wrap);
      };

      reader.readAsDataURL(file);
    }

    function removeFile(id) {
      selectedFiles = selectedFiles.filter(f => f.id !== id);
      strip.querySelector(`[data-id="${id}"]`)?.remove();
      updateCount();
      syncInput();
    }

    function syncInput() {
      const dt = new DataTransfer();
      selectedFiles.forEach(({ file }) => dt.items.add(file));
      input.files = dt.files;
    }

    function updateCount() {
      if (!badge) return;

      if (!selectedFiles.length) {
        badge.style.display = 'none';
        return;
      }

      badge.style.display = 'block';
      badge.textContent =
        `${selectedFiles.length} image${selectedFiles.length > 1 ? 's' : ''} selected`;
    }

    input.addEventListener('change', () => handleFiles(input.files));

    // =========================
    // 🔹 DRAG & DROP
    // =========================
    if (dropZone) {
      dropZone.addEventListener('dragover', e => {
        e.preventDefault();
        dropZone.style.opacity = '0.7';
      });

      dropZone.addEventListener('dragleave', () => {
        dropZone.style.opacity = '';
      });

      dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.style.opacity = '';
        handleFiles(e.dataTransfer.files);
      });
    }

    // =========================
    // 🔹 EXISTING IMAGE HANDLING (EDIT ONLY)
    // =========================
    if (existingContainer) {

      existingContainer.addEventListener('click', function (e) {
        if (!e.target.classList.contains('remove-existing')) return;

        const wrapper = e.target.closest('[data-id]');
        const id = wrapper.dataset.id;

        // mark for delete
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'delete_images';
        input.value = id;

        document.querySelector('form').appendChild(input);

        wrapper.remove();
      });

      // hide if empty
      if (!existingContainer.children.length) {
        existingContainer.style.display = 'none';
      }
    }
  }

  // expose globally
  window.initImageUpload = initImageUpload;

})();