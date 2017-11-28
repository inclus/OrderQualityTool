module.exports = ["$scope", "$http", function ($scope, $http) {
    var ctrl = this;
    ctrl.definition = {};
    $http.get("/api/fields/consumption").then(function (data) {
        ctrl.consumption_fields = data.data.values;
    })

    $http.get("/api/fields/patients").then(function (data) {
        ctrl.patient_fields = data.data.values;
    })

    $http.get("/api/formulations").then(function (data) {
        ctrl.formulations = data.data.values;
    })
    var newGroup = function () {
        return { selected_consumption_fields: [], selected_formulations: [] };
    };
    ctrl.definition.groups = [newGroup()];
    ctrl.addGroup = function () {
        ctrl.definition.groups.push(newGroup());
    };
}];

