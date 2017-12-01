var angular = require('angular');
require("angular-ui-router");
require("angular-selector/dist/angular-selector");
require("angular-selector/dist/angular-selector.css");
require("../../node_modules/ng-pattern-restrict/src/ng-pattern-restrict.js");

var testDefinitionModule = angular.module("testDefinition", ["selector", "ngPatternRestrict"]);

var testDefinitionController = require("./test.definition.component");
var metadataService = require("./metadata.service");

testDefinitionModule.service('metadataService', metadataService);
testDefinitionModule.component('testDefinition', {
  template: require("./test.definition.html"),
  controller: testDefinitionController,
  controllerAs: "ctrl",
  bindings: {
    value: '@'
  }
});