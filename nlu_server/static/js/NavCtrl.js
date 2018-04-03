
var appControllers = angular.module('app.navctrl', []);

appControllers.controller('NavCtrl', 
		['$scope', '$http', 'MercueRequests', '$state',
		 function ($scope, $http, MercueRequests,$state){
$scope.goPage = function(index){
    console.log("click");
    console.log(index);
    
    switch(index){
        case 1:
        $state.go("page",{page:"ai_entity"});
        console.log("go page")
        break;
       
        case 2:
        $state.go("page",{page:"ai_intent_edit"});
        break

    }
}
            

		console.log("nav ctrl...");
}]);