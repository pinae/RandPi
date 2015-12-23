(function(app) {
  app.Statistics = ng.core
    .Component({
      selector: 'my-app',
      appInjector: [Http]
    })
    .View({
      template: "<h1>RandPi Entropy Server</h1>\n" +
                "<h2>Statistics</h2>\n" +
                "<p>The entropy pool is {{ poolSize }} bits.</p>"
    })
    .Class({
      constructor: [new ng.core.Inject(Http), function(http) {
        this.poolSize = "...loading...";
        http.get("statistics").subscribe(function(response) {
            console.log(response.text())
            this.poolSize = response.json()["pool_size"]
        })
      }]
    });
})(window.app || (window.app = {}));