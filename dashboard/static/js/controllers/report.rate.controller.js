angular.module('dashboard').controller('ReportingRateController', ['$scope', 'ReportService',
    function($scope, ReportService) {
        var update = function(start, end) {
            ReportService.getDataForTest('submittedOrder', {
                start: start,
                end: end
            }).then(function(data) {
                var values = data.values;
                $scope.options = {
                    data: values,
                    chart: {
                        axis: {
                            y: {
                                max: 100,
                                min: 0,
                                padding: {
                                    top: 0,
                                    bottom: 0
                                }
                            }
                        }
                    },
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