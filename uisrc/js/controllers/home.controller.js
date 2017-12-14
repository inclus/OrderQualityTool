angular.module("dashboard").controller("HomeController", ["$scope", "ReportService", "$httpParamSerializer", "NgTableParams",
    function($scope, ReportService, $httpParamSerializer, NgTableParams) {
        $scope.formulation = "TDF/3TC/EFV";
        $scope.isAdmin = false;
        ReportService.getAdminStatus().then(function(data){
            $scope.isAdmin = data.is_admin;
        });

        ReportService.getFilters().then(function(data){
            $scope.districts = data.districts;
            $scope.districts.unshift({"district": "All Districts"});
            $scope.ips = data.ips;
            $scope.ips.unshift({"ip": "All IPs"});
            $scope.warehouses = data.warehouses;
            $scope.warehouses.unshift({"warehouse": "All Warehouses"});

            $scope.selectedIp = $scope.ips[0];
            $scope.selectedDistrict = $scope.districts[0];
            $scope.selectedWarehouse = $scope.warehouses[0];
        });

        $scope.displayCycle = function(cycle) {
            return "CYCLE " + cycle.number + " '" + cycle.year;
        };

        $scope.selectBest = function(name) {
            $scope.bestPerforming = name;
        };

        $scope.selectWorst = function(name) {
            $scope.worstPerforming = name;
        };
        ReportService.getCycles().then(function(data) {
            $scope.cycles = data.values;
            $scope.startCycle = $scope.cycles[6 - 1];
            $scope.endCycle = $scope.selectedCycle = data.most_recent_cycle;
        });

        $scope.$watch("startCycle", function(start) {
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
            downloadURL(url, "best.csv");
        };

        $scope.downloadWorst = function() {
            var query = $httpParamSerializer({
                level: $scope.worstPerforming,
                cycle: $scope.selectedCycle
            });
            var url = "/api/test/ranking/worst/csv?" + query;
            downloadURL(url, "worst.csv");
        };

        var updateWorstList = function() {
            ReportService.getWorstRankings($scope.worstPerforming, $scope.selectedCycle, $scope.formulation).then(function(data) {
                $scope.worstTableParams = new NgTableParams({
                    page: 1,
                    count: 10
                }, {
                    filterDelay: 0,
                    counts: [],
                    dataset: data.values
                });
            });
        };

        var updateBestList = function() {
            ReportService.getBestRankings($scope.bestPerforming, $scope.selectedCycle, $scope.formulation).then(function(data) {
                $scope.bestTableParams = new NgTableParams({
                    page: 1,
                    count: 10
                }, {
                    filterDelay: 0,
                    counts: [],
                    dataset: data.values
                });
            });
        };

        $scope.$watch("selectedCycle", function(cycle) {
            console.log("selected the cycle", cycle);
            if (cycle) {
                updateWorstList();
                updateBestList();
            }
        });

        $scope.$watch("bestPerforming", function() {
            updateBestList();
        });

        $scope.$watch("worstPerforming", function() {
            updateWorstList();
        });
        var setupMetrics = function(guidelineType){
          ReportService.getMetrics(guidelineType, $scope.selectedDistrict, $scope.selectedIp, $scope.selectedWarehouse).then(function(data) {
            $scope.webRate = data.webBased;
            $scope.reportingRate = data.reporting;
            $scope.adherenceRate = data.adherence;
          });
        };

        $scope.$on("GUIDELINE_TYPE", function(event, data) { setupMetrics(data); });

        setupMetrics();

        $scope.$watchGroup(["selectedIp", "selectedWarehouse", "selectedDistrict"], function(data){
            console.log(data, "changes -------------------");
            if(data[0] && data[1] && data[2]){
              setupMetrics();
            }
        });
        ReportService.getRankingsAccess().then(function(data) {
          $scope.rankingLevels = data.values;
          $scope.bestPerforming = $scope.rankingLevels[0];
          $scope.worstPerforming = $scope.rankingLevels[0];
        });
    }
]);
