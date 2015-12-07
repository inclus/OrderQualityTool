angular.module('dashboard').controller('MainChecksController', ['$scope', '$http',
    function($scope, $http) {
        $scope.tests = [{
            "url": "orderFormFreeOfGaps",
            "desc": "Order Form Is Free of Gaps",
            "hasRegimen": false
        }, {
            "url": "orderFormFreeOfNegativeNumbers",
            "desc": "Order Form Is Free of Negative Numbers",
            "hasRegimen": true
        }, {
            "url": "differentOrdersOverTime",
            "desc": "Did the facility submit different orders over time",
            "hasRegimen": true
        }, {
            "url": "closingBalance",
            "desc": "Does Closing balance of one cycle = Opening balance from following one?",
            "hasRegimen": true
        }];
        $http.get('/api/regimens').then(function(response) {
            $scope.regimens = _.map(response.data.values, function(item) {
                return {
                    name: item.formulation
                };
            });
            $scope.selectedRegimen = $scope.regimens[0];
        });
        $scope.selectedTest = $scope.tests[0];
        var update = function(start, end) {
            console.log('updating', start, end);
            var test = $scope.selectedTest.url;
            var regimen = undefined;
            if ($scope.selectedRegimen) {
                regimen = $scope.selectedRegimen.name;
            }
            $http.get('/api/test/' + test, {
                params: {
                    start: start,
                    end: end,
                    regimen: regimen
                }
            }).then(function(response) {
                var values = response.data.values;
                $scope.options = {
                    data: values,
                    dimensions: {
                        cycle: {
                            axis: 'x',
                            type: 'line'
                        },
                        no: {
                            axis: 'y',
                            type: 'line',
                            name: 'No',
                            dataType: 'numeric',
                            displayFormat: d3.format(".1f")
                        },
                        yes: {
                            axis: 'y',
                            type: 'line',
                            name: 'Yes',
                            dataType: 'numeric',
                            displayFormat: d3.format(".1f")
                        },
                        not_reporting: {
                            axis: 'y',
                            type: 'line',
                            name: 'Not Reporting',
                            dataType: 'numeric',
                            displayFormat: d3.format(".1f")
                        }
                    }
                };
                $scope.colors = ["#42BE73"];
            });
        };
        $scope.$watch('startCycle', function(start) {
            if (start && $scope.selectedTest) {
                update($scope.startCycle, $scope.endCycle);
            }

        }, true);

        $scope.$watch('endCycle', function(end) {
            if (end && $scope.selectedTest) {
                update($scope.startCycle, $scope.endCycle);
            }

        }, true);

        $scope.$watch('selectedTest', function(test) {
            if (test) {
                update($scope.startCycle, $scope.endCycle);
            }

        }, true);

        $scope.$watch('selectedRegimen', function(regimen) {
            if (regimen) {
                update($scope.startCycle, $scope.endCycle);
            }

        }, true);
    }
]);