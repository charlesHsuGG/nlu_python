
var appControllers = angular.module('app.aiintentlistctrl', []);

appControllers.controller('AiIntentListCtrl',
	['$scope', '$http', 'MercueRequests', '$state',
		function ($scope, $http, MercueRequests, $state) {

			console.log("list ctrl...");
			$scope.admin_id = "40w9dse0277455f634fw40439sd";
    		$scope.model_id = "024a140e177851ea83a36ef0ed9b1ddd";
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
			$scope.train = function () {
				$http({
					method: 'POST',
					url: './train',
					data: { "admin_id": $scope.admin_id,
							"model_id":$scope.model_id  }
				}).then(function successCallback(response) {
					console.log(response);
					alert("訓練完成");
				}, function errorCallback(response) {
					console.log(response);
				});
			}
			function loadData() {
				$http({
					method: 'POST',
					url: './ai_intent/intent_list',
					data: { "admin_id": $scope.admin_id,
							"model_id":$scope.model_id  }
				}).then(function successCallback(response) {
					console.log(response.data);
					$scope.intent_list = response.data.intent_list;

				}, function errorCallback(response) {
					console.log(response);
				});

			}


		}]);