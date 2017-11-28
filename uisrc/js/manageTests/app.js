var angular = require('angular');
require("angular-ui-router");
require("angular-selector/dist/angular-selector");
require("angular-selector/dist/angular-selector.css");

var manageTestsModule = angular.module("manageTests", ["selector"]);

var addTestController = require("./controllers/add.tests.controller");

manageTestsModule.component('addTests', {
  template: require("../../views/manageTests.html"),
  controller: addTestController,
  controllerAs: "ctrl",
  bindings: {
    value: '@'
  }
});


