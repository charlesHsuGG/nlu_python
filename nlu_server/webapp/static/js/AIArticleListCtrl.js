
var appControllers = angular.module('app.aiarticlelistctrl', []);

appControllers.controller('AIArticleListCtrl',
	['$scope', '$http', 'MercueRequests', '$state',
		function ($scope, $http, MercueRequests, $state) {

			console.log("list ctrl...");
			init();
			function init() {
				loadData();
			}

			$scope.addSlots = function () {
				console.log("click");
				$state.go("page", { page: "ai_article" });
			}

			$scope.editIntent = function (index) {
				window.location.href = "/ai/#/ai_article/?"+$scope.article_list[index].article_id;
			}

			function loadData() {
				$http({
					method: 'POST',
					url: './ai_entity/article_list',
					data: { "admin_id": "40w9dse0277455f634fw40439sd" }
				}).then(function successCallback(response) {
					console.log(response);
					var editData = response.data;

					$scope.article_list = editData.article_list;

				}, function errorCallback(response) {
					
				});

			}


		}]);