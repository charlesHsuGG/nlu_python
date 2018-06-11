
var appControllers = angular.module('app.aichatctrl', []);

appControllers.controller('AIChatCtrl', 
		['$scope', '$http', 'MercueRequests', '$state','ModalService',
		 function ($scope, $http, MercueRequests,$state,ModalService){

		   $scope.messageList = [];
 
            
			$scope.editIntent = function(index){
				console.log("edit")
				var msg = $scope.messageList[index];

				ModalService.showModal({
					templateUrl: "/ai/static/views/aichatedit_modal.html",
					controller: "AIEditChatModalCtrl",
					inputs: {
						data:msg
					  },
					preClose: (modal) => { modal.element.modal('hide'); } 
				}).then(function(modal) {
					modal.element.on('hidden.bs.modal', function () {$('.ngmodal').remove(); });
					modal.element.modal();
					modal.close.then(function(data) {
						console.log(data);
						if(data != "cancel"){
							 
						}
					});
				});
			}

			           
            
			$scope.submit = function(){
				 console.log("submit")
				//  var msg = {}
				//  msg.text = $scope.textInput;
				//  msg.sender = "cutomer"
				//  $scope.messageList.push(msg);
				//  $scope.textInput = "";
		 
				 sendData($scope.textInput);
				 $scope.textInput = "";
			}

			$scope.checkBtn = function(message){
				if(message.sender == "admin"){
					return false
				}else{
					return true
				}

			}
			$scope.checkAdmin = function(message){
				console.log(message);
				if(message.sender == "admin"){
					return "angent-text"
				}else{
					return "custom-text"
				}
				
			}
			$scope.checkTextRight = function(message){
				if(message.sender == "admin"){
					return "border-lp"
				}else{
					return "border-rp"
				}
				
			}

			function sendData(text) {
				console.log(text);

				$http({
					method: 'POST',
					url: './chat',
					data: { "admin_id": $scope.admin_id,
					"model_id": $scope.model_id,
					"message": text}
				}).then(function successCallback(response) {
					console.log(response);
					var editData = response.data;

				    var msg = {}
					msg.text = text;
					msg.sender = "cutomer"
					msg.data = editData;
					$scope.messageList.push(msg);
					

					$scope.slot_list = editData.slots;
					$scope.entity_list = editData.entities;
					$scope.intent_ranking_list = editData.intent_ranking;

					var msg = {}
			   		msg.text = editData.bot_response;
					msg.sender = "admin";
					   

					$scope.messageList.push(msg);
				}, function errorCallback(response) {
					
				});

			}

		console.log("chat ctrl...");
}]);