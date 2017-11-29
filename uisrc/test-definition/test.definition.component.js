module.exports = ["$scope", "metadataService", function ($scope, metadataService) {
    var ctrl = this;

    var newGroup = function () {
        var next_group_number = ctrl.definition.groups.length + 1;
        return {
            selected_consumption_fields: [],
            selected_formulations: [],
            name: "Group " + next_group_number
        };
    };

    ctrl.addGroup = function () {
        var group = newGroup();
        ctrl.definition.groups.push(newGroup());
    };

    ctrl.removeGroup = function (group) {
        ctrl.definition.groups.pop(group);
    };

    ctrl.setFields = function (index, model) {

        if (model == "Adult Patient Records" || model == "Paed Patient Records") {
            ctrl.fields[index] = ctrl.patient_fields;
        }
        if (model == "Consumption Records") {
            ctrl.fields[index] = ctrl.consumption_fields;
        }
    }

    metadataService.getAllFields().then(function (data) {
        ctrl.fields = [];
        ctrl.consumption_fields = data.consumption_fields;
        ctrl.patient_fields = data.patient_fields;
        ctrl.formulations = data.formulations;


        if (ctrl.value) {
            var definition = JSON.parse(ctrl.value);
            for (var index = 0; index < definition.groups.length; index++) {
                var group = definition.groups[index];
                ctrl.setFields(index, group.model);
            }
            ctrl.definition = definition;

        } else {
            ctrl.definition = {};
            ctrl.definition.groups = [];
            ctrl.addGroup();
            ctrl.definition.cycle = "Current Cycle";
            ctrl.definition.model = "Consumption Records";
        }
    })
}];