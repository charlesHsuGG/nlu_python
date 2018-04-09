'use strict';
var appControllers = angular.module('app.aislotaddmodalctrl', []);

appControllers.controller('aiSlotAddModalCtrl',['$scope', '$http','$window' ,'close','MercueRequests','DTOptionsBuilder' ,function ($scope,$http,$window,close,MercueRequests,DTOptionsBuilder){
	 
	console.log("call slotCtrlctrl...");
	init();
  
	
	function init()    {
		setTimeout(function(){
		 
		},250);
		
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