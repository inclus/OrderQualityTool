angular.module('dashboard').controller('HomeController', ['$scope', '$stateParams', '$http', '$httpParamSerializer',
    function($scope, $stateParams, $http, $httpParamSerializer) {

        $scope.displayCycle = function(cycle) {
            return "CYCLE " + cycle.number + " '" + cycle.year;
        };
        $scope.bestPerforming = 'District';
        $scope.selectBest = function(name) {
            $scope.bestPerforming = name;
        };

        $scope.worstPerforming = 'District';
        $scope.selectWorst = function(name) {
            $scope.worstPerforming = name;
        };
        $http.get('/api/cycles').then(function(response) {
            $scope.cycles = response.data.values;
            $scope.startCycle = $scope.cycles[6 - 1];
            $scope.endCycle = $scope.selectedCycle = response.data.most_recent_cycle;
        });

        $scope.$watch('startCycle', function(start) {
            if (start) {
                var pos = _.findIndex($scope.cycles, function(item) {
                    return item == start;
                });
                $scope.endCycles = $scope.cycles.slice(0, pos + 1);
            }

        }, true);

        function downloadURL(url, name) {
            var link = document.createElement("a");
            link.download = name;
            link.href = url;
            link.click();
        }

        $scope.downloadBest = function() {
            var query = $httpParamSerializer({
                level: $scope.bestPerforming,
                cycle: $scope.selectedCycle
            });
            var url = "/api/test/ranking/best/csv?" + query;
            downloadURL(url, 'best.csv');
        }

        $scope.downloadWorst = function() {
            var query = $httpParamSerializer({
                level: $scope.worstPerforming,
                cycle: $scope.selectedCycle
            });
            var url = "/api/test/ranking/worst/csv?" + query;
            downloadURL(url, 'worst.csv');
        }

        var updateWorstList = function() {
            $http.get('/api/test/ranking/worst', {
                params: {
                    level: $scope.worstPerforming,
                    cycle: $scope.selectedCycle
                }
            }).then(function(response) {
                $scope.worstDistricts = response.data.values;
            });
        };

        var updateBestList = function() {
            $http.get('/api/test/ranking/best', {
                params: {
                    level: $scope.bestPerforming,
                    cycle: $scope.selectedCycle
                }
            }).then(function(response) {
                $scope.bestDistricts = response.data.values;
            });
        };

        $scope.$watch('selectedCycle', function(cycle) {
            if (cycle) {
                updateWorstList();
                updateBestList();
            }
        });

        $scope.$watch('bestPerforming', function() {
            updateBestList();
        });


        $scope.$watch('worstPerforming', function() {
            updateWorstList();
        });

        $scope.currentTest = $stateParams.name;
        var templates = {
            "reportingRate": "/static/views/reporting_rate.html",
            "webVsPaper": "/static/views/web_vs_paper.html",
            "guidlineAdherenceRate": "/static/views/guidlineAdherenceRate.html",
            "addTests": "/static/views/addTests.html",
        };

        $scope.template = templates[$scope.currentTest];

        $http.get('/api/test/metrics').then(function(response) {
            var web = response.data.webBased;
            var reporting = response.data.webBased;
            $scope.tests = [{
                name: "reportingRate",
                description: "Reporting Rate",
                metric: reporting + "%"
            }, {
                name: "webVsPaper",
                description: "Web VS Paper Reporting",
                metric: web + "%"
            }, {
                name: "guidlineAdherenceRate",
                description: "GuideLine Adherence Rate",
                metric: web + "%"
            }];
        });
    }
])