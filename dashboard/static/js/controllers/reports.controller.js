angular.module('reports').controller('ReportsController', ['$scope', 'ReportService', 'DTOptionsBuilder',
    function($scope, ReportService, DTOptionsBuilder) {

        ReportService.getFilters().then(function(data) {
            $scope.filters = data;
        });
        $scope.selectedFilter = {};
        $scope.dtOptions = DTOptionsBuilder.newOptions()
            .withOption('scrollX', '100%')
            .withOption('scrollCollapse', true)
            .withOption('bLengthChange', false)
            .withOption('paging', true)
            .withFixedColumns({
                leftColumns: 4,
                rightColumns: 0
            });
        $scope.formulations = [{
            name: "TDF/3TC/EFV (Adult)",
            value: "TDF/3TC/EFV"
        }, {
            name: "ABC/3TC (Paed)",
            value: "ABC/3TC"
        }, {
            name: "EFV200 (Paed)",
            value: "(EFV) 200mg"
        }];
        var tests = [{
            'test': 'REPORTING',
            'display': 'REPORTING',
            'formulation': false
        }, {
            'test': 'WEB_BASED',
            'display': 'WEB/PAPER',
            'formulation': false
        }, {
            'test': 'guidelineAdherenceAdult lL',
            'display': 'Adult 1L',
            'formulation': false
        }, {
            'test': 'guidelineAdherenceAdult 2L',
            'display': 'Adult 2L',
            'formulation': false
        }, {
            'test': 'guidelineAdherencePaed 1L',
            'display': 'Adult 2L',
            'formulation': false
        }, {
            'test': 'OrderFormFreeOfGaps',
            'display': 'Blanks',
            'formulation': false
        }, {
            'test': 'MULTIPLE_ORDERS',
            'display': '>1 Order',
            'formulation': false
        }, {
            'test': 'orderFormFreeOfNegativeNumbers',
            'display': 'Negatives',
            'formulation': true
        }, {
            'test': 'consumptionAndPatients',
            'display': 'Cons. & Patients',
            'formulation': true
        }, {
            'test': 'differentOrdersOverTime',
            'display': 'Repeat Ord.',
            'formulation': true
        }, {
            'test': 'closingBalanceMatchesOpeningBalance',
            'display': 'Open/ Close',
            'formulation': true
        }, {
            'test': 'stableConsumption',
            'display': 'Cons. Stable',
            'formulation': true
        }, {
            'test': 'warehouseFulfilment',
            'display': 'Fulfillment',
            'formulation': true
        }, {
            'test': 'stablePatientVolumes',
            'display': 'Patient Stability',
            'formulation': true
        }, {
            'test': 'nnrtiCurrentAdults',
            'display': 'Adult NRTI',
            'formulation': false
        }, {
            'test': 'nnrtiCurrentPaed',
            'display': 'PAED NRTI',
            'formulation': false
        }, {
            'test': 'nnrtiNewAdults',
            'display': 'N. Adult NRTI',
            'formulation': false
        }, {
            'test': 'nnrtiNewPaed',
            'display': 'N. PAED NRTI',
            'formulation': false
        }];
        $scope.tests = tests;
        var calculateTotal = function(name) {
            var size = $scope.scores.length;
            var count = _.countBy($scope.scores, name);
            var percentage = (count.Pass / size) * 100;
            if (isNaN(percentage)) {
                return 0;
            } else {
                return percentage;
            }

        };
        $scope.cleanFormulation = function(name) {
            var map = {
                "TDF/3TC/EFV": "TDF/3TC/EFV",
                "EFV": "EFV",
                "EFV) 200mg [Pack 90]": "(EFV) 200mg [Pack 90]",
                "ABC/3TC": "ABC/3TC",
                "(EFV) 200mg [Pack 90]": "(EFV) 200mg [Pack 90]",
            }
            var newName = map[name];
            if (!newName) {
                return name;
            }
            return newName;
        };
        var cleanScore = function(score) {
            var map = {
                "YES": "Pass",
                "NO": "Fail",
                "NOT_REPORTING": "N/A"
            }
            var newScore = map[score];
            if (!newScore) {
                return "N/A"
            }
            return newScore;
        }
        var cleanupData = function(data) {
            $scope.scores = _.map(data.results, function(item) {
                var cleanedUpScore = {
                    "name": item.facility.name,
                    "warehouse": item.facility.warehouse,
                    "ip": item.facility.ip,
                    "district": item.facility.district
                };
                _.forEach(tests, function(test) {
                    var items = _.filter(item.scores, function(score) {
                        if ($scope.selectedFilter.formulation && test.formulation) {
                            return score.test == test.test && $scope.selectedFilter.formulation.value === score.formulation;
                        } else {
                            return score.test == test.test;
                        }

                    });
                    if (items && items.length > 0) {
                        cleanedUpScore[test.test] = cleanScore(items[0].score);
                    } else {
                        cleanedUpScore[test.test] = "N/A";
                    }
                });
                return cleanedUpScore;
            });

            $scope.totals = {};
            _.forEach(tests, function(test) {
                $scope.totals[test.test] = calculateTotal(test.test);
            })
        };
        var updateTable = function() {
            var params = {};
            if ($scope.selectedFilter.ip) {
                params['facility__ip'] = $scope.selectedFilter.ip.pk;
            }

            if ($scope.selectedFilter.district) {
                params['facility__district'] = $scope.selectedFilter.district.pk;
            }

            if ($scope.selectedFilter.warehouse) {
                params['facility__warehouse'] = $scope.selectedFilter.warehouse.pk;
            }

            if ($scope.selectedFilter.cycle) {
                params['cycle'] = $scope.selectedFilter.cycle.cycle;
            }
            ReportService.getScores(params).then(cleanupData);
        };

        $scope.updateTable = updateTable;
        updateTable();



    }
]);