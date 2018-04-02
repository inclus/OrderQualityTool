var testTypes = require("./test.types");
var _ = require("lodash");

var testDefinitionController = ["$scope", "metadataService", "previewService", function ($scope, metadataService, preview) {
    var ctrl = this;

    ctrl.setMultiplicationFactors = function (has_factors, group) {
        if (has_factors && !group.factors) {
            group.factors = {};
            group.selected_fields.forEach(function (field) {
                group.factors[field] = 1;
            });
        }
    };

    ctrl.getFormulationsForFactors = function (group) {
        var key = "patient_formulations";
        if (group.model.id === "Consumption"){
            key = "consumption_formulations";
        }
        if (group.model.hasTrace) {
            return _.chain(group.model.tracingFormulations).map(key).flatten().value();
        } else {
            return group.selected_formulations;
        }
    };

    ctrl.previewDefinition = function (definition) {
        preview.show(definition);
    };

    ctrl.reset = function () {
        ctrl.definition = {type: testTypes.FacilityTest(ctrl.metaData), operatorConstant: 1.0};
        var testType = ctrl.definition.type;
        ctrl.definition.groups = testType.getGroups(ctrl.metaData);
    };

    ctrl.testTypeChanged = function (testType) {
        if (testType) {
            ctrl.definition.groups = testType.getGroups(ctrl.metaData);
        }
    };

    var init = function () {
        metadataService.getAllFields().then(function (metaData) {
            ctrl.metaData = metaData;
            ctrl.testTypes = [
                testTypes.FacilityTest(metaData),
                testTypes.FacilityTestWithTracingFormulation(metaData),
                testTypes.SingleGroupFacilityTest(metaData),
                testTypes.ClassBasedTest(metaData)
            ];
            if (ctrl.value) {
                ctrl.definition = testTypes.buildDefinition(ctrl.value, metaData);
            } else {
                ctrl.reset();
            }
        });
    };

    init();

    return ctrl;
}];
module.exports = testDefinitionController;