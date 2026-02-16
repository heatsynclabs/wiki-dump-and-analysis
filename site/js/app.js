// HeatSync Labs Governance Site - Tab switching and mobile menu

document.addEventListener('DOMContentLoaded', function() {
  // Tab switching
  document.querySelectorAll('.tab-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var container = btn.closest('.page-wrapper') || document;
      var tabGroup = btn.getAttribute('data-tab');

      // Deactivate all tabs in this group
      container.querySelectorAll('.tab-btn').forEach(function(b) {
        b.classList.remove('active');
      });
      container.querySelectorAll('.tab-content').forEach(function(c) {
        c.classList.remove('active');
      });

      // Activate clicked tab
      btn.classList.add('active');
      var target = container.querySelector('#tab-' + tabGroup);
      if (target) target.classList.add('active');
    });
  });

  // Mobile menu toggle
  var toggle = document.querySelector('.menu-toggle');
  var sidebar = document.querySelector('.sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', function() {
      sidebar.classList.toggle('open');
    });

    // Close sidebar on link click (mobile)
    sidebar.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        if (window.innerWidth <= 768) {
          sidebar.classList.remove('open');
        }
      });
    });
  }

  // Highlight active sidebar link
  var currentPath = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.sidebar nav a').forEach(function(link) {
    var href = link.getAttribute('href');
    if (href === currentPath) {
      link.classList.add('active');
    }
  });
});
