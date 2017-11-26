var angular = require('angular');
require("angular-ui-router");
require("ui-select/dist/select");
require("ui-select/dist/select.css");

var manageTestsModule = angular.module("manageTests", ["ui.router", 'ui.select']);

var addTestController = require("./controllers/add.tests.controller");

manageTestsModule.controller("AddTests", addTestController);

manageTestsModule.config(["$stateProvider", "$urlRouterProvider",
    function($stateProvider, $urlRouterProvider) {
        //$urlRouterProvider.otherwise("/reportingRate");
        $stateProvider
            .state("addTests", {
                url: "/",
                template: require("../../views/manageTests.html"),
                controller: "AddTests",
                controllerAs: "ctrl"
            });
    }
]);

