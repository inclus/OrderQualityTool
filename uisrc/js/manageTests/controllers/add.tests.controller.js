module.exports = ["$scope", "$http", function($scope, $http) {
  console.log("working", "===");
 var ctrl = this;
 $http.get("/api/fields/consumption").then(function (data) {
     ctrl.consumption_fields = data.data.values;
 })

 $http.get("/api/fields/patients").then(function (data) {
     ctrl.patient_fields = data.data.values;
 })

 $http.get("/api/formulations").then(function (data) {
     ctrl.formulations = data.data.values;
 })
}];

