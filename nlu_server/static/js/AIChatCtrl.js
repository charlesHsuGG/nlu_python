
var appControllers = angular.module('app.aichatctrl', []);

appControllers.controller('AIChatCtrl', 
		['$scope', '$http', 'MercueRequests', '$state','ModalService',
		 function ($scope, $http, MercueRequests,$state,ModalService){

           
            
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
			}
		console.log("chat ctrl...");
}]);