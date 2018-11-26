'use strict';
var appControllers = angular.module('app.aislotaddmodalctrl', []);

appControllers.controller('aiSlotAddModalCtrl',['$scope', '$http','$window' ,'close','MercueRequests','DTOptionsBuilder','data' ,function ($scope,$http,$window,close,MercueRequests,DTOptionsBuilder,data){
	 
	console.log("call slotCtrlctrl...");
	$scope.promptList = [];
	$scope.sendData = {};
	$scope.sendData.required = false;
	init();
	$scope.admin_id = "40w9dse0277455f634fw40439sd";
	$scope.model_id = "024a140e177851ea83a36ef0ed9b1ddd";
	
	function init()    {
		console.log(data);
		var dataPost = {};
		dataPost.admin_id = "40w9dse0277455f634fw40439sd";
		if (data.entity_name != null){
			console.log( data.entity_value_list);
			$scope.sendData.entity = data.entity_name;
			if( data.entity_value_list != null){
				$scope.promptList = data.entity_value_list;
			}

		}
		//dataPost.model_dir = "/opt/nfs/nlu_system_data/models/system/system_model";
		// $http({
		// 	method: 'POST',
		// 	url: './ai_entity/entity_list',
		// 	data: dataPost
		// }).then(function successCallback(response) {

		// 	console.log(response.data);
		// 	$scope.entities = response.data.entities;
		// 	$scope.sendData.slotType = 	$scope.entities[0];
		// }, function errorCallback(response) {
		// 	console.log(response);
		// });

		setTimeout(function(){
		 
		},250);
		
	}
	$scope.addPrompt = function(){
		console.log($scope.sendData.entity_value);
		var prompt = {};
		prompt.entity_value = $scope.sendData.entity_value;
		$scope.promptList.push(prompt);
		$scope.sendData.entity_value = "";
		console.log($scope.promptList);
	}
	$scope.deletePrompt = function(index){
	 $scope.promptList.splice(index,1);
	}
	$scope.close = function(result) {
		$scope.sendData.entity_value = $scope.promptList;
		console.log( $scope.sendData);
			if(result == "cancel"){
				close("cancel", 500);
			}else{
				close($scope.sendData, 500);
			}
			

	};



}]);