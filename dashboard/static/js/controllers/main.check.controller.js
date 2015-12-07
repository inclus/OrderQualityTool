angular.module('dashboard').controller('MainChecksController', ['$scope', '$http', 'NgTableParams',
    function($scope, $http, NgTableParams) {
        $scope.tests = [{
            "url": "orderFormFreeOfGaps",
            "desc": "NO BLANKS: If the facility reported, is the whole order form free of blanks?",
            "hasRegimen": false,
            "hasChart": true,
            "testNumber": 3,
            "template": "/static/views/chart.html"
        }, {
            "url": "facilitiesMultiple",
            "desc": "DUPLICATE ORDERS: Facilities that submitted more than one order over the cycle",
            "hasRegimen": false,
            "hasChart": false,
            "testNumber": 4,
            "template": "/static/views/table.html"
        }, {
            "url": "orderFormFreeOfNegativeNumbers",
            "desc": "NO NEGATIVES: Is the order free of negative numbers?",
            "hasRegimen": true,
            "hasChart": true,
            "testNumber": 5,
            "template": "/static/views/chart.html"
        }, {
            "url": "differentOrdersOverTime",
            "desc": "NON-REPEATING ORDERS: Does the facility avoid repeating the same orders in consecutive cycles?",
            "hasRegimen": true,
            "hasChart": true,
            "testNumber": 7,
            "template": "/static/views/chart.html"
        }, {
            "url": "closingBalance",
            "desc": "Does Opening  balance of the cycle = Closing balance from the previous one?",
            "hasRegimen": true,
            "hasChart": true,
            "testNumber": 8,
            "template": "/static/views/chart.html"
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
            if ($scope.selectedTest.hasChart) {
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
            } else {
                var test = $scope.selectedTest.url;

                $http.get('/api/test/' + test, {
                    params: {
                        start: start,
                        end: end
                    }
                }).then(function(response) {
                    var values = response.data.values;
                    $scope.tableParams = new NgTableParams({
                        page: 1, // show first page
                        count: 10 // count per page
                    }, {
                        filterDelay: 0,
                        data: values
                    });
                });
            }

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