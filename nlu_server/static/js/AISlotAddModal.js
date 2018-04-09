'use strict';
var appControllers = angular.module('app.aislotaddmodalctrl', []);

appControllers.controller('aiSlotAddModalCtrl',['$scope', '$http','$window' ,'close','MercueRequests','DTOptionsBuilder' ,function ($scope,$http,$window,close,MercueRequests,DTOptionsBuilder){
	 
	console.log("call slotCtrlctrl...");
	$scope.promptList = [];
	init();
  
	
	function init()    {
		setTimeout(function(){
		 
		},250);
		
	}
	$scope.addPrompt = function(){
		console.log($scope.sendData.prompt);
		var prompt = {};
		prompt.prompt = $scope.sendData.prompt;
		$scope.romptList.push(prompt);
		$scope.sendData.prompt = "";
		console.log(promptList);
	}
	
	$scope.close = function(result) {
		console.log( $scope.sendData);
			if(result == "cancel"){
				close("cancel", 500);
			}else{
				close($scope.sendData, 500);
			}
			

	};



}]);