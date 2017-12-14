var _ = require("lodash");
ModelHelper = {
    getFields: function (id, metaData) {
        var key = "fields" + id;
        if (metaData && key in metaData) {
            return metaData[key];
        }
        return [];
    },
    getFormulations: function (id, metaData) {
        var key = "formulations" + id;
        if (metaData && key in metaData) {
            return metaData[key];
        }
        return [];
    },
    getInitialFormulations: function (id, metaData) {
        var key = "tracing" + id;
        if (metaData && key in metaData) {
            return metaData[key][0].formulations;
        }
        return [];
    }
};

var definitionModel = {
    initializeFormulations: function (formulations) {
        if (formulations && formulations.length === 0) {
            formulations = this.initialFormulations;
        }
    }
};

var newModel = function (id, name, metaData) {
    return Object.create(definitionModel, {
        id: {
            value: id,
            writable: true,
            enumerable: true
        },
        name: {
            value: name,
            writable: true,
            enumerable: true
        },
        fields: {
            value: ModelHelper.getFields(id, metaData),
            enumerable: true
        },
        formulations: {
            value: ModelHelper.getFormulations(id, metaData),
            enumerable: true
        },
        initialFormulations: {
            value: [],
            writable: true,
            enumerable: true
        }
    });
};

var newTracingModel = function (id, name, meta_data) {
    return Object.create(newModel(id, name, meta_data), {
        disabled: {
            value: true,
            writable: true,
            enumerable: true
        },
        initialFormulations: {
            value: ModelHelper.getInitialFormulations(id, meta_data),
            writable: true,
            enumerable: true
        }
    });
};

var BaseTest = Object.create(null);

BaseTest.prototype = {
    newGroup:
        function (groupNumber) {
            return {
                cycle: this.cycles[0],
                model: this.models[0],
                aggregation: this.calculations[0],
                selected_consumption_fields: [],
                selected_formulations: [],
                name: "G" + groupNumber
            };

        }
};
var FacilityTest = function (metaData) {
    return Object.create(BaseTest.prototype, {
        id: {
            value: "FacilityTwoGroups",
            writable: true,
            enumerable: true
        },
        name: {
            value: "Facility with 2 Groups of data",
            writable: true,
            enumerable: true
        },
        cycles: {
            value:
                [
                    {id: "Current", name: "Current Cycle"},
                    {id: "Next", name: "Next Cycle"},
                    {id: "Previous", name: "Previous Cycle"}
                ],
            enumerable: true

        },
        calculations: {
            value: [
                {id: "SUM", name: "Sum"},
                {id: "AVG", name: "Average"}
            ],
            enumerable: true

        },
        models: {
            value: [
                newModel("Adult", "Adult Records", metaData),
                newModel("Paed", "Paed Records", metaData),
                newModel("Consumption", "Consumption Records", metaData)
            ],
            enumerable: true,
            writable: true
        }

    });
};

var FacilityTestWithTracingFormulation = function (metaData) {
    return Object.create(FacilityTest(metaData), {
        id: {
            value: "FacilityTwoGroupsAndTracingFormulation",
            writable: true,
            enumerable: true
        },
        name: {
            value: "Facility with 2 Groups And Tracing Formulation",
            writable: true,
            enumerable: true
        },
        models: {
            value: [
                newTracingModel("Adult", "Adult Records", metaData),
                newTracingModel("Paed", "Paed Records", metaData),
                newTracingModel("Consumption", "Consumption Records", metaData)
            ],
            writable: true,
            enumerable: true
        }
    });
};

var getTypeFromJson = function (metaData, typeData) {
    if (typeData.id === "FacilityTwoGroups") {
        return FacilityTest(meta_data);
    }
    if (typeData.id === "FacilityTwoGroupsAndTracingFormulation") {
        return FacilityTestWithTracingFormulation(meta_data);
    }
};


module.exports = ["$scope", "metadataService", "ngDialog", function ($scope, metadataService, ngDialog) {
    var ctrl = this;

    ctrl.setMultiplicationFactors = function (has_factors, group) {
        if (has_factors && !group.factors) {
            group.factors = {};
            group.selected_fields.forEach(function (field) {
                group.factors[field] = 1;
            });
        }
    };

    ctrl.previewDefinition = function (definition) {
        ngDialog.open({
            template: require("./test.definition.preview.html"),
            plain: true,
            closeByDocument: false,
            controller: ["$scope", "locations", function Ctrl($scope, locations) {
                $scope.locations = locations;
                $scope.update = function (location, cycle) {
                    definition.sample = {cycle: cycle, location: location};
                    metadataService.previewDefinition(definition).then(function (preview) {
                        $scope.groups = preview.groups;
                    });
                };
                if (locations.length > 0) {
                    $scope.location = locations[0];
                    $scope.cycle = locations[0].cycles[0];
                    $scope.update($scope.location, $scope.cycle);
                }


            }],
            resolve: {
                locations: function getLocations() {
                    return metadataService.getLocations(definition);
                }
            }
        });
    };


    var build_from_value = function (metaData) {
        var definition = JSON.parse(ctrl.value);
        definition.type = getTypeFromJson(metaData, definition.type);
        if (definition.groups) {
            definition.groups.forEach(function (group) {
                group.model = newModel(group.model.id, group.model.name, metaData);
            });
        }
        ctrl.definition = definition;
    };

    ctrl.setInitialModel = function (testType) {
        console.log("initialModel", testType, ctrl.definition.groups);
        if (ctrl.definition.groups) {
            ctrl.definition.groups.forEach(function (group) {
                group.model = testType.models[0];
                group.selected_formulations = group.model.initialFormulations;
            });
        }
    };

    ctrl.reset = function () {
        ctrl.definition = {type: FacilityTest(ctrl.meta_data), operatorConstant: 1.0};
        var testType = ctrl.definition.type;
        ctrl.definition.groups = [
            testType.newGroup(1, ctrl.meta_data),
            testType.newGroup(2, ctrl.meta_data)];
    };

    var init = function () {
        metadataService.getAllFields().then(function (metaData) {
            ctrl.meta_data = metaData;
            ctrl.testTypes = [
                FacilityTest(metaData),
                FacilityTestWithTracingFormulation(metaData)
            ];
            if (ctrl.value) {
                build_from_value(metaData);
            } else {
                ctrl.reset();
            }
        });
    };

    init();

    return ctrl;
}];