angular.module('dashboard').controller('MainChecksController', ['$scope', '$http',
    function($scope, $http) {
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
            "url": "consumptionAndPatients",
            "desc": "CONSUMPTION AND PATIENTS: Do consumption volumes tally with corresponding patient regimen volumes (i.e. they are within 30% of each other)?",
            "hasRegimen": true,
            "hasChart": true,
            "testNumber": 6,
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
        }, {
            "url": "stableConsumption",
            "desc": "STABLE CONSUMPTION: Is total consumption stable from one cycle to the next (i.e. less than 50% growth or decline from one cycle to the next)?",
            "hasRegimen": true,
            "hasChart": true,
            "testNumber": 9,
            "template": "/static/views/chart.html"
        }, {
            "url": "warehouseFulfilment",
            "desc": "WAREHOUSE FULFILMENT: Does volume ordered = volume delivered in following cycle?",
            "hasRegimen": true,
            "hasChart": true,
            "testNumber": 9,
            "template": "/static/views/chart.html"
        }, {
            "url": "stablePatientVolumes",
            "desc": "STABLE PATIENT VOLUMES: Are total patient numbers stable from one cycle to the next?",
            "hasRegimen": true,
            "hasChart": true,
            "testNumber": 9,
            "template": "/static/views/chart.html"
        }];
        $scope.regimens = [{
            name: "TDF/3TC/EFV (Adult)",
            value: "TDF/3TC/EFV"
        }, {
            name: "ABC/3TC (Paed)",
            value: "ABC/3TC"
        }, {
            name: "EFV200 (Paed)",
            value: "(EFV) 200mg"
        }];
        $scope.selectedRegimen = $scope.regimens[0];

        $scope.selectedTest = $scope.tests[0];

    }
]);
angular.module('dashboard').controller('MultipleOrdersController', ['$scope', '$http', 'NgTableParams',
    function($scope, $http, NgTableParams) {
        $http.get('/api/test/facilitiesMultiple').then(function(response) {
            var values = response.data.values;
            $scope.tableParams = new NgTableParams({
                page: 1,
                count: 10
            }, {
                filterDelay: 0,
                data: values
            });
        });
    }
]);
angular.module('dashboard').controller('LineChartController', ['$scope', '$http',
    function($scope, $http) {
        var update = function(start, end) {
            console.log('updating', start, end);

            var test = $scope.selectedTest.url;
            var regimen = undefined;
            if ($scope.selectedRegimen) {
                regimen = $scope.selectedRegimen.value;
            }
            $http.get('/api/test/' + test, {
                params: {
                    start: start,
                    end: end,
                    regimen: regimen
                }
            }).then(function(response) {
                var values = response.data.values;
                $scope.options = {};
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