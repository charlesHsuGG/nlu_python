
var appControllers = angular.module('app.aiarticlelistctrl', []);

appControllers.controller('AIArticleListCtrl',
	['$scope', '$http', 'MercueRequests', '$state',
		function ($scope, $http, MercueRequests, $state) {

			console.log("list ctrl...");
			$scope.admin_id = "40w9dse0277455f634fw40439sd";
    		$scope.model_id = "024a140e177851ea83a36ef0ed9b1ddd";
			init();
			function init() {
				loadData();
			}

			$scope.addArticle = function () {
				console.log("click");
				$state.go("page", { page: "ai_article" });
			}

			$scope.editArticle = function (index) {
				window.location.href = "/ai/#/ai_article/?"+$scope.article_list[index].article_id;
			}

			$scope.deleteArticle = function (index) {
				console.log("click");
				$http({
					method: 'POST',
					url: './ai_entity/article_delete',
					data: { "article_id": $scope.article_list[index].article_id }
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
					url: './ai_entity/article_list',
					data: { "admin_id": $scope.admin_id,
						"model_id":$scope.model_id }
				}).then(function successCallback(response) {
					console.log(response);
					var editData = response.data;

					$scope.article_list = editData.article_list;

				}, function errorCallback(response) {
					
				});

			}


		}]);