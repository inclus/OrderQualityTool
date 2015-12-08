angular.module('dashboard').controller('WebBasedRateController', ['$scope', '$http',
    function($scope, $http) {

        var update = function(start, end) {
            $http.get('/api/test/orderType', {
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
                        web: {
                            axis: 'y',
                            type: 'line',
                            name: 'Web',
                            dataType: 'numeric',
                            displayFormat: d3.format(".1f")
                        },
                        paper: {
                            axis: 'y',
                            type: 'line',
                            name: 'Paper',
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