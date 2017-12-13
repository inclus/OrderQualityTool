var _ = require('lodash');
ModelHelper = {
    getFields: function (id, meta_data) {
        var key = "fields_" + id.toLowerCase();
        if (meta_data && key in meta_data) {
            return meta_data[key];
        }
        return [];
    },
    getFormulations: function (id, meta_data) {
        var key = "formulations_" + id.toLowerCase();
        if (meta_data && key in meta_data) {
            return meta_data[key];
        }
        return [];
    }
};

var newModel = function (id, name, meta_data) {
    return Object.create({}, {
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
            value: ModelHelper.getFields(id, meta_data),
            enumerable: true
        },
        formulations: {
            value: ModelHelper.getFormulations(id, meta_data),
            enumerable: true
        }
    })
};

var BaseTest = Object.create(null);

BaseTest.prototype = {
    newGroup:
        function (group_number) {
            return {
                cycle: this.cycles[0],
                model: this.models[0],
                aggregation: this.calculations[0],
                selected_consumption_fields: [],
                selected_formulations: [],
                name: "G" + group_number
            }

        }
};
var FacilityTest = function (meta_data) {
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
                newModel("Adult", "Adult Records", meta_data),
                newModel("Paed", "Paed Records", meta_data),
                newModel("Consumption", "Consumption Records", meta_data)
            ],
            enumerable: true
        }

    })
};

var newTest = function (meta_data, id, name) {
    return Object.create(FacilityTest(meta_data), {
        id: {
            value: id,
            writable: true,
            enumerable: true
        },
        name: {
            value: name,
            writable: true,
            enumerable: true
        }
    })
};

var FacilityTestWithTracingFormulation = function (meta_data) {
    return newTest(meta_data, "FacilityTwoGroupsAndTracingFormulation", "Facility with 2 Groups And Tracing Formulation")
};

var buildType = function (meta_data, type_data) {
    return newTest(meta_data, type_data.id, type_data.name)
};


module.exports = ["$scope", "metadataService", "ngDialog", function ($scope, metadataService, ngDialog) {
    var ctrl = this;

    ctrl.setMultiplicationFactors = function (has_factors, group) {
        if (has_factors && !group.factors) {
            group.factors = {};
            group.selected_fields.forEach(function (field) {
                group.factors[field] = 1
            })
        }
    };

    ctrl.previewDefinition = function (definition) {
        ngDialog.open({
            template: require('./test.definition.preview.html'),
            plain: true,
            closeByDocument: false,
            controller: ["$scope", "locations", function Ctrl($scope, locations) {
                $scope.locations = locations;
                $scope.update = function (location, cycle) {
                    definition.sample = {cycle: cycle, location: location};
                    metadataService.previewDefinition(definition).then(function (preview) {
                        $scope.groups = preview.groups;
                    })
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


    var build_from_value = function (meta_data) {
        var definition = JSON.parse(ctrl.value);
        definition.type = buildType(meta_data, definition.type);
        definition.groups.forEach(function (group) {
            group.model = newModel(group.model.id, group.model.name, meta_data);
        });
        ctrl.definition = definition;
    };


    ctrl.reset = function () {
        ctrl.definition = {type: FacilityTest(ctrl.meta_data), operatorConstant: 1.0};
        var testType = ctrl.definition.type;
        ctrl.definition.groups = [
            testType.newGroup(1, ctrl.meta_data),
            testType.newGroup(2, ctrl.meta_data)];
    };

    var init = function () {
        metadataService.getAllFields().then(function (meta_data) {
            ctrl.meta_data = meta_data;
            ctrl.testTypes = [
                FacilityTest(meta_data),
                FacilityTestWithTracingFormulation(meta_data)
            ];
            if (ctrl.value) {
                build_from_value(meta_data);
            } else {
                ctrl.reset();
            }
        });
    };

    init();

    return ctrl;
}];