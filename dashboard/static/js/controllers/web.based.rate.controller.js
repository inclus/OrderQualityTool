angular.module('dashboard').controller('WebBasedRateController', ['$scope', '$http',
    function($scope, $http) {

        var update = function(start, end) {
            $http.get('/api/test/webBased', {
                params: {
                    start: start,
                    end: end,
                }
            }).then(function(response) {
                var values = response.data.values;
                $scope.labels = _.map(values, 'cycle');
                var items = _.map(values, 'rate');
                $scope.series = ['Web Based Reporting Rate'];
                $scope.data = [items];
                $scope.options = {
                    scaleOverride: true,
                    scaleSteps: 10,
                    scaleStepWidth: 10,
                    scaleStartValue: 0,
                    scaleLineColor: "#42BE73",
                    strokeColor: "#42BE73",
                };
                $scope.colors = ["#42BE73"];
            });
        };
        $scope.$watch('startCycle', function(start) {
            if (start) {
                update($scope.startCycle.name, $scope.endCycle.name);
            }

        }, true);

        $scope.$watch('endCycle', function(end) {
            if (end) {
                update($scope.startCycle.name, $scope.endCycle.name);
            }

        }, true);
    }
]);