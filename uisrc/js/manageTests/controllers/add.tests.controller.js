module.exports = ["$scope", "$http", "$q", function ($scope, $http, $q) {
    var ctrl = this;

    var newGroup = function () {
        return { selected_consumption_fields: [], selected_formulations: [] };
    };

    ctrl.addGroup = function () {
        ctrl.definition.groups.push(newGroup());
    };
    $q.all([$http.get("/api/fields/consumption"), $http.get("/api/fields/patients"), $http.get("/api/formulations")]).then(
        function (data) {
            ctrl.consumption_fields = data[0].data.values;
            ctrl.patient_fields = data[1].data.values;
            ctrl.formulations = data[2].data.values;

            if (ctrl.value) {
                ctrl.definition = JSON.parse(ctrl.value);
            } else {
                ctrl.definition = {};
                ctrl.definition.groups = [newGroup()];
            }
        });

}];

