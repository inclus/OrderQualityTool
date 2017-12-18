var angular = require("angular");
require("angular-ui-router");
require("angular-selector/dist/angular-selector");
require("angular-selector/dist/angular-selector.css");
require("ng-dialog");
require("../../node_modules/ng-dialog/css/ngDialog.css");
require("../../node_modules/ng-dialog/css/ngDialog-theme-default.css");
require("../../node_modules/angular-loading-bar/build/loading-bar.js");
require("../../node_modules/angular-loading-bar/build/loading-bar.css");
require("angular-animate");

var testDefinitionModule = angular.module("testDefinition", ["selector", "ngDialog", "angular-loading-bar", "ngAnimate"]);

var testDefinitionController = require("./test.definition.component");
var metadataService = require("./metadata.service");
var previewService = require("./preview.service");

testDefinitionModule.service("metadataService", metadataService);
testDefinitionModule.service("previewService", previewService);
testDefinitionModule.component("testDefinition", {
    template: require("./test.definition.html"),
    controller: testDefinitionController,
    controllerAs: "ctrl",
    bindings: {
        value: "@"
    }
});