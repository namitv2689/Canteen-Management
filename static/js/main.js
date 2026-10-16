(function () {
  // Mobile navigation toggle
  var toggle = document.querySelector('[data-nav-toggle]');
  var nav = document.querySelector('[data-nav]');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open);
    });
  }

  // Dismissible flash messages (auto-hide after 5s)
  document.querySelectorAll('[data-dismiss]').forEach(function (btn) {
    btn.addEventListener('click', function () { btn.parentElement.remove(); });
  });
  setTimeout(function () {
    document.querySelectorAll('.flash').forEach(function (el) { el.remove(); });
  }, 5000);

  // Confirm destructive actions
  document.querySelectorAll('[data-confirm]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      if (!window.confirm(btn.getAttribute('data-confirm'))) e.preventDefault();
    });
  });

  // Client-side table filter
  document.querySelectorAll('[data-filter]').forEach(function (input) {
    var table = document.getElementById(input.getAttribute('data-filter'));
    if (!table) return;
    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      table.querySelectorAll('tbody tr').forEach(function (row) {
        row.style.display = row.textContent.toLowerCase().indexOf(q) === -1 ? 'none' : '';
      });
    });
  });

  // Live display board
  var board = document.querySelector('[data-board]');
  if (board) {
    var nowEl = board.querySelector('[data-now]');
    var nowNumEl = board.querySelector('[data-now-number]');
    var nextEl = board.querySelector('[data-next]');
    var servedEl = board.querySelector('[data-served]');
    var updatedEl = board.querySelector('[data-updated]');
    var current = null;

    var renderList = function (el, items) {
      el.innerHTML = '';
      if (!items.length) {
        var li = document.createElement('li');
        li.className = 'muted';
        li.textContent = 'None';
        el.appendChild(li);
        return;
      }
      items.forEach(function (c) {
        var li = document.createElement('li');
        li.textContent = c.display_name;
        if (c.customer_name) {
          var tag = document.createElement('span');
          tag.className = 'chip-number';
          tag.textContent = c.number;
          li.appendChild(tag);
        }
        el.appendChild(li);
      });
    };

    var refresh = function () {
      fetch(board.getAttribute('data-api'), { cache: 'no-store' })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          var now = data.now_serving;
          var num = now ? now.label : '—';
          if (num !== current) {
            nowEl.textContent = now ? now.display_name : '—';
            nowNumEl.textContent = now && now.customer_name ? now.number : '';
            nowNumEl.hidden = !(now && now.customer_name);
            nowEl.classList.remove('flash-in');
            void nowEl.offsetWidth;
            nowEl.classList.add('flash-in');
            current = num;
          }
          renderList(nextEl, data.up_next);
          renderList(servedEl, data.recently_served);
          updatedEl.textContent = data.now_serving
            ? 'Please collect your order at the counter.'
            : 'The queue is empty right now.';
        })
        .catch(function () { updatedEl.textContent = 'Reconnecting…'; });
    };
    refresh();
    setInterval(refresh, 5000);
  }
})();
