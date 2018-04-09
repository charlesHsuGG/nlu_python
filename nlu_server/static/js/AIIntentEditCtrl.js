'use strict';
var appControllers = angular.module('app.aiintenteditctrl', []);

appControllers.controller('aiIntentEditCtrl',['$http','$scope', '$state', 'MercueRequests','DTOptionsBuilder','ModalService'
	,function ($http,$scope,$state,MercueRequests,DTOptionsBuilder,ModalService){

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

		if($scope.currentUtterance == "" || $scope.currentUtterance == null){
			return
		};
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
		if($scope.currentResponse == "" || $scope.currentResponse == null){
			return
		};

		console.log("click");
		var response = {};
		response.prompt_text = 	$scope.currentResponse ;
		response.action_type = 	"utter" ;
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
		console.log($scope.utterancesList.length);
		if($scope.utterancesList.length  == 0  ){
			alert("請新增例句");
			return
		}else if($scope.slotsList.length  == 0  ){
			alert("請新增關鍵字欄位");
			return
		}else if($scope.responseList.length  == 0  ){
			alert("請新增回應句");
			return
		}


		var sendUtterances = [];
		console.log($scope.name);
		console.log($scope.utterancesList);
		angular.forEach($scope.utterancesList, function(value, key) {
			console.log(value.utterances);
			sendUtterances.push(value.utterances);
		  });
		
		console.log($scope.slotsList);
		console.log($scope.confirmText);
		console.log($scope.cancelText);
		var confirm_prompt = {};
		confirm_prompt.prompt_text = $scope.confirmText;
		confirm_prompt.action_type = "utter";

		var cancel_prompt = {};
		cancel_prompt.prompt_text = $scope.cancelText;
		cancel_prompt.action_type = "utter";

		var sendData = {};
		sendData.intent  = $scope.name;
		sendData.sentences =  sendUtterances;
		sendData.entities = $scope.slotsList;
		sendData.confirm_prompt = confirm_prompt;
		sendData.cancel_prompt = cancel_prompt;
		sendData.response_prompt = $scope.responseList;




		console.log(sendData);
		$http({
			method: 'POST',
			url: './ai_intent/entity_save',
			data:  sendData
		}).then(function successCallback(response) {
			console.log(response);
		}, function errorCallback(response) {
			console.log(response);
		});





	}


}]);

