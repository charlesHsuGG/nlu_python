'use strict';
var appControllers = angular.module('app.aieditchatmodalctrl', []);

appControllers.controller('AIEditChatModalCtrl',['$scope', '$http','$window' ,'close','MercueRequests','DTOptionsBuilder' ,
function ($scope,$http,$window,close,MercueRequests,DTOptionsBuilder){
	 
	console.log("call editchat...");
	$scope.promptList = [];
	$scope.sendData = {};
	init();
  
	
	function init()    {

		
	}

	$scope.close = function(result) {
		$scope.sendData.prompt = $scope.promptList;
		console.log( $scope.sendData);
			if(result == "cancel"){
				close("cancel", 500);
			}else{
				close("", 500);
			}
			

	};



}]);