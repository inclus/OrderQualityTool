var previewController = function (definition) {
    return ["$scope", "locations", "metadataService", function Ctrl($scope, locations, metadataService) {
        $scope.locations = locations;
        $scope.update = function (location, cycle) {
            definition.sample = {cycle: cycle, location: location};
            metadataService.previewDefinition(definition).then(function (preview) {
                $scope.groups = preview.groups;
            });
        };
        if (locations.length > 0) {
            $scope.location = locations[0];
            $scope.cycle = locations[0].cycles[0];
            $scope.update($scope.location, $scope.cycle);
        }
    }];
};

var previewService = ["ngDialog", "metadataService", function (ngDialog, metadataService) {
    var self = this;

    self.show = function (definition) {

        ngDialog.open({
            template: require("./test.definition.preview.html"),
            plain: true,
            closeByDocument: false,
            controller: previewController(definition),
            resolve: {
                locations: function getLocations() {
                    return metadataService.getLocations(definition);
                }
            }
        });
    };

    return self;
}];

module.exports = previewService;