var angular = require("angular");
require("angular-ui-router");
require("ui-select/dist/select");
require("ui-select/dist/select.css");
require("angular-bootstrap");
require("checklist-model");
require("angular-chart");
require("ng-table");

require("d3");
require("c3");


var services = angular.module("services", []);
require("./services/report.service");
var dashboard = angular.module("dashboard", ["ui.router", "ui.bootstrap", "checklist-model", "angularChart", "ngTable", "services", "ui.select"]);
require("./controllers/home.controller");
var serviceConstructor = require("../charts/charts.service");
serviceConstructor(dashboard);
var componentConstructor = require("../charts/charts.component");
componentConstructor(dashboard);
require("./controllers/main.check.controller");


dashboard.config(["$stateProvider", "$urlRouterProvider",
    function ($stateProvider, $urlRouterProvider) {
        $stateProvider
            .state("home", {
                url: "",
                template: require("../views/main.html"),
                controller: "HomeController"
            });
    }
]);


