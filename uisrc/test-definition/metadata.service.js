module.exports = ["$http", "$q", function ($http, $q) {
    var self = this;
    var parseDjangoResponse = function (response) {
        return response.data.values;
    };

    var parsePreviewResponse = function (response) {
        return response.data;
    };

    var parseLocationsResponse = function (response) {
        return response.data.locations;
    };

    self.getConsumptionFields = function () {
        return $http.get("/api/fields/consumption").then(parseDjangoResponse);
    };

    self.previewDefinition = function (definition) {
        return $http.post("/api/tests/preview", definition).then(parsePreviewResponse);
    };
    self.getLocations = function (definition) {
        return $http.post("/api/tests/preview/locations", definition).then(parseLocationsResponse);
    };
    self.getPatientFields = function () {
        return $http.get("/api/fields/patients").then(parseDjangoResponse);
    };
    self.getFormulations = function (extra) {
        return $http.get("/api/formulations/" + extra).then(parseDjangoResponse);
    };
    self.getAllFields = function () {
        return $q.all([self.getConsumptionFields(), self.getPatientFields(), self.getFormulations('adult'), self.getFormulations('paed'), self.getFormulations('consumption')]).then(
            function (data) {
                var output = {};
                output.fields_consumption = data[0];
                output.fields_adult = data[1];
                output.fields_paed = data[1];
                output.formulations_adult = data[2];
                output.formulations_paed = data[3];
                output.formulations_consumption = data[4];
                return output
            });
    };

    return self;

}];