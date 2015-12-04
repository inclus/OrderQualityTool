angular.module('dashboard').controller('MainChecksController', ['$scope', '$http',
    function($scope, $http) {
        $scope.selectedTest = 'orderFormFreeOfGaps';
        var update = function(start, end) {
            var test = $scope.selectedTest;
            $http.get('/api/test/' + test, {
                params: {
                    start: start,
                    end: end,
                }
            }).then(function(response) {
                var values = response.data.values;
                console.log(values);
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
    }
]);