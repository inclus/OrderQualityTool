angular.module('dashboard').controller('ReportingRateController', ['$scope', '$http',
    function($scope, $http) {
        var update = function(start, end) {
            $http.get('/api/test/submittedOrder', {
                params: {
                    start: start,
                    end: end,
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
                        reporting: {
                            axis: 'y',
                            type: 'line',
                            name: 'Reporting',
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
            if (start) {
                update($scope.startCycle, $scope.endCycle);
            }

        }, true);

        $scope.$watch('endCycle', function(end) {
            if (end) {
                update($scope.startCycle, $scope.endCycle);
            }

        }, true);
    }
]);