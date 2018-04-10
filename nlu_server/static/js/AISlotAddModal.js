'use strict';
var appControllers = angular.module('app.aislotaddmodalctrl', []);

appControllers.controller('aiSlotAddModalCtrl',['$scope', '$http','$window' ,'close','MercueRequests','DTOptionsBuilder' ,function ($scope,$http,$window,close,MercueRequests,DTOptionsBuilder){
	 
	console.log("call slotCtrlctrl...");
	$scope.promptList = [];
	$scope.sendData = {};
	init();
  
	
	function init()    {
		var dataPost = {};
		dataPost.model_dir = "/opt/nfs/nlu_system_data/models/system/system_model";
		$http({
			method: 'POST',
			url: './ai_entity/slot_get',
			data: dataPost
		}).then(function successCallback(response) {

			console.log(response.data.entities);
			$scope.entities = response.data.entities;
			$scope.sendData.slotType = 	$scope.entities[0];
		}, function errorCallback(response) {
			console.log(response);
		});

		setTimeout(function(){
		 
		},250);
		
	}
	$scope.addPrompt = function(){
		console.log($scope.sendData.prompt);
		var prompt = {};
		prompt.prompt_text = $scope.sendData.prompt;
		prompt.action_type = "utter";
		$scope.promptList.push(prompt);
		$scope.sendData.prompt = "";
		console.log($scope.promptList);
	}
	$scope.deletePrompt = function(index){
	 $scope.promptList.splice(index,1);
	}
	$scope.close = function(result) {
		$scope.sendData.entity_prompt = $scope.promptList;
		console.log( $scope.sendData);
			if(result == "cancel"){
				close("cancel", 500);
			}else{
				close($scope.sendData, 500);
			}
			

	};



}]);