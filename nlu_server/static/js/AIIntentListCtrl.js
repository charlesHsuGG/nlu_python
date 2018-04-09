
var appControllers = angular.module('app.aiintentlistctrl', []);

appControllers.controller('AiIntentListCtrl',
	['$scope', '$http', 'MercueRequests', '$state',
		function ($scope, $http, MercueRequests, $state) {

			console.log("list ctrl...");
			init();
			function init() {
				$http({
					method: 'POST',
					url: './ai_intent/intent_list',
					data: {"bot_id":"be090fcbc28ba19ac835879c36f861f4"}
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