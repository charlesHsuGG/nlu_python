
var appControllers = angular.module('app.aientitylistctrl', []);

appControllers.controller('AIEntityListCtrl',
	['$scope', '$http', 'MercueRequests', '$state','ModalService',
		function ($scope, $http, MercueRequests, $state,ModalService) {

			console.log("list ctrl...");
			$scope.admin_id = "40w9dse0277455f634fw40439sd";
    		$scope.model_id = "024a140e177851ea83a36ef0ed9b1ddd";
			init();
			function init() {
				loadData();
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
					url: './ai_entity/entity_list',
					data: { "admin_id": $scope.admin_id,
							"model_id": $scope.model_id}
				}).then(function successCallback(response) {
					console.log(response);
					var editData = response.data;

					$scope.entity_list = editData.entities;

				}, function errorCallback(response) {
					
				});

			}

			$scope.addSlots = function(){
				console.log("add")
				ModalService.showModal({
					templateUrl: "/ai/static/views/aislotadd_modal.html",
					controller: "aiSlotAddModalCtrl",
					inputs: {
						data:  {}
					  },
					preClose: (modal) => { modal.element.modal('hide'); } 
				}).then(function(modal) {
					modal.element.on('hidden.bs.modal', function () {$('.ngmodal').remove(); });
					modal.element.modal();
					modal.close.then(function(data) {
						console.log(data);
						if(data != "cancel"){
							addSlotRequest(data);
						}
					});
				});
			}
			$scope.editIntent = function(index){
				console.log(index);
				console.log($scope.entity_list[index].entity_id);
				var id = $scope.entity_list[index].entity_id;
				$http({
					method: 'POST',
					url: './ai_entity/entity_get',
					data: {"entity_id":id}
				}).then(function successCallback(response) {
					console.log(response);
					var resData = response.data;
					console.log(resData);
					ModalService.showModal({
						templateUrl: "/ai/static/views/aislotadd_modal.html",
						controller: "aiSlotAddModalCtrl",
						inputs: {
							data:  resData
						  },
						preClose: (modal) => { modal.element.modal('hide'); } 
					}).then(function(modal) {
						modal.element.on('hidden.bs.modal', function () {$('.ngmodal').remove(); });
						modal.element.modal();
						modal.close.then(function(data) {
							console.log(data);
							if(data != "cancel"){
								// $scope.slotsList.push(data);
								console.log(data);
	
							}
						});
					});


				}, function errorCallback(response) {
					
				});

				
				
			 
			}
	
			function addSlotRequest(data) {
				
				var finalObj = {};
				var sendArray = [];
				var sendObj = {};
				sendObj.entity = data.entity;
				sendObj.entity_value_list = data.entity_value;
				sendArray.push(sendObj);
				finalObj.admin_id = $scope.admin_id;
				finalObj.model_id = $scope.model_id;
				finalObj.entities =  sendArray;
				console.log(finalObj);
				$http({
					method: 'POST',
					url: './ai_entity/entity_save',
					data: finalObj
				}).then(function successCallback(response) {
					console.log(response);
					loadData();

				}, function errorCallback(response) {
					
				});

			}
		}]);