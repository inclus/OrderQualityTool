angular.module('dashboard').controller('WebBasedRateController', ['$scope', 'ReportService',
    function($scope, ReportService) {

        var update = function(start, end) {
            ReportService.getDataForTest('orderType', {
                start: start,
                end: end
            }).then(function(data) {

                var values = data.values;
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