(function(app) {
  document.addEventListener('DOMContentLoaded', function() {
    ng.platform.browser.bootstrap([app.Statistics, HTTP_PROVIDERS]);
  });
})(window.app || (window.app = {}));