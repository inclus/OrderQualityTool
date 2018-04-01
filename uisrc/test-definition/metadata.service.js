module.exports = ["$http", "$q", function ($http, $q) {
    var self = this;
    var parseDjangoResponse = function (response) {
        return response.data.values;
    };

    var parseTracingResponse = function (response) {
        return response.data;
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

    self.getTracingFormulations = function () {
        return $http.get("/api/tests/tracingformulations").then(parseTracingResponse);
    };

    self.getAllFields = function () {

        return $q.all(
            [
                self.getConsumptionFields(),
                self.getPatientFields(),
                self.getFormulations("adult"),
                self.getFormulations("paed"),
                self.getFormulations("consumption"),
                self.getTracingFormulations()
            ]).then(
            function (data) {
                var output = {};
                output.fieldsConsumption = data[0];
                output.fieldsAdult = data[1];
                output.fieldsPaed = data[1];
                output.formulationsAdult = data[2];
                output.formulationsPaed = data[3];
                output.formulationsConsumption = data[4];
                output.tracingFormulations = data[5];
                return output;
            });
    };

    return self;

}];