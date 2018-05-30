'use strict';
var appControllers = angular.module('app.navbarctrl', []);

appControllers.controller('navBarCtrl',
			['$scope', '$http', '$window', 'MercueRequests' ,
			 function ($scope, $http, $window, MercueRequests){
				
	$scope.adminName = "";
	
	var adminData;
	console.log("nav ctrl...");
	
	init();
	
	
	function init()
	{
		
	}
	
	$scope.$on('navbar_update', function(e, passAdminData) {
		// console.log("nav bar receive:"+passAdminData);
		 //adminData = JSON.parse(passAdminData);
		 $scope.adminName = sessionStorage.getItem("adminName");
		 
		 try { $scope.$apply(); }
		 catch(err){ }
	});
	
	$scope.onNavResetPasswordClick = function()
	{    	
		$scope.modalNavFormaerPassword == ""
    	$scope.modalNavResetPassword = "";
		$scope.modalNavResetRePassword = "";
		
		setTimeout(function(){
			$('#navResetPwd_modal').modal({
				  keyboard: false,
				  backdrop: false 
			});
			$('#navResetPwd_modal').modal('show');
		},300);
	}
	
	$scope.onNavResetPWDAcceptClick = function()
    {
    	console.log("onNavResetPWDAcceptClick");
//    	console.log("reset password:"+$scope.modalResetPassword);
//    	console.log("reset rePassword:"+$scope.modalResetRePassword);
    	
    	if(	$scope.modalNavFormaerPassword == "" || 
    		$scope.modalNavResetPassword == "" || 
    		$scope.modalNavResetRePassword == "")
    	{
    		alert("密碼欄位不能為空!");
    		return ;
    	}
    	else if($scope.modalNavResetPassword != $scope.modalNavResetRePassword)
    	{
    		alert("密碼與確認密碼不相符!");
    		return ;
    	}
    	else
    	{      	        	
        	var sendData = {};
        	sendData.token = sessionStorage.getItem("adminToken");
        	sendData.former_password = $scope.modalNavFormaerPassword;
        	sendData.new_password = $scope.modalNavResetRePassword;
        	
    		MercueRequests.cueRequest(
			    $scope.navResetPwdSuccess,
			    $scope.navResetPwdFail,
			    "./udpatepassword"
			    ,sendData); 
    		
    		
    	}
    }
    
    $scope.onNavResetPWDCanceltClick = function()
    {
    	console.log("onResetPWDCanceltClick");
    	$('#navResetPwd_modal').modal('hide');	
    }
    
	$scope.navResetPwdSuccess = function(data, status, headers, config)
	{
		alert(data.message);
		if(data.code == 1)
		{
			$('#navResetPwd_modal').modal('hide');
		}	
	}
	
	$scope.navResetPwdFail = function(data, status, headers, config)
	{
		alert("check error");
	}
	
	$scope.logoutSuccessFunc = function(data, status, headers, config) {
		console.log("user logout");
		if(data.code == 1)
		{
			sessionStorage.setItem("tokenCookie","");
			window.location.href = './login';
		}else if(data.code == -6)
		{
			alert("logout fail..." + data.message);
			location.reload();
		}else
		{
			alert("logout fail..." + data.message);
		}	
		
	};
	$scope.logoutFailFunc = function(data, status, headers, config) { 
		alert(data.msg);
	}
	$scope.logout = function(){
		console.log("logout");
		if(confirm("確認是否登出?"))
		{
			var sendData = {};
			sendData.token = sessionStorage.getItem("adminToken");
			MercueRequests.userLogout($scope.logoutSuccessFunc, $scope.logoutFailFunc, sendData);
		}
	}
	

}]);

