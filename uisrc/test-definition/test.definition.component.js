var models = {
    adult: "Adult",
    paed: "Paed",
    consumption: "Consumption"
};

function isAdult(model) {
    return model.id === models.adult;
}

function isAdultOrPaed(model) {
    return model.id === models.adult || model.id === models.paed;
}

function isPaed(model) {
    return model.id === models.paed;
}

function isConsumption(model) {
    return model.id === models.consumption;
}

module.exports = ["$scope", "metadataService", "ngDialog", function ($scope, metadataService, ngDialog) {
    var ctrl = this;
    ctrl.testTypes = [
        {id: "FacilityOnly", name: "Facility Only"},
        {id: "FacilityAndSampleFormulation", name: "Facility And Sample Formulation"}
    ];
    ctrl.cycles = [
        {id: "Current", name: "Current Cycle"},
        {id: "Next", name: "Next Cycle"},
        {id: "Previous", name: "Previous Cycle"},
    ];
    ctrl.calculations = [
        {id: "SUM", name: "Sum"},
        {id: "AVG", name: "Average"}
    ];

    ctrl.models = [
        {id: models.adult, name: "Adult Records"},
        {id: models.paed, name: "Paed Records"},
        {id: models.consumption, name: "Consumption Records"}
    ];
    var newGroup = function () {
        var next_group_number = ctrl.definition.groups.length + 1;
        return {
            cycle: ctrl.cycles[0],
            model: ctrl.models[0],
            aggregation: ctrl.calculations[0],
            selected_consumption_fields: [],
            selected_formulations: [],
            name: "G" + next_group_number
        };
    };

    ctrl.main_regex = /^(G\d) (>|<|(?:<=)|(?:>=)|==|\*) ((?:\d+\.?\d*|\.\d+)|G\d) ?(?: ?(\s|>|<|<=|>=|==) ?((?:\d+\.?\d*|\.\d*)|G\d)?)?$/g;

    ctrl.newGroup = newGroup;
    ctrl.previewDefinition = function (definition) {
        ngDialog.open({
            template: require('./preview.html'),
            plain: true,
            closeByDocument: false,
            controller: ["$scope", "locations", function Ctrl($scope, locations) {
                $scope.locations = locations;
                $scope.update = function (location, cycle) {
                    definition.sample = {cycle: cycle, location: location};
                    metadataService.previewDefinition(definition).then(function (preview) {
                        $scope.groups = preview.groups;
                    })
                }
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
    ctrl.addGroup = function () {
        var group = newGroup();
        ctrl.definition.groups.push(group);
        var lastIndex = ctrl.definition.groups.length - 1;
        ctrl.setFields(lastIndex, group.model)
    };

    ctrl.removeGroup = function (group) {
        ctrl.definition.groups.pop(group);
    };

    ctrl.setFields = function (index, model) {
        if (!model) {
            return;
        }
        if (isAdultOrPaed(model)) {
            ctrl.fields[index] = ctrl.patient_fields;
        }
        if (isAdult(model)) {
            ctrl.formulations[index] = ctrl.formulations_adult;
        }
        if (isPaed(model)) {
            ctrl.formulations[index] = ctrl.formulations_paed;

        }
        if (isConsumption(model)) {
            ctrl.fields[index] = ctrl.consumption_fields;
            ctrl.formulations[index] = ctrl.formulations_consumption;
        }
    };

    function init() {
        metadataService.getAllFields().then(function (data) {
            ctrl.fields = [];
            ctrl.formulations = [];
            ctrl.consumption_fields = data.consumption_fields;
            ctrl.patient_fields = data.patient_fields;
            ctrl.formulations_adult = data.formulations_adult;
            ctrl.formulations_paed = data.formulations_paed;
            ctrl.formulations_consumption = data.formulations_consumption;


            if (ctrl.value) {
                var definition = JSON.parse(ctrl.value);
                for (var index = 0; index < definition.groups.length; index++) {
                    var group = definition.groups[index];
                    ctrl.setFields(index, group.model);
                }
                ctrl.definition = definition;

            } else {
                ctrl.definition = {type: ctrl.testTypes[0], operatorConstant: 1};
                ctrl.definition.groups = [];
                ctrl.addGroup();
                ctrl.addGroup();
            }
        });
    }

    ctrl.reset = function () {
        ctrl.definition = {type: ctrl.testTypes[0], operatorConstant: 1.0};
        ctrl.definition.groups = [];
        ctrl.addGroup();
        ctrl.addGroup();
    };

    init();

    return ctrl;
}];