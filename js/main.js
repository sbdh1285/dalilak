/* وظائف دليلك المشتركة: البحث، السمة، قائمة الهاتف، وشريط التقدم */
(function () {
  'use strict';
  var script = document.currentScript;
  var siteBase = script ? new URL('../', script.src) : new URL('./', location.href);
  var index = [];
  var searchInput = document.getElementById('searchInput');
  var searchResults = document.getElementById('searchRes');
  var themeButton = document.getElementById('themeBtn');
  var burger = document.getElementById('burger');
  var navigation = document.getElementById('nav');
  var navClose = document.getElementById('navClose');
  var scrim = document.getElementById('navScrim');

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, function (character) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[character];
    });
  }

  fetch(new URL('search-index.json', siteBase))
    .then(function (response) { if (!response.ok) throw new Error(); return response.json(); })
    .then(function (data) { index = Array.isArray(data) ? data : []; })
    .catch(function () { index = []; });

  if (localStorage.getItem('theme') === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
  function updateThemeButton() {
    if (!themeButton) return;
    var dark = document.documentElement.getAttribute('data-theme') === 'dark';
    themeButton.textContent = dark ? '☼' : '◐';
    themeButton.setAttribute('aria-pressed', String(dark));
    themeButton.setAttribute('aria-label', dark ? 'تفعيل الوضع النهاري' : 'تفعيل الوضع الليلي');
    themeButton.title = dark ? 'الوضع النهاري' : 'الوضع الليلي';
  }
  updateThemeButton();
  if (themeButton) themeButton.addEventListener('click', function () {
    var dark = document.documentElement.getAttribute('data-theme') === 'dark';
    if (dark) { document.documentElement.removeAttribute('data-theme'); localStorage.setItem('theme', 'light'); }
    else { document.documentElement.setAttribute('data-theme', 'dark'); localStorage.setItem('theme', 'dark'); }
    updateThemeButton();
  });

  if (searchInput && searchResults) {
    searchInput.addEventListener('input', function () {
      var query = searchInput.value.trim().toLocaleLowerCase('ar');
      searchResults.innerHTML = '';
      if (query.length < 2) { searchResults.classList.remove('open'); return; }
      if (!index.length) {
        searchResults.innerHTML = '<span class="search-message">جارٍ تحميل البحث…</span>';
        searchResults.classList.add('open'); return;
      }
      var hits = index.filter(function (item) {
        return (item.t || '').toLocaleLowerCase('ar').includes(query) || (item.c || '').toLocaleLowerCase('ar').includes(query);
      }).slice(0, 7);
      if (!hits.length) searchResults.innerHTML = '<span class="search-message">لا توجد نتائج مطابقة</span>';
      else {
        hits.forEach(function (item) {
          var link = document.createElement('a');
          link.href = new URL('posts/' + encodeURIComponent(item.s) + '.html', siteBase).href;
          link.innerHTML = '<span class="sr-cat">' + escapeHtml(item.c) + '</span>' + escapeHtml(item.t);
          searchResults.appendChild(link);
        });
        var all = document.createElement('a'); all.className = 'all-results';
        all.href = new URL('search.html?q=' + encodeURIComponent(searchInput.value.trim()), siteBase).href;
        all.textContent = 'عرض كل النتائج ←'; searchResults.appendChild(all);
      }
      searchResults.classList.add('open');
    });
    searchInput.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') { searchResults.classList.remove('open'); searchInput.blur(); }
      if (event.key === 'Enter' && searchInput.value.trim().length >= 2)
        location.href = new URL('search.html?q=' + encodeURIComponent(searchInput.value.trim()), siteBase).href;
    });
  }
  document.addEventListener('click', function (event) {
    if (searchResults && !event.target.closest('.search-box')) searchResults.classList.remove('open');
  });

  function setMenu(open) {
    if (!navigation || !burger) return;
    navigation.classList.toggle('open', open); burger.setAttribute('aria-expanded', String(open));
    document.body.classList.toggle('menu-open', open);
    if (scrim) { scrim.hidden = !open; scrim.classList.toggle('open', open); }
    if (open) { var first = navigation.querySelector('a'); if (first) first.focus(); }
  }
  if (burger && navigation) burger.addEventListener('click', function () { setMenu(!navigation.classList.contains('open')); });
  if (navClose) navClose.addEventListener('click', function () { setMenu(false); burger.focus(); });
  if (scrim) scrim.addEventListener('click', function () { setMenu(false); burger.focus(); });
  if (navigation) navigation.addEventListener('click', function (event) { if (event.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && navigation && navigation.classList.contains('open')) { setMenu(false); burger.focus(); }
  });

  var progress = document.getElementById('progress');
  var toTop = document.getElementById('toTop');
  function updateScrollUi() {
    var scrollable = document.documentElement.scrollHeight - window.innerHeight;
    if (progress) progress.style.width = (scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0) + '%';
    if (toTop) toTop.classList.toggle('show', window.scrollY > 500);
  }
  window.addEventListener('scroll', updateScrollUi, {passive:true}); updateScrollUi();
  if (toTop) toTop.addEventListener('click', function () { window.scrollTo({top:0,behavior:'smooth'}); });

  window.copyLink = function () {
    var toast = document.getElementById('toast');
    function showToast() { if (!toast) return; toast.classList.add('show'); setTimeout(function(){toast.classList.remove('show');},2200); }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(location.href).then(showToast).catch(showToast);
    else showToast();
  };

  // ===== نموذج التواصل: تحقق فوري ورسائل خطأ مرتبطة بالحقول =====
  var cform = document.querySelector('.contact-form');
  if (cform) {
    var MSG = {
      valueMissing: 'هذا الحقل مطلوب.',
      typeMismatch: 'اكتب بريدًا إلكترونيًا صحيحًا، مثل name@example.com.',
      tooShort: 'الرسالة قصيرة جدًا؛ اكتب 10 أحرف على الأقل.'
    };
    function errorFor(field) {
      var v = field.validity;
      if (v.valueMissing) return MSG.valueMissing;
      if (v.typeMismatch) return MSG.typeMismatch;
      if (v.tooShort) return MSG.tooShort;
      return field.validationMessage || 'قيمة غير صالحة.';
    }
    function slot(field) {
      var id = field.id + '-error', el = document.getElementById(id);
      if (!el) {
        el = document.createElement('p');
        el.id = id; el.className = 'field-error'; el.setAttribute('aria-live', 'polite');
        field.insertAdjacentElement('afterend', el);
      }
      return el;
    }
    function validate(field, show) {
      if (!field.willValidate || field.type === 'hidden') return true;
      var ok = field.checkValidity(), el = slot(field);
      if (ok) {
        field.removeAttribute('aria-invalid'); field.classList.remove('is-invalid');
        el.textContent = ''; el.classList.remove('show');
      } else if (show) {
        field.setAttribute('aria-invalid', 'true'); field.classList.add('is-invalid');
        field.setAttribute('aria-describedby', field.id + '-error');
        el.textContent = errorFor(field); el.classList.add('show');
      }
      return ok;
    }
    var fields = Array.prototype.slice.call(cform.querySelectorAll('input:not([type=hidden]):not(.form-honeypot), select, textarea'));
    fields.forEach(function (f) {
      f.addEventListener('blur', function () { validate(f, true); });
      f.addEventListener('input', function () { if (f.classList.contains('is-invalid')) validate(f, true); });
      f.addEventListener('change', function () { validate(f, true); });
    });
    cform.setAttribute('novalidate', 'novalidate');
    cform.addEventListener('submit', function (e) {
      var bad = fields.filter(function (f) { return !validate(f, true); });
      if (bad.length) {
        e.preventDefault();
        bad[0].focus();
        bad[0].scrollIntoView({block:'center', behavior:'smooth'});
        return;
      }
      var btn = cform.querySelector('button[type=submit]');
      if (btn) { btn.disabled = true; btn.dataset.label = btn.textContent; btn.textContent = 'جارٍ الإرسال…'; }
    });
  }
})();
