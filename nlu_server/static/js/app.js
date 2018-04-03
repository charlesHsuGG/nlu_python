'use strict';
 
var mainApp = angular.module('mainApp',[
	
    //import library
    "ui.router",
    "ui.router.util",
    //util library
    'app.services',
    'datatables',
    'datatables.bootstrap',
    //custom library
    "mercue.services",
    "angularModalService",
    "ngFileUpload",
    "vcRecaptcha",
    //page controllers   
    "app.mainctrl",
    "app.aientityctrl",
    "app.aiintenteditctrl",
    "app.navctrl",
    "app.aislotaddmodalctrl",
    "app.aiintentlistctrl",
 
]);
 
 
mainApp.config(function($stateProvider, $urlRouterProvider){
   
   console.log('app start2');
   $urlRouterProvider.otherwise("ai_entity/");
   $stateProvider    
       .state('page', {
           url: '/:page/',
           resolve: {
               deps: ['scriptLoader', function(scriptLoader){
                   return scriptLoader;
               }]
           },
           templateProvider: function ($http, $stateParams, scriptLoader) {
               console.log("page name:"+$stateParams.page);
               return $http.get('/static/views/'+$stateParams.page+'.html')
                   .then(function(response) {
                       console.log("load")
                       return scriptLoader.loadScriptTagsFromData(response.data);
                   })
                   .then(function(responseData){
                       return responseData;
                   });
           }
       });
   
   
});