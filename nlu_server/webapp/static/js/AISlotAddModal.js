'use strict';
var appControllers = angular.module('app.aislotaddmodalctrl', []);

appControllers.controller('aiSlotAddModalCtrl',['$scope', '$http','$window' ,'close','MercueRequests','DTOptionsBuilder' ,function ($scope,$http,$window,close,MercueRequests,DTOptionsBuilder){
	 
	console.log("call slotCtrlctrl...");
	$scope.promptList = [];
	$scope.sendData = {};
	$scope.sendData.required = false;
	init();
  
	
	function init()    {
		var dataPost = {};
		dataPost.admin_id = "40w9dse0277455f634fw40439sd";
		//dataPost.model_dir = "/opt/nfs/nlu_system_data/models/system/system_model";
		$http({
			method: 'POST',
			url: './ai_entity/entity_list',
			data: dataPost
		}).then(function successCallback(response) {

			console.log(response.data);
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
		$scope.sendData.prompt = $scope.promptList;
		console.log( $scope.sendData);
			if(result == "cancel"){
				close("cancel", 500);
			}else{
				close($scope.sendData, 500);
			}
			

	};



}]);