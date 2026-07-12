$(function () {
  // Auto-dismiss flash messages after 4 seconds
  setTimeout(function () {
    $('.alert').fadeOut('slow');
  }, 4000);

  // Highlight the current nav link based on URL path
  var path = window.location.pathname;
  $('.navbar-eventhive .nav-link').each(function () {
    if ($(this).attr('href') === path) {
      $(this).addClass('active');
    }
  });
});
