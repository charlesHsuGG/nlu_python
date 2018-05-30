
var appControllers = angular.module('app.aichatctrl', []);

appControllers.controller('AIChatCtrl', 
		['$scope', '$http', 'MercueRequests', '$state','ModalService',
		 function ($scope, $http, MercueRequests,$state,ModalService){

		   $scope.messageList = [];
		   setData();
		   function setData(){
			   var msg = {}
			   msg.text = "測試"
			   msg.sender = "admin"
			   $scope.messageList.push(msg);
			   $scope.messageList.push(msg);
			   var msg = {}
			   msg.text = "測試"
			   msg.sender = "cutomer"
			   $scope.messageList.push(msg);
			   $scope.messageList.push(msg);
			   console.log("sets");
			   console.log( $scope.messageList);
		   }
            
			$scope.editIntent = function(){
				console.log("edit")
				ModalService.showModal({
					templateUrl: "/ai/static/views/aichatedit_modal.html",
					controller: "AIEditChatModalCtrl",
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
				 var msg = {}
				 msg.text = $scope.textInput;
				 msg.sender = "cutomer"
				 $scope.messageList.push(msg);
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
		console.log("chat ctrl...");
}]);