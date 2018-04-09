'use strict';
var appControllers = angular.module('app.aiintenteditctrl', []);

appControllers.controller('aiIntentEditCtrl',['$scope', '$state', 'MercueRequests','DTOptionsBuilder','ModalService'
	,function ($scope,$state,MercueRequests,DTOptionsBuilder,ModalService){

	console.log("ai intent edit ctrl...");
	$scope.utterancesList = [];
	$scope.slotsList = [];
	$scope.responseList = [];
	$scope.confirmation = true;
	$scope.slotsListDT = DTOptionsBuilder.newOptions()
	// .withBootstrap()
	// .withDisplayLength(5)
	// .withOption('info', false)
	// .withOption('ordering', false)
	// .withOption('bLengthChange', false)
	// .withOption('searching', false)
	// .withOption('paging', true) 
	// .withDOM('lfrt<"row"<"col-md-4"i><"col-md-8"p>>');

	init();

	function init()	{
		loadSlots();

	}
	//增加例句
	$scope.addUtterances = function(){
		console.log("click");

		var utterances = {};
		utterances.utterances = 	$scope.currentUtterance ;
		$scope.utterancesList.push(utterances);
		$scope.currentUtterance = ""
	}
	//刪除例句
	$scope.deleteUtterances  = function(index){
		console.log(index);
		console.log($scope.utterancesList);
		if (index  > -1) {
			$scope.utterancesList.splice(index, 1);
		}
	}
	//隱藏顯示例句
	$scope.showHideUtterances  = function(){
		console.log("click");
		$("#utterancesList").toggle();

	}

	//提示字元checkBox
	$scope.confirmationClick  = function(){
		console.log("click");
		$("#confirmation").toggle();

	}
	
	//增加回應
	$scope.addResponse = function(){
		console.log("click");
		var response = {};
		response.response = 	$scope.currentResponse ;
		$scope.responseList.push(response);
		$scope.currentResponse = ""
		console.log("addsuccese")
		console.log($scope.responseList)
	}
	//刪除回應
	$scope.deleteResponse   = function(index){
		console.log(index);
		console.log($scope.responseList);
		if (index  > -1) {
			$scope.responseList.splice(index, 1);
		}
	}
	$scope.addSlots = function(){
		console.log("add")
		ModalService.showModal({
			templateUrl: "/ai/static/views/aislotadd_modal.html",
			controller: "aiSlotAddModalCtrl",
			preClose: (modal) => { modal.element.modal('hide'); } 
		}).then(function(modal) {
			modal.element.on('hidden.bs.modal', function () {$('.ngmodal').remove(); });
			modal.element.modal();
			modal.close.then(function(data) {
				console.log(data);
				if(data != "cancel"){
					$scope.slotsList.push(data);
				}
			});
		});
	}
	$scope.deleteSlots = function(index){
		console.log(index);
		$scope.slotsList.splice(index,1);
	}

	function loadSlots(){

		// var slots ={};
		// slots.prioriry = "1";
		// slots.required = "是";
		// slots.name = "書本名稱";
		// slots.slotType = "書籍資料";
		// slots.prompt = "請問您想租閱的書名是？";
		// $scope.slotsList.push(slots);
		// console.log("push done");


	}


	$scope.submit = function(){
		console.log("submit");
		console.log($scope.name);
		console.log($scope.utterancesList);
		angular.forEach($scope.utterancesList, function(value, key) {
			console.log(value);
		  });
		
		console.log($scope.slotsList);
		console.log($scope.responseText);
		console.log($scope.confirmText);
		console.log($scope.responseList);
		var sendData = {};
		sendData.intent  = $scope.name;
	




	}


}]);

