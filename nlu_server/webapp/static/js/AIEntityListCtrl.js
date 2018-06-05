
var appControllers = angular.module('app.aientitylistctrl', []);

appControllers.controller('AIEntityListCtrl',
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

			function loadData() {
				$http({
					method: 'POST',
					url: './ai_entity/entity_list',
					data: { "admin_id": "40w9dse0277455f634fw40439sd" }
				}).then(function successCallback(response) {
					console.log(response);
					var editData = response.data;

					$scope.entity_list = editData.entities;

				}, function errorCallback(response) {
					
				});

			}


		}]);