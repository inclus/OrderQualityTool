module.exports = ["$http", "$q", function ($http, $q) {
    var self = this;
    var parseDjangoResponse = function (response) {
        return response.data.values;
    }

    self.getConsumptionFields = function () {
        return $http.get("/api/fields/consumption").then(parseDjangoResponse);
    }

    self.getPatientFields = function () {
        return $http.get("/api/fields/patients").then(parseDjangoResponse);
    }
    self.getFormulations = function () {
        return $http.get("/api/formulations").then(parseDjangoResponse);
    }
    self.getAllFields = function () {
        return $q.all([self.getConsumptionFields(), self.getPatientFields(), self.getFormulations()]).then(
            function (data) {
                var output = {}
                output.consumption_fields = data[0];
                output.patient_fields = data[1];
                output.formulations = data[2];
                return output
            });
    }

}];