'use strict';
var appControllers = angular.module('app.aislotaddmodalctrl', []);

appControllers.controller('aiSlotAddModalCtrl',['$scope', '$http','$window' ,'close','MercueRequests','DTOptionsBuilder' ,function ($scope,$http,$window,close,MercueRequests,DTOptionsBuilder){
	 
	console.log("call slotCtrlctrl...");
	$scope.promptList = [];
	init();
  
	
	function init()    {
		$http({
			method: 'POST',
			url: './ai_intent/entity_get',
			data: {"bot_id":"be090fcbc28ba19ac835879c36f861f4"}
		}).then(function successCallback(response) {
			console.log(response);
		}, function errorCallback(response) {
			console.log(response);
		});

		setTimeout(function(){
		 
		},250);
		
	}
	$scope.addPrompt = function(){
		console.log($scope.sendData.prompt);
		var prompt = {};
		prompt.prompt = $scope.sendData.prompt;
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