
var appControllers = angular.module('app.navctrl', []);

appControllers.controller('NavCtrl', 
		['$scope', '$http', 'MercueRequests', '$state',
		 function ($scope, $http, MercueRequests,$state){
$scope.page = 1;

$scope.goPage = function(index){
    console.log("click");
    console.log(index);
    $scope.page = index;
    for (var i = 1 ; i<7;i++){
        console.log(i);
        if( i == index){
        $("#page_"+i).css("color", "darkturquoise");
        }else{
        $("#page_"+i).css("color", "white");
        }
    }

    switch(index){
        case 1:
        $state.go("page",{page:"ai_article"});
        console.log("go page")
        break;
       
        case 2:
        
        $state.go("page",{page:"ai_intent_edit"});
        break
        case 3:

        $state.go("page",{page:"ai_intent_list"});
        break
        case 4:

        $state.go("page",{page:"ai_entity_list"});
        break
        case 5:

        $state.go("page",{page:"ai_chat"});
        break

        case 6:

        $state.go("page",{page:"ai_article_list"});
        break
        
    }
}
 
		console.log("nav ctrl...");
}]);