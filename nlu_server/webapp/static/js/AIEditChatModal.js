'use strict';
var appControllers = angular.module('app.aieditchatmodalctrl', []);

appControllers.controller('AIEditChatModalCtrl',['$scope', '$http','$window' ,'close','MercueRequests','DTOptionsBuilder' ,
function ($scope,$http,$window,close,MercueRequests,DTOptionsBuilder){
	 
	console.log("call editchat...");
	$scope.sendData = {};
	init();
  
	
	function init()    {

		
	}

	$scope.close = function(result) {
		$scope.sendData.slot_list = $scope.slot_list;
		$scope.sendData.intent_ranking_list = $scope.intent_ranking_list;
		console.log( $scope.sendData);
			if(result == "cancel"){
				close("cancel", 500);
			}else{
				close("", 500);
			}
			

	};



}]);