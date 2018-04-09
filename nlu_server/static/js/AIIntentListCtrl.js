
var appControllers = angular.module('app.aiintentlistctrl', []);

appControllers.controller('AiIntentListCtrl',
	['$scope', '$http', 'MercueRequests', '$state',
		function ($scope, $http, MercueRequests, $state) {

			console.log("list ctrl...");
			init();
			function init() {
				$http({
					method: 'POST',
					url: './intent_list'
				}).then(function successCallback(response) {
					console.log(response);
				}, function errorCallback(response) {
					console.log(response);
				});

			}

			$scope.addSlots = function () {
				console.log("click");
				$state.go("page", { page: "ai_intent_edit" });
			}




		}]);