'use strict';

var appControllers = angular.module('app.mainctrl', []);

appControllers.controller('mainCtrl',['$rootScope', '$scope', '$state', 'MercueRequests' 
                                      ,function ($rootScope,$scope,$state,MercueRequests){
   

    
 
    //確認連線狀態
   
    console.log("main page ctrl...");
	
	
	function init()
	{
 
		setTimeout(function(){
			updateContent();
			 
		},300);
	}

	
	function updateContent()
	{
		console.log("updateContent");	
	}
	
	$rootScope.$on('$stateChangeSuccess',
			function(event, toState, toParams, fromState, fromParams) {
				 $state.current = toState;
				 console.log("state change:"+JSON.stringify(toParams));
				 
				 pageNameField = toParams.page;	 
				 init();
			}
	)
}]);

