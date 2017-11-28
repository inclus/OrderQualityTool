var angular = require('angular');
require("angular-ui-router");
require("ui-select/dist/select");
require("ui-select/dist/select.css");

var manageTestsModule = angular.module("manageTests", ["ui.router", 'ui.select']);

var addTestController = require("./controllers/add.tests.controller");

manageTestsModule.component('addTests', {
  template: require("../../views/manageTests.html"),
  controller: addTestController,
  controllerAs: "ctrl"
});


