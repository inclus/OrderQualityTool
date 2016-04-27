angular.module('dashboard').controller('ReportingRateController', ['$scope', 'ReportService',
    function($scope, ReportService) {
        var setUpScope = function(data) {
                var values = data.values;
                $scope.options = {
                    data: values,
                    chart: {
                        legend: {
                          position: 'right'
                        },

                        grid: {
                            y: {
                                  show: true
                            }
                        },
                        axis: {
                            y: {
                                max: 100,
                                min: 0,
                                tick: {
                                  count: 5
                                },
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
                            color: '#27ae60',
                            dataType: 'numeric',
                            displayFormat: d3.format(".1f")
                        },
                        not_reporting: {
                            axis: 'y',
                            type: 'line',
                            name: 'Not Reporting',
                            color: 'Red',
                            dataType: 'numeric',
                            displayFormat: d3.format(".1f")
                        }
                    }
                };
            };

        var update = function(start, end) {
            ReportService.getDataForTest('submittedOrder', {
                start: start,
                end: end
            }).then(setUpScope);
        };

        var updateWithLocation = function(start, end) {
            ReportService.getDataForTest('submittedOrder', {
                start: start,
                end: end,
                ip: $scope.selectedIp.ip,
                warehouse: $scope.selectedWarehouse.warehouse,
                district: $scope.selectedDistrict.district
            }).then(setUpScope);
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

        $scope.$watchGroup(['selectedIp', 'selectedWarehouse', 'selectedDistrict'], function(data){
            if(data[0] && data[1] && data[2]){
                updateWithLocation($scope.startCycle, $scope.endCycle);
            }
        });
    }
]);
