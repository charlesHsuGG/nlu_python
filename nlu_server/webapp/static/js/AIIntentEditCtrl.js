'use strict';
var appControllers = angular.module('app.aiintenteditctrl', []);

appControllers.controller('aiIntentEditCtrl',['$http','$scope', '$state', 'MercueRequests','DTOptionsBuilder','ModalService','$sce'
	,function ($http,$scope,$state,MercueRequests,DTOptionsBuilder,ModalService,$sce){

	console.log("ai intent edit ctrl...");
	$scope.utterancesList = [];
	$scope.slotsList = [];
	$scope.responseList = [];
	$scope.confirmation = true;
	$scope.slotsListDT = DTOptionsBuilder.newOptions()
	$scope.submitText = "送出"
	$scope.selectText = "";
	$scope.editMode = false;

	$scope.popoverIsOpen = [];
	// .withBootstrap()
	// .withDisplayLength(5)
	// .withOption('info', false)
	// .withOption('ordering', false)
	// .withOption('bLengthChange', false)
	// .withOption('searching', false)
	// .withOption('paging', true) 
	// .withDOM('lfrt<"row"<"col-md-4"i><"col-md-8"p>>');

	
	$scope.dynamicPopover = {
		content: 'Hello, World!',
		templateUrl: 'myPopoverTemplate.html',
		title: $scope.selectText
	  };
	 
	 
	  
	init();

	function init()	{
		
		 var url = location.href.toString(); 
		 console.log(url);
		 url = url.split("?");
		 console.log(url[1]);
		 if(url[1] != null){
				console.log("edit mode");		 
				$scope.edit_id = url[1];
				$scope.submitText = "更新"
				$scope.editMode = true;
				loadData();
		 }
		 //設定反白事件
		 
	 
		 


		
	}
 
	//增加例句
	$scope.addUtterances = function(){
		console.log("click");

		if($scope.currentUtterance == "" || $scope.currentUtterance == null){
			return
		};
		var utterances = {};
	 
		utterances.sentence = 	$scope.currentUtterance ;
		var sentenceHtml =  $sce.trustAsHtml( '<span >'+$scope.currentUtterance+ '</span>');
		utterances.sentenceHtml = sentenceHtml;
		$scope.utterancesList.push(utterances);
		$scope.currentUtterance = "";
		setMouseUp();
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
		closeAllPop();
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
			console.log(value.sentence);
			sendUtterances.push(value.sentence);
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
		sendData.bot_id =  "be090fcbc28ba19ac835879c36f861f4";
		
		
		var url = "./ai_intent/intent_save"
		if($scope.editMode == true){
			url = './ai_intent/intent_update'
			sendData.intent_id = $scope.edit_id;
		}



		console.log(sendData);
		$http({
			method: 'POST',
			url: url ,
			data:  sendData
		}).then(function successCallback(response) {
			console.log(response);
			$state.go("page",{page:"ai_intent_list"});

		}, function errorCallback(response) {
			console.log(response);
		});





	}
	function loadData(){
		$http({
			method: 'POST',
			url: './ai_intent/intent_get',
			data: {intent_id:$scope.edit_id}
		}).then(function successCallback(response) {
			console.log(response);
			
			var editData = response.data;
			if(editData.cancel_prompt =! null){
				$scope.cancelText = editData.cancel_prompt.prompt_text;
			}
			if(editData.confirmText =! null){
				$scope.confirmText = editData.confirm_prompt.prompt_text;
			}
			$scope.confirmText = editData.confirm_prompt.prompt_text;
			$scope.responseList = editData.response_prompt;
			$scope.name = editData.intent;
			$scope.utterancesList = editData.sentence;
			$scope.slotsList = 	 editData.entities;
		 
		}, function errorCallback(response) {
			console.log(response);
		});

	}
	$scope.setSlot = function(slot){
		console.log("set");
		console.log($scope.selectPop);
		console.log($scope.utterancesList[$scope.selectPop]);
		console.log($scope.selectText);
		console.log(slot);
		// var myRegExp = new RegExp($scope.selectText, 'g');
		// var sentence = 	$scope.utterancesList[$scope.selectPop].sentence;
		// var tag = '<button class="badge badge-primary">'+'美食'+'</button>';
		// var sentenceHtml =  sentence.replace(myRegExp,tag);
		console.log($scope.utterancesList);
		// sentence = sentence.replace(myRegExp,"")
		console.log(sentence);

		//s$scope.utterancesList[$scope.selectPop].sentence = sentence;
		
	 
		// $scope.utterancesList[$scope.selectPop].sentenceHtml =  $sce.trustAsHtml( '<span >'+sentenceHtml+ '</span>');
		
		console.log($scope.utterancesList.sentenceHtml);
		$scope.$apply();
	}
		
	$scope.closePop = function()   {
	console.log("123");
	closeAllPop();   
		  $scope.$apply();
	}
	
 



	$scope.openPop = function(index){
		closeAllPop();
		$scope.selectPop = index;
		console.log($scope.selectText);
		if($scope.selectText != ""){
			$scope.dynamicPopover = {
				content: '請選擇slot',
				templateUrl: 'myPopoverTemplate.html',
				title: $scope.selectText
				
			  };
			$scope.popoverIsOpen[index] = true ;
			console.log("set true");		 
			$scope.$apply();
		}		 
	

	}


	function setMouseUp(){
		console.log("set");
		setTimeout(function(){ 
			$('#input_text').mouseup(function(e) { 
				console.log("mouse");
				$scope.selectText = "";
				var text=getSelectedText();
				if (text!='') {
				//alert(text) 
				$scope.selectText = text;
				}	
			
			});

		 }, 500);
	}

	function closeAllPop(){
		for(var i = 0;i<$scope.popoverIsOpen.length;i++){
			console.log(i);
			$scope.popoverIsOpen[i] = false;
		}

	}
	function getSelectedText() {
		if (window.getSelection) {
			return window.getSelection().toString();
		} else if (document.selection) {
			return document.selection.createRange().text;
		}
		return ''
	}

}]);

