angular.module('dashboard').controller('GuidelineAdherenceController', ['$scope', 'ReportService',
    function($scope, ReportService) {
        $scope.guidelineType = 'Adult 1L';
        var update = function(start, end) {
            ReportService.getDataForTest('guidelineAdherence', {
                start: start,
                end: end,
                regimen: $scope.guidelineType
            }).then(function(data) {
                var values = data.values;
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
            if (start) {
                update($scope.startCycle, $scope.endCycle);
            }

        }, true);

        $scope.$watch('guidelineType', function(guidelineType) {
            if (guidelineType) {
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