
var appControllers = angular.module('app.aiintentlistctrl', []);

appControllers.controller('AiIntentListCtrl',
	['$scope', '$http', 'MercueRequests', '$state',
		function ($scope, $http, MercueRequests, $state) {

			console.log("list ctrl...");
			init();
			function init() {
				loadData();
			}

			$scope.addSlots = function () {
				console.log("click");
				$state.go("page", { page: "ai_intent_edit" });
			}
			$scope.editIntent = function (index) {
				window.location.href = "/ai/#/ai_intent_edit/?"+$scope.intent_list[index].intent_id;
			}
			$scope.deleteIntent = function (index) {
				console.log("click");
				$http({
					method: 'POST',
					url: './ai_intent/intent_delete',
					data: { "intent_id": $scope.intent_list[index].intent_id }
				}).then(function successCallback(response) {
					console.log(response);
					loadData();
				}, function errorCallback(response) {
					console.log(response);
				});

			}
			function loadData() {
				$http({
					method: 'POST',
					url: './ai_intent/intent_list',
					data: { "admin_id": "40w9dse0277455f634fw40439sd" }
				}).then(function successCallback(response) {
					console.log(response.data);
					$scope.intent_list = response.data.intent_list;

				}, function errorCallback(response) {
					console.log(response);
				});

			}


		}]);